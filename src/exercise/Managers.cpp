/* _____________________________________________________________________ */
//! \file Managers.cpp

//! \brief Management of the operators

/* _____________________________________________________________________ */

#include "Managers.hpp"
#include "Operators.hpp"

using ExecSpace = Kokkos::DefaultExecutionSpace;
using MemorySpace = ExecSpace::memory_space;

namespace managers {

void initialize(const Params &params, ElectroMagn &em,
                std::vector<Particles> &particles) {

  ExecSpace execSpace{};
  const auto n_cells = params.nx_cells*params.ny_cells*params.nz_cells;
  for (std::size_t is = 0; is < particles.size(); ++is) {
    particles[is].boxVal = Kokkos::View<std::size_t *, MemorySpace>(
      Kokkos::view_alloc(execSpace, Kokkos::WithoutInitializing), particles[is].size());
    particles[is].boxOff = Kokkos::View<std::size_t *, MemorySpace>(
      Kokkos::view_alloc(execSpace, Kokkos::WithoutInitializing), n_cells+1);
    particles[is].tempA = Kokkos::View<std::size_t *, MemorySpace>(
      Kokkos::view_alloc(execSpace, Kokkos::WithoutInitializing), n_cells);
  }  

  // Momentum correction (to respect the leap frog scheme)
  if (params.momentum_correction) {

    std::cout << " > Apply momentum correction "
              << "\n"
              << std::endl;            

    // em.sync(minipic::device, minipic::host);
    // for (std::size_t is = 0; is < particles.size(); ++is) {
    //   particles[is].sync(minipic::device, minipic::host);
    // }

    operators::interpolate(em, particles);
    operators::push_momentum(particles, -0.5 * params.dt);

    // em.sync(minipic::host, minipic::device);
    // for (std::size_t is = 0; is < particles.size(); ++is) {
    //   particles[is].sync(minipic::host, minipic::device);
    // }
  }
}

void iterate(const Params &params, ElectroMagn &em,
             std::vector<Particles> &particles, int it) {

  ExecSpace execSpace{};
  Kokkos::Profiling::pushRegion("Cost Box A");

  const auto nx = params.nx_cells;
  const auto ny = params.ny_cells;
  const auto nz = params.nz_cells;

  const auto ncells = nx * ny * nz;

  const auto inv_dx = params.inv_dx;
  const auto inv_dy = params.inv_dy;
  const auto inv_dz = params.inv_dz;

  std::vector<ExecSpace> streams;

  for (std::size_t is = 0; is < particles.size(); is++) {

  ExecSpace ep;
  streams.push_back(ep);
  const std::size_t n_particles = particles[is].size();
  Kokkos::deep_copy(particles[is].boxOff, 0);
  Kokkos::deep_copy(particles[is].tempA, 0);
  Kokkos::View<std::size_t*, Kokkos::MemoryTraits<Kokkos::Atomic>> boxOffA(particles[is].boxOff);
  Kokkos::View<std::size_t*, Kokkos::MemoryTraits<Kokkos::Atomic>> tempA(particles[is].tempA);

  auto boxV = particles[is].boxVal;

  auto x = particles[is].x_m;
  auto y = particles[is].y_m;
  auto z = particles[is].z_m;

  Kokkos::parallel_for(
        "interpolate: for each particle in species",
        Kokkos::RangePolicy<ExecSpace>(streams[is], 0, n_particles),
        KOKKOS_LAMBDA(const int part) {
          // Calculate normalized positions
          const double ixn = x(part) * inv_dx;
          const double iyn = y(part) * inv_dy;
          const double izn = z(part) * inv_dz;

          // Compute indexes in global primal grid
          const unsigned int ixp = Kokkos::floor(ixn);
          const unsigned int iyp = Kokkos::floor(iyn);
          const unsigned int izp = Kokkos::floor(izn);
          const unsigned int boxglobIdx = ixp + nx * (iyp +  ny * izp);
          boxOffA(boxglobIdx + 1)++;
        }
      );
  Kokkos::parallel_for(
        "interpolate: for each particle in species",
        Kokkos::RangePolicy<ExecSpace>(streams[is], 0, n_particles),
        KOKKOS_LAMBDA(const int part) {
          // Calculate normalized positions
          const double ixn = x(part) * inv_dx;
          const double iyn = y(part) * inv_dy;
          const double izn = z(part) * inv_dz;

          // Compute indexes in global primal grid
          const unsigned int ixp = Kokkos::floor(ixn);
          const unsigned int iyp = Kokkos::floor(iyn);
          const unsigned int izp = Kokkos::floor(izn);
          const unsigned int boxglobIdx = ixp + nx * (iyp +  ny * izp);
          tempA(boxglobIdx)++;
          const unsigned int offset = boxOffA(boxglobIdx);
          boxV(offset+tempA(boxglobIdx)) = boxglobIdx;
        }
      );
  } // Species loop
  Kokkos::fence();
  Kokkos::Profiling::popRegion();

  if (params.current_projection || params.n_particles > 0) {

    DEBUG("  -> start reset current");

    em.reset_currents(minipic::device);

    DEBUG("  -> stop reset current");
  }

  // em.sync(minipic::device, minipic::host);
  // for (std::size_t is = 0; is < particles.size(); ++is) {
  //   particles[is].sync(minipic::device, minipic::host);
  // }

  // Interpolate from global field to particles
  DEBUG("  -> start interpolate ");

  operators::interpolate(em, particles);

  DEBUG("  -> stop interpolate");

  // Push all particles
  DEBUG("  -> start push ");

  operators::push(particles, params.dt);

  DEBUG("  -> stop push");

  // em.sync(minipic::host, minipic::device);
  // for (std::size_t is = 0; is < particles.size(); ++is) {
  //   particles[is].sync(minipic::host, minipic::device);
  // }

  // Do boundary conditions on global domain
  DEBUG("  -> Patch 0: start pushBC");

  operators::pushBC(params, particles);

  DEBUG("  -> stop pushBC");

#if defined(MINI_MINIPIC_DEBUG)
  // check particles
  for (std::size_t is = 0; is < particles.size(); ++is) {
    particles[is].check(inf_m[0], sup_m[0], inf_m[1], sup_m[1], inf_m[2],
                        sup_m[2]);
  }
#endif

  // Projection in local field
  if (params.current_projection) {

    // for (std::size_t is = 0; is < particles.size(); ++is) {
    //   particles[is].sync(minipic::device, minipic::host);
    // }

    // Projection directly in the global grid
    DEBUG("  ->  start projection");

    operators::project(params, em, particles);

    DEBUG("  ->  stop projection");

    // for (std::size_t is = 0; is < particles.size(); ++is) {
    //   particles[is].sync(minipic::host, minipic::device);
    // }
  }

  // __________________________________________________________________
  // Sum all species contribution in the local and global current grids

  if (params.current_projection || params.n_particles > 0) {

    // em.sync(minipic::host, minipic::device);
    // for (std::size_t is = 0; is < particles.size(); ++is) {
    //   particles[is].sync(minipic::host, minipic::device);
    // }

    // Perform the boundary conditions for current
    DEBUG("  -> start current BC")

    operators::currentBC(params, em);

    DEBUG("  -> stop current BC")

  } // end if current projection

  // __________________________________________________________________
  // Maxwell solver

  if (params.maxwell_solver) {

    // em.sync(minipic::device, minipic::host);

    // Generate a laser field with an antenna
    for (std::size_t iantenna = 0; iantenna < params.antenna_profiles_m.size();
         iantenna++) {
      operators::antenna(params, em, params.antenna_profiles_m[iantenna],
                         params.antenna_positions_m[iantenna], it * params.dt);
    }

    // Solve the Maxwell equation
    DEBUG("  -> start solve Maxwell")

    operators::solve_maxwell(params, em);

    DEBUG("  -> stop solve Maxwell")

    // em.sync(minipic::host, minipic::device);

    // Boundary conditions on EM fields
    DEBUG("  -> start solve BC")

    operators::solveBC(params, em);

    DEBUG("  -> end solve BC")

  } // end test params.maxwell_solver
}

} // namespace managers
