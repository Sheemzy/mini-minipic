"""Validation script for the `default` setup."""

import os

import numpy as np

from libminipic import ci as minipic_ci
from libminipic import diag as minipic_diag
from libminipic.exceptions import MissingFileMiniPICError
from libminipic.validate import THRESHOLD


def validate(evaluate=True, threshold=THRESHOLD):

    # ______________________________________________________________________
    # Check output files are created

    # list of output files
    output_file_list = []

    # Add *.vtk files
    for field in [
        "Ex",
        "Ey",
        "Ez",
        "Bx",
        "By",
        "Bz",
        "diag_x_y_z_d_s00",
        "diag_x_y_z_d_s01",
        "diag_px_py_pz_d_s00",
        "diag_px_py_pz_d_s01",
    ]:
        for it in range(0, 200, 50):
            file = "{}_{:03d}.vtk".format(field, it)
            output_file_list.append(file)

    # Add *.bin files
    for field in ["cloud_s00", "cloud_s01", "diag_w_gamma_s00", "diag_w_gamma_s01"]:
        for it in range(0, 200, 50):
            file = "{}_{:03d}.bin".format(field, it)
            output_file_list.append(file)

    # Add scalars
    output_file_list.append("fields.txt")
    output_file_list.append("species_00.txt")
    output_file_list.append("species_01.txt")

    # Check that all output files exist
    for file in output_file_list:
        if not (os.path.exists("diags/" + file)):
            raise MissingFileMiniPICError(f"File {file} not generated")

    # ______________________________________________________________________
    # Check scalars

    print(" > Checking scalars")

    # Check initial scalar for species

    reference_data = [
        [0, 16777216, 1.499952252449287e-07],
        [0, 16777216, 1.499979783958965e-07],
    ]

    for ispecies in range(2):

        with open("diags/species_{:02d}.txt".format(ispecies), "r") as f:
            lines = f.readlines()

            last_line = lines[1].split(" ")

            iteration = int(last_line[0])
            particles = float(last_line[1])
            energy = float(last_line[2])

        print(
            "    - Initial scalar for species {}: {}, {}, {}".format(
                ispecies, iteration, particles, energy
            )
        )

        if evaluate:

            minipic_ci.evaluate(
                iteration,
                reference_data[ispecies][0],
                reference_data[ispecies][0],
                "==",
                "First iteration in species_{}.txt is not correct".format(ispecies),
            )

            minipic_ci.evaluate(
                particles,
                reference_data[ispecies][1],
                reference_data[ispecies][1],
                "==",
                "Number of particles in species_{:02d}.txt is not correct".format(
                    ispecies
                ),
            )

            minipic_ci.evaluate(
                energy,
                reference_data[ispecies][2],
                threshold,
                "relative",
                "Kinetic energy in species_{:02d}.txt is not correct".format(ispecies),
            )

    # Check final scalar for species

    reference_data = [
        [200, 16777216, 1.499958286027602e-07],
        [200, 16777216, 1.499977885488740e-07],
    ]

    for ispecies in range(2):

        with open("diags/species_{:02d}.txt".format(ispecies), "r") as f:
            lines = f.readlines()

            last_line = lines[-1].split(" ")

            iteration = int(last_line[0])
            particles = float(last_line[1])
            energy = float(last_line[2])

        print(
            "    - Final scalar for species {}: {}, {}, {}".format(
                ispecies, iteration, particles, energy
            )
        )

        if evaluate:

            minipic_ci.evaluate(
                iteration,
                reference_data[ispecies][0],
                reference_data[ispecies][0],
                "==",
                "Last iteration in species_{}.txt is not correct".format(ispecies),
            )

            minipic_ci.evaluate(
                particles,
                reference_data[ispecies][1],
                reference_data[ispecies][1],
                "==",
                "Number of particles in species_{:02d}.txt is not correct".format(
                    ispecies
                ),
            )

            minipic_ci.evaluate(
                energy,
                reference_data[ispecies][2],
                threshold,
                "relative",
                "Kinetic energy in species_{:02d}.txt is not correct".format(ispecies),
            )

    # Check final scalar values for fields

    reference_data = [
        200,
        2.661456444853063e-17,
        2.494703374240188e-17,
        2.660089866321201e-17,
        4.000475322163436e-18,
        2.515068854661692e-18,
        1.968836182669220e-18,
    ]

    with open("diags/fields.txt", "r") as f:
        lines = f.readlines()

        last_line = lines[-1].split(" ")

        iteration = int(last_line[0])
        Ex = float(last_line[1])
        Ey = float(last_line[2])
        Ez = float(last_line[3])
        Bx = float(last_line[4])
        By = float(last_line[5])
        Bz = float(last_line[6])

    print(
        "    - Field values at final iteration {}: \n {}, {}, {}, {}, {}, {}".format(
            iteration, Ex, Ey, Ez, Bx, By, Bz
        )
    )

    if evaluate:

        minipic_ci.evaluate(
            iteration,
            reference_data[0],
            reference_data[0],
            "==",
            "Last iteration in fields.txt is not correct",
        )

        # We check that the fields do not explode (numerical instability)
        minipic_ci.evaluate(
            Ex,
            reference_data[1],
            threshold,
            "relative",
            "Ex value at it {} in fields.txt is not correct".format(iteration),
        )
        minipic_ci.evaluate(
            Ey,
            reference_data[2],
            threshold,
            "relative",
            "Ey value at it {} in fields.txt is not correct".format(iteration),
        )
        minipic_ci.evaluate(
            Ez,
            reference_data[3],
            threshold,
            "relative",
            "Ez value at it {} in fields.txt is not correct".format(iteration),
        )
        minipic_ci.evaluate(
            Bx,
            reference_data[4],
            threshold,
            "relative",
            "Bx value at it {} in fields.txt is not correct".format(iteration),
        )
        minipic_ci.evaluate(
            By,
            reference_data[5],
            threshold,
            "relative",
            "By value at it {} in fields.txt is not correct".format(iteration),
        )
        minipic_ci.evaluate(
            Bz,
            reference_data[6],
            threshold,
            "relative",
            "Bz value at it {} in fields.txt is not correct".format(iteration),
        )

    # ______________________________________________________________________
    # Check gamma spectrums

    reference_sum_data = [
        [
            1.0150597401850308e-05,
            1.0150597529179078e-05,
            1.0150598273792077e-05,
            1.0150598116635371e-05,
            1.0150597873414933e-05,
            1.0150435409492973e-05,
        ],
        [
            1.0001580020106392e-05,
            1.0001580020341790e-05,
            1.0001580020415498e-05,
            1.0001580020473257e-05,
            1.0001580020140429e-05,
            1.0001575882811223e-05,
        ],
    ]

    print(" > Checking gamma spectrums")

    for ispecies in range(2):

        new_data = []

        for i, it in enumerate(range(0, 200, 50)):

            file = "diag_w_gamma_s{:02d}_{:03d}.bin".format(ispecies, it)

            x_axis_name, x_min, x_max, x_data, data_name, data = (
                minipic_diag.read_1d_diag("diags/" + file)
            )

            new_data.append(np.sum(np.abs(data * x_data)))

        print("    - For species {}: {}".format(ispecies, new_data))

        if evaluate:
            for i, it in enumerate(range(0, 200, 50)):
                minipic_ci.evaluate(
                    new_data[i],
                    reference_sum_data[ispecies][i],
                    1e-13,
                    "relative",
                    "Gamma spectrum for species {} at iteration {} not similar".format(
                        ispecies, it
                    ),
                )

    # ______________________________________________________________________
    # Check initial cloud file (particle initialization)

    reference_data = [
        [8388609.273422275, 8388608.223742893, 8388607.295782689, 1345277.1638367819, 1345287.6357619246, 1345276.2842692742],
        [8388609.273422275, 8388608.223742893, 8388607.295782689, 31239.48867078933, 31240.339148407398, 31239.83530535533],
    ]

    print(" > Checking initial cloud file")

    for ispecies in range(2):

        file = "cloud_s{:02}_000.bin".format(ispecies)

        particle_number, id, w, x, y, z, px, py, pz = minipic_diag.read_particle_cloud(
            "diags/" + file
        )

        x_sum = np.sum(np.abs(x))
        y_sum = np.sum(np.abs(y))
        z_sum = np.sum(np.abs(z))

        px_sum = np.sum(np.abs(px))
        py_sum = np.sum(np.abs(py))
        pz_sum = np.sum(np.abs(pz))

        print(
            "   - For Species {}: {}, {}, {}, {}, {}, {}".format(
                ispecies, x_sum, y_sum, z_sum, px_sum, py_sum, pz_sum
            )
        )

        if evaluate:
            minipic_ci.evaluate(
                x_sum,
                reference_data[ispecies][0],
                threshold,
                "relative",
                "Sum over x positions not similar",
            )
            minipic_ci.evaluate(
                y_sum,
                reference_data[ispecies][1],
                threshold,
                "relative",
                "Sum over y positions not similar",
            )
            minipic_ci.evaluate(
                z_sum,
                reference_data[ispecies][2],
                threshold,
                "relative",
                "Sum over z positions not similar",
            )

            minipic_ci.evaluate(
                px_sum,
                reference_data[ispecies][3],
                threshold,
                "relative",
                "Sum over px not similar",
            )
            minipic_ci.evaluate(
                py_sum,
                reference_data[ispecies][4],
                threshold,
                "relative",
                "Sum over py not similar",
            )
            minipic_ci.evaluate(
                pz_sum,
                reference_data[ispecies][5],
                threshold,
                "relative",
                "Sum over pz not similar",
            )

    # ______________________________________________________________________
    # Check final cloud file (particle initialization)

    reference_data = [
        [8388690.182898799, 8388869.37299231, 8388436.356830236, 1345284.9369570762 , 1345278.656959498, 1345277.0503750877],
        [8387715.472760824, 8387134.949183166, 8388681.588967344, 31239.5389402392, 31240.227334379924, 31239.731722495122],
    ]

    print(" > Checking final cloud file")

    for ispecies in range(2):

        file = "cloud_s{:02}_200.bin".format(ispecies)

        particle_number, id, w, x, y, z, px, py, pz = minipic_diag.read_particle_cloud(
            "diags/" + file
        )

        x_sum = np.sum(np.abs(x))
        y_sum = np.sum(np.abs(y))
        z_sum = np.sum(np.abs(z))

        px_sum = np.sum(np.abs(px))
        py_sum = np.sum(np.abs(py))
        pz_sum = np.sum(np.abs(pz))

        print(
            "    - For Species {}: {}, {}, {}, {}, {}, {}".format(
                ispecies, x_sum, y_sum, z_sum, px_sum, py_sum, pz_sum
            )
        )

        if evaluate:
            minipic_ci.evaluate(
                x_sum,
                reference_data[ispecies][0],
                threshold,
                "relative",
                "Sum over x positions not similar",
            )
            minipic_ci.evaluate(
                y_sum,
                reference_data[ispecies][1],
                threshold,
                "relative",
                "Sum over y positions not similar",
            )
            minipic_ci.evaluate(
                z_sum,
                reference_data[ispecies][2],
                threshold,
                "relative",
                "Sum over z positions not similar",
            )

            minipic_ci.evaluate(
                px_sum,
                reference_data[ispecies][3],
                threshold,
                "relative",
                "Sum over px not similar",
            )
            minipic_ci.evaluate(
                py_sum,
                reference_data[ispecies][4],
                threshold,
                "relative",
                "Sum over py not similar",
            )
            minipic_ci.evaluate(
                pz_sum,
                reference_data[ispecies][5],
                threshold,
                "relative",
                "Sum over pz not similar",
            )
