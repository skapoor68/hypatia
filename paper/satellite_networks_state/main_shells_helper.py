# The MIT License (MIT)
#
# Copyright (c) 2020 ETH Zurich
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import sys
sys.path.append("../../satgenpy")
import satgen
import os


class MainShellsHelper:

    def __init__(
            self,
            BASE_NAME,
            NICE_NAME,
            NUM_SHELLS,
            ECCENTRICITY,
            ARG_OF_PERIGEE_DEGREE,
            PHASE_DIFF,
            MEAN_MOTION_REV_PER_DAY,
            ALTITUDE_M,
            MAX_GSL_LENGTH_M,
            MAX_ISL_LENGTH_M,
            NUM_ORBS,
            NUM_SATS_PER_ORB,
            INCLINATION_DEGREE,
    ):
        self.BASE_NAME = BASE_NAME
        self.NICE_NAME = NICE_NAME
        self.NUM_SHELLS = NUM_SHELLS
        self.ECCENTRICITY = ECCENTRICITY
        self.ARG_OF_PERIGEE_DEGREE = ARG_OF_PERIGEE_DEGREE
        self.PHASE_DIFF = PHASE_DIFF
        self.MEAN_MOTION_REV_PER_DAY = MEAN_MOTION_REV_PER_DAY
        self.ALTITUDE_M = ALTITUDE_M
        self.MAX_GSL_LENGTH_M = MAX_GSL_LENGTH_M
        self.MAX_ISL_LENGTH_M = MAX_ISL_LENGTH_M
        self.NUM_ORBS = NUM_ORBS
        self.NUM_SATS_PER_ORB = NUM_SATS_PER_ORB
        self.INCLINATION_DEGREE = INCLINATION_DEGREE

    def calculate(
            self,
            output_generated_data_dir,  # gen_data
            duration_s,
            time_step_ms,
            isl_selection,            # isls_{none, plus_grid}
            gs_selection,             # ground_stations_{top_100, paris_moscow_grid}
            dynamic_state_algorithm,  # algorithm_{free_one_only_{gs_relays,_over_isls}, paired_many_only_over_isls}
            num_threads
    ):

        # Add base name to setting
        name = self.BASE_NAME + "_" + str(self.NUM_SHELLS) + "shells_" + isl_selection + "_" + gs_selection + "_" + dynamic_state_algorithm

        # Create output directories
        if not os.path.isdir(output_generated_data_dir):
            os.makedirs(output_generated_data_dir, exist_ok=True)
        if not os.path.isdir(output_generated_data_dir + "/" + name):
            os.makedirs(output_generated_data_dir + "/" + name, exist_ok=True)

        # Ground stations
        print("Generating ground stations...")
        if gs_selection == "ground_stations_top_100":
            satgen.extend_ground_stations(
                "input_data/ground_stations_cities_sorted_by_estimated_2025_pop_top_100.basic.txt",
                output_generated_data_dir + "/" + name + "/ground_stations.txt",
                100
            )
        elif gs_selection == "ground_stations_top_1000":
            satgen.extend_ground_stations(
                "input_data/ground_stations_cities_sorted_by_estimated_2025_pop_top_1000.basic.txt",
                output_generated_data_dir + "/" + name + "/ground_stations.txt"
            )
        elif gs_selection == "ground_stations_paris_moscow_grid":
            satgen.extend_ground_stations(
                "input_data/ground_stations_paris_moscow_grid.basic.txt",
                output_generated_data_dir + "/" + name + "/ground_stations.txt"
            )
        elif gs_selection == "ground_stations_newyork_london":
            satgen.extend_ground_stations(
                "input_data/ground_stations_newyork_london.basic.txt",
                output_generated_data_dir + "/" + name + "/ground_stations.txt"
            )
        else:
            raise ValueError("Unknown ground station selection: " + gs_selection)

        # TLEs
        print("Generating TLEs...")
        satgen.generate_tles_from_scratch_manual_shells(
            output_generated_data_dir + "/" + name + "/tles.txt",
            self.NICE_NAME + "_" + str(self.NUM_SHELLS) + "shells",
            self.NUM_SHELLS,
            self.NUM_ORBS,
            self.NUM_SATS_PER_ORB,
            self.PHASE_DIFF,
            self.INCLINATION_DEGREE,
            self.ECCENTRICITY,
            self.ARG_OF_PERIGEE_DEGREE,
            self.MEAN_MOTION_REV_PER_DAY
        )

        # ISLs
        print("Generating ISLs...")
        if isl_selection == "isls_plus_grid":
            satgen.generate_plus_grid_isls_shells(
                output_generated_data_dir + "/" + name + "/isls.txt",
                self.NUM_SHELLS,
                self.NUM_ORBS,
                self.NUM_SATS_PER_ORB,
                isl_shift=0,
                idx_offset=0
            )
        elif isl_selection == "isls_none":
            satgen.generate_empty_isls(
                output_generated_data_dir + "/" + name + "/isls.txt"
            )
        else:
            raise ValueError("Unknown ISL selection: " + isl_selection)

        # Description
        print("Generating description...")
        satgen.generate_description_shells(
            output_generated_data_dir + "/" + name + "/description.txt",
            self.NUM_ORBS,
            self.NUM_SATS_PER_ORB,
            self.MAX_GSL_LENGTH_M,
            self.MAX_ISL_LENGTH_M
        )

        # GSL interfaces
        ground_stations = satgen.read_ground_stations_extended(
            output_generated_data_dir + "/" + name + "/ground_stations.txt"
        )

    def calculate_shells_failure(
            self,
            output_generated_data_dir,   # gen_data
            duration_s,
            time_step_ms,
            isl_selection,            # isls_{none, plus_grid}
            gs_selection,             # ground_stations_{top_100, paris_moscow_grid, starlink}
            num_gateways,
            ut_selection,
            num_user_terminals,
            dynamic_state_algorithm,  # algorithm_{free_one_only_{gs_relays,_over_isls}, paired_many_only_over_isls}
            num_threads,
            failure_id,
            num_shells
    ):

        # Add base name to setting
        name = "starlink_current_" + str(num_shells) + "_shells_" + isl_selection + "_" + gs_selection + "_" + dynamic_state_algorithm + "_" + ut_selection + "_failure_" + str(failure_id)

        # Create output directories
        if not os.path.isdir(output_generated_data_dir):
            os.makedirs(output_generated_data_dir, exist_ok=True)
        if not os.path.isdir(output_generated_data_dir + "/" + name):
            os.makedirs(output_generated_data_dir + "/" + name, exist_ok=True)

        graph_dir = "%s/%s/%dms" % (
            output_generated_data_dir, name, time_step_ms
        )
        if not os.path.isdir(graph_dir):
            os.makedirs(graph_dir, exist_ok=True)

        # print(graph_dir)

        # Ground stations
        print("Generating ground stations...")
        if gs_selection == "ground_stations_top_100":
            satgen.extend_ground_stations(
                "input_data/ground_stations_cities_sorted_by_estimated_2025_pop_top_100.basic.txt",
                output_generated_data_dir + "/" + name + "/ground_stations.txt",
                num_gateways
            )
        elif gs_selection == "ground_stations_top_1000":
            satgen.extend_ground_stations(
                "input_data/ground_stations_cities_sorted_by_estimated_2025_pop_top_1000.basic.txt",
                output_generated_data_dir + "/" + name + "/ground_stations.txt",
                num_gateways
            )
        elif gs_selection == "ground_stations_paris_moscow_grid":
            satgen.extend_ground_stations(
                "input_data/ground_stations_paris_moscow_grid.basic.txt",
                output_generated_data_dir + "/" + name + "/ground_stations.txt",
                num_gateways
            )
        elif gs_selection == "ground_stations_atlanta":
            satgen.extend_ground_stations(
                "input_data/ground_stations_atlanta.basic.txt",
                output_generated_data_dir + "/" + name + "/ground_stations.txt",
                num_gateways
            )
        elif gs_selection == "ground_stations_starlink":
            satgen.extend_ground_stations(
                "input_data/ground_stations_starlink.basic.txt",
                output_generated_data_dir + "/" + name + "/ground_stations.txt",
                num_gateways
            )
        elif gs_selection == "ground_stations_sydney":
            satgen.extend_ground_stations(
                "input_data/ground_stations_sydney.basic.txt",
                output_generated_data_dir + "/" + name + "/ground_stations.txt",
                num_gateways
            )
        elif gs_selection == "ground_stations_fiji":
            satgen.extend_ground_stations(
                "input_data/ground_stations_fiji.basic.txt",
                output_generated_data_dir + "/" + name + "/ground_stations.txt",
                num_gateways
            )
        else:
            raise ValueError("Unknown ground station selection: " + gs_selection)

        # User Terminals
        print("Generating user terminals...")
        if ut_selection == "user_terminals_top_100":
            satgen.extend_user_terminals(
                    "input_data/user_terminals_top_100.txt",
                    output_generated_data_dir + "/" + name + "/user_terminals.txt",
                    num_user_terminals
            )
        elif ut_selection == "user_terminals_top_1000":
            satgen.extend_user_terminals(
                    "input_data/user_terminals_top_1000.txt",
                    output_generated_data_dir + "/" + name + "/user_terminals.txt",
                    num_user_terminals
            )
        elif ut_selection == "user_terminals_atlanta":
            satgen.extend_user_terminals(
                    "input_data/user_terminals_atlanta.basic.txt",
                    output_generated_data_dir + "/" + name + "/user_terminals.txt",
                    num_user_terminals
        )
        elif ut_selection == "user_terminals_fiji":
            satgen.extend_user_terminals(
                    "input_data/user_terminals_fiji.basic.txt",
                    output_generated_data_dir + "/" + name + "/user_terminals.txt",
                    num_user_terminals
        )
        # TLEs
        print("Generating TLEs...")
        satgen.generate_tles_from_scratch_manual_shells(
            output_generated_data_dir + "/" + name + "/tles.txt",
            self.NICE_NAME + "_" + str(self.NUM_SHELLS) + "shells",
            self.NUM_SHELLS,
            self.NUM_ORBS,
            self.NUM_SATS_PER_ORB,
            self.PHASE_DIFF,
            self.INCLINATION_DEGREE,
            self.ECCENTRICITY,
            self.ARG_OF_PERIGEE_DEGREE,
            self.MEAN_MOTION_REV_PER_DAY
        )

        # ISLs
        print("Generating ISLs...")
        if isl_selection == "isls_plus_grid":
            satgen.generate_plus_grid_isls_shells(
                output_generated_data_dir + "/" + name + "/isls.txt",
                self.NUM_SHELLS,
                self.NUM_ORBS,
                self.NUM_SATS_PER_ORB,
                isl_shift=0,
                idx_offset=0
            )
        elif isl_selection == "isls_none":
            satgen.generate_empty_isls(
                output_generated_data_dir + "/" + name + "/isls.txt"
            )
        else:
            raise ValueError("Unknown ISL selection: " + isl_selection)
        
        # Description
        print("Generating description...")
        satgen.generate_description_shells(
            output_generated_data_dir + "/" + name + "/description.txt",
            self.NUM_ORBS,
            self.NUM_SATS_PER_ORB,
            self.MAX_GSL_LENGTH_M,
            self.MAX_ISL_LENGTH_M
        )
        
