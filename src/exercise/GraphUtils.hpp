#pragma once

#include "Kokkos_Core.hpp"
#include "Kokkos_Graph.hpp"

namespace best_team_namespace {

/* Meyers Singleton pattern to manage the workgraph instance
 */
class GraphUtils {
public:
  using graph_t = Kokkos::Experimental::Graph<Kokkos::DefaultExecutionSpace>;

  static graph_t &get_graph();
  static int &get_it();

  GraphUtils() = delete;
  ~GraphUtils() = delete;
};

} // namespace best_team_namespace
