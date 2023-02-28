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

import exputil
import time

local_shell = exputil.LocalShell()
max_num_processes = 38

# Check that no screen is running
# if local_shell.count_screens() != 0:
#     print("There is a screen already running. "
#           "Please kill all screens before running this analysis script (killall screen).")
#     exit(1)

# Re-create data directory
# local_shell.remove_force_recursive("data")
# local_shell.make_full_dir("data")
# local_shell.make_full_dir("data/command_logs")

# Where to store all commands
commands_to_run = []

# Manual
print("Generating commands for manually selected endpoints pair (printing of routes and RTT over time)...")

# commands_to_run.append("cd ../../satgenpy; python -m satgen.post_analysis.main_print_all_routes_and_rtt "
#                        "../paper/satgenpy_analysis/all_paths ../paper/satellite_networks_state/gen_data/"
#                        "kuiper_630_isls_plus_grid_ground_stations_top_100_algorithm_free_one_only_over_isls "
#                        "1000 200 "
#                        "> ../paper/satgenpy_analysis/all_paths/command_logs/manual_kuiper_isls_1174_to_1229.log 2>&1")

# # Rio de Janeiro to St. Petersburg with only ISLs on Kuiper
# commands_to_run.append("cd ../../satgenpy; python -m satgen.post_analysis.main_print_routes_and_rtt "
#                        "../paper/satgenpy_analysis/old_data ../paper/satellite_networks_state/gen_data/"
#                        "kuiper_630_isls_plus_grid_ground_stations_top_100_algorithm_free_one_only_over_isls "
#                        "1000 200 1174 1229 "
#                        "> ../paper/satgenpy_analysis/old_data/command_logs/manual_kuiper_isls_1174_to_1229.log 2>&1")

# # Rio de Janeiro to St. Petersburg with only ISLs on Kuiper
# commands_to_run.append("cd ../../satgenpy; python -m satgen.post_analysis.main_print_modified_routes_and_rtt "
#                        "../paper/satgenpy_analysis/modified_data ../paper/satellite_networks_state/gen_data/"
#                        "kuiper_630_isls_plus_grid_ground_stations_top_100_algorithm_free_one_only_over_isls "
#                        "1000 200 1174 1229 "
#                        "> ../paper/satgenpy_analysis/modified_data/command_logs/manual_kuiper_isls_modified_1174_to_1229.log 2>&1")

# # Manila to Dalian with only ISLs on Kuiper
# commands_to_run.append("cd ../../satgenpy; python -m satgen.post_analysis.main_print_routes_and_rtt "
#                        "../paper/satgenpy_analysis/data ../paper/satellite_networks_state/gen_data/"
#                        "kuiper_630_isls_plus_grid_ground_stations_top_100_algorithm_free_one_only_over_isls "
#                        "100 200 1173 1241 "
#                        "> ../paper/satgenpy_analysis/data/command_logs/manual_kuiper_isls_1173_to_1241.log 2>&1")

# # Istanbul to Nairobi with only ISLs on Kuiper
# commands_to_run.append("cd ../../satgenpy; python -m satgen.post_analysis.main_print_routes_and_rtt "
#                        "../paper/satgenpy_analysis/data ../paper/satellite_networks_state/gen_data/"
#                        "kuiper_630_isls_plus_grid_ground_stations_top_100_algorithm_free_one_only_over_isls "
#                        "100 200 1170 1252 "
#                        "> ../paper/satgenpy_analysis/data/command_logs/manual_kuiper_isls_1170_to_1252.log 2>&1")

# # Paris to Moscow with only ISLs on Kuiper
# commands_to_run.append("cd ../../satgenpy; python -m satgen.post_analysis.main_print_routes_and_rtt "
#                        "../paper/satgenpy_analysis/data ../paper/satellite_networks_state/gen_data/"
#                        "kuiper_630_isls_plus_grid_ground_stations_top_100_algorithm_free_one_only_over_isls "
#                        "100 200 1180 1177 "
#                        "> ../paper/satgenpy_analysis/data/command_logs/manual_kuiper_isls_1180_to_1177.log 2>&1")
# commands_to_run.append("cd ../../satgenpy; python -m satgen.post_analysis.main_print_graphical_routes_and_rtt "
#                        "../paper/satgenpy_analysis/data ../paper/satellite_networks_state/gen_data/"
#                        "kuiper_630_isls_plus_grid_ground_stations_top_100_algorithm_free_one_only_over_isls "
#                        "100 200 1180 1177 "
#                        "> ../paper/satgenpy_analysis/data/command_logs/manual_graphical_kuiper_isls_1180_to_1177.log"
#                        " 2>&1")

# # Chicago (1193) to Zhengzhou (1243) with only ISLs on Kuiper
# commands_to_run.append("cd ../../satgenpy; python -m satgen.post_analysis.main_print_routes_and_rtt "
#                        "../paper/satgenpy_analysis/data ../paper/satellite_networks_state/gen_data/"
#                        "kuiper_630_isls_plus_grid_ground_stations_top_100_algorithm_free_one_only_over_isls "
#                        "100 200 1193 1243 "
#                        "> ../paper/satgenpy_analysis/data/command_logs/manual_kuiper_isls_1193_to_1243.log 2>&1")
# commands_to_run.append("cd ../../satgenpy; python -m satgen.post_analysis.main_print_graphical_routes_and_rtt "
#                        "../paper/satgenpy_analysis/data ../paper/satellite_networks_state/gen_data/"
#                        "kuiper_630_isls_plus_grid_ground_stations_top_100_algorithm_free_one_only_over_isls "
#                        "100 200 1193 1243 "
#                        "> ../paper/satgenpy_analysis/data/command_logs/manual_graphical_kuiper_isls_1193_to_1243.log"
#                        " 2>&1")

# # Paris to Moscow with only ground-station relays (added a grid to support this) on Kuiper
# commands_to_run.append("cd ../../satgenpy; python -m satgen.post_analysis.main_print_routes_and_rtt "
#                        "../paper/satgenpy_analysis/data ../paper/satellite_networks_state/gen_data/"
#                        "kuiper_630_isls_none_ground_stations_paris_moscow_grid_algorithm_free_one_only_gs_relays "
#                        "100 200 1156 1232 "
#                        "> ../paper/satgenpy_analysis/data/command_logs/manual_kuiper_isls_1156_to_1232.log 2>&1")

# commands_to_run.append("cd ../../satgenpy; python -m satgen.post_analysis.main_print_graphical_routes_and_rtt "
#                        "../paper/satgenpy_analysis/data ../paper/satellite_networks_state/gen_data/"
#                        "kuiper_630_isls_none_ground_stations_paris_moscow_grid_algorithm_free_one_only_gs_relays "
#                        "100 200 1156 1232 "
#                        "> ../paper/satgenpy_analysis/data/command_logs/"
#                        "manual_graphical_kuiper_gs_relay_1156_to_1232.log"
#                        " 2>&1")


# # Paris (1608) to Luanda (1650) with only ISLs on Starlink
# commands_to_run.append("cd ../../satgenpy; python -m satgen.post_analysis.main_print_routes_and_rtt "
#                        "../paper/satgenpy_analysis/data ../paper/satellite_networks_state/gen_data/"
#                        "starlink_550_isls_plus_grid_ground_stations_top_100_algorithm_free_one_only_over_isls "
#                        "100 200 1608 1650 "
#                        "> ../paper/satgenpy_analysis/data/command_logs/manual_starlink_isls_1608_to_1650.log 2>&1")
# commands_to_run.append("cd ../../satgenpy; python -m satgen.post_analysis.main_print_graphical_routes_and_rtt "
#                        "../paper/satgenpy_analysis/data ../paper/satellite_networks_state/gen_data/"
#                        "starlink_550_isls_plus_grid_ground_stations_top_100_algorithm_free_one_only_over_isls "
#                        "100 200 1608 1650 "
#                        "> ../paper/satgenpy_analysis/data/command_logs/manual_graphical_starlink_isls_1608_to_1650.log"
#                        " 2>&1")


# Constellation comparison
eight_threads = [[98,100]]
# eight_threads = [[3,4], [49,53], [53, 58], [58,65]]
# eight_threads = [[7,14], [21, 29], [29,38], [65,100]]
# eight_threads = [[0, 25], [25, 60], [60, 100] ]
sixteen_threads = [[0,40], [40,80], [80,120], [120,160], [160,200], [200,240], [240,280], [280,320], [320,360], [360,400],
                [400,440], [440,480], [480,520], [520,560], [560,600], [600,640], [640,680], [680,720], [720,760], [760,800],
                [800,840], [840,880], [880,920], [920,960], [960,1000], [1000,1040], [1040,1080], [1080,1120], [1120,1160], [1160,1200],
                [1200,1240], [1240,1280], [1280,1320], [1320,1360], [1360,1400], [1400,1440], [1440,1480], [1480,1520], [1520,1560], [1560,1600]]

seventeen_threads = [[0,3], [3,6], [6,9], [9,13], [13,17], [17,21], [21,26], [26,31], [31,36], [36,42], [42,48], [48,54], [54,61], [61,68], [68,75], [75,85], [85,100]]
# seventeen_threads = [[21,26], [26,31], [31,36], [36,42], [42,48], [48,54], [54,61], [61,68], [68,75], [75,85], [85,100]]
# tasks = [[i, i+3] for i in range(0,96,3)]
# tasks.append([96,98])
# tasks = [[i, i+50] for i in range(0,2100,50)]
# tasks.append([2100,2101])
# tasks = [[750,800]]
# seventeen_threads = [[98,100]]

seven_threads = [[0,7], [7,15], [15,24], [24,34], [34,46], [46,62],[62,98]]
five_threads = [[0,10], [10,21], [21,34], [34,52], [52,98]]
phases = [[i, i + 2] for i in range(0, 72, 2)]
phases = [[0,1], [12,13], [24,25], [36,37], [48,49], [60,61]]
# tasks = [[3,6], [12,15], [18,24], [30,36], [39,48],[51,54], [75,81]]
# tasks = [[1,2],[2,3],[48,50],[50,52],[52,54],[57,60],[60,63],[63,67],[67,71], [71,75], [75,80], [80,85], [90,92],[92,98]]
# tasks = [[2,3], [3,4], [1399,1400]]
# tasks = [[98,100]]

# for phase in phases:
#     commands_to_run.append("python find_best_phase.py %d %d > phase_expts/best_phase_lats_all_%d.txt" % (phase[0], phase[1], phase[0]))


for time_stamp in range(2, 200, 3):
    commands_to_run.append("python calculate_path_lengths_variations.py %d" % (time_stamp))

# # tasks.append([99,100])
# print("Generating commands for constellation comparison...")
# for satgenpy_generated_constellation in [
#     # "kuiper_630_isls_none_ground_stations_paris_moscow_grid_algorithm_free_one_only_gs_relays",
#     # "kuiper_630_isls_plus_grid_ground_stations_top_100_algorithm_free_one_only_over_isls"
#     # "starlink_550_isls_plus_grid_ground_stations_newyork_london_circular_algorithm_free_one_only_over_isls"
#     # "starlink_550_isls_plus_grid_ground_stations_newyork_london_circular_bigger_algorithm_free_one_only_over_isls"
#     # "starlink_550_isls_plus_grid_ground_stations_kyiv_algorithm_free_one_only_over_isls"
#     # "starlink_550_isls_plus_grid_ground_stations_darfur_algorithm_free_one_only_over_isls"
#     # "starlink_550_isls_plus_grid_ground_stations_newyork_london_1600_algorithm_free_one_only_over_isls"
#     # "starlink_550_isls_plus_grid_ground_stations_top_100_algorithm_free_one_only_over_isls"
#     "starlink_550_half_phase_isls_plus_grid_ground_stations_top_100_algorithm_free_one_only_over_isls",
#     # "telesat_1015_isls_plus_grid_ground_stations_top_100_algorithm_free_one_only_over_isls"
#     # "starlink_current_5shells_isls_plus_grid_ground_stations_top_100_algorithm_free_one_only_over_isls",
#     # "starlink_older_5shells_isls_plus_grid_ground_stations_top_100_algorithm_free_one_only_over_isls",
#     # "starlink_550_72_66_isls_plus_grid_ground_stations_top_100_algorithm_free_one_only_over_isls",
#     # "starlink_different_8shells_isls_plus_grid_ground_stations_top_100_algorithm_free_one_only_over_isls", #run this later from 600
#     # "starlink_different_4shells_isls_plus_grid_ground_stations_top_100_algorithm_free_one_only_over_isls",
#     # "starlink_550_isls_plus_grid_ground_stations_world_grid_paper_algorithm_free_one_only_over_isls"
#     # "starlink_different_2shells_isls_plus_grid_ground_stations_top_100_algorithm_free_one_only_over_isls",
#     # "starlink_8shells_isls_plus_grid_ground_stations_top_100_algorithm_free_one_only_over_isls",
#     # "starlink_4shells_isls_plus_grid_ground_stations_top_100_algorithm_free_one_only_over_isls",
#     # "starlink_2shells_isls_plus_grid_ground_stations_top_100_algorithm_free_one_only_over_isls"
# ]:
#     for duration_s in [6000]:
#         list_update_interval_ms = [1000]

#         for update_interval_ms in list_update_interval_ms:
#             for thread in seventeen_threads:
#                 start = thread[0]
#                 end = thread[1]
#                 commands_to_run.append(
#                     "cd ../../satgenpy; "
#                     # "python -m satgen.post_analysis.main_print_newyork_london_routes "
#                     # "python -m satgen.post_analysis.main_print_v2_routes_and_rtt "
#                     "python -m satgen.post_analysis.main_print_all_routes_and_rtt "
#                     # "python -m satgen.post_analysis.main_print_path_life "
#                     # "python -m satgen.post_analysis.main_print_greedy_path_routes_and_rtt "
#                     "../paper/satgenpy_analysis/paper_data ../paper/satellite_networks_state/gen_data/%s ../paper/satgenpy_analysis/graphs/%s/%dms %d %d %d %d "
#                     "> ../paper/satgenpy_analysis/paper_data/command_logs/v2_path_%s_%dms_for_%ds_%d_to_%d.log "
#                     "2>&1" % (
#                         satgenpy_generated_constellation, satgenpy_generated_constellation, update_interval_ms, update_interval_ms, duration_s, start, end,
#                         satgenpy_generated_constellation, update_interval_ms, duration_s, start, end
#                     )
#                 )



    #     # Path
    #     for update_interval_ms in list_update_interval_ms:
    #         commands_to_run.append(
    #             "cd ../../satgenpy; "
    #             "python -m satgen.post_analysis.main_analyze_path "
    #             "../paper/satgenpy_analysis/data ../paper/satellite_networks_state/gen_data/%s %d %d "
    #             "> ../paper/satgenpy_analysis/data/command_logs/constellation_comp_path_%s_%dms_for_%ds.log "
    #             "2>&1" % (
    #                 satgenpy_generated_constellation, update_interval_ms, duration_s,
    #                 satgenpy_generated_constellation, update_interval_ms, duration_s
    #             )
    #         )

    #     # RTT
    #     for update_interval_ms in list_update_interval_ms:
    #         commands_to_run.append(
    #             "cd ../../satgenpy; "
    #             "python -m satgen.post_analysis.main_analyze_rtt "
    #             "../paper/satgenpy_analysis/data ../paper/satellite_networks_state/gen_data/%s %d %d "
    #             "> ../paper/satgenpy_analysis/data/command_logs/constellation_comp_rtt_%s_%dms_for_%ds.log "
    #             "2>&1" % (
    #                 satgenpy_generated_constellation, update_interval_ms, duration_s,
    #                 satgenpy_generated_constellation, update_interval_ms, duration_s
    #             )
    #         )

    #     # Time step path
    #     commands_to_run.append(
    #         "cd ../../satgenpy; "
    #         "python -m satgen.post_analysis.main_analyze_time_step_path "
    #         "../paper/satgenpy_analysis/data ../paper/satellite_networks_state/gen_data/%s %s %d "
    #         "> ../paper/satgenpy_analysis/data/command_logs/constellation_comp_time_step_path_%s_%ds.log "
    #         "2>&1" % (
    #             satgenpy_generated_constellation,
    #             ",".join(list(map(lambda x: str(x), list_update_interval_ms))),
    #             duration_s,
    #             satgenpy_generated_constellation,
    #             duration_s
    #         )
    #     )

# Run the commands
# commands_to_run.append("python generate_all_graphs.py")
print("Running commands (at most %d in parallel)..." % max_num_processes)
for i in range(len(commands_to_run)):
    while local_shell.count_screens() >= max_num_processes:
        time.sleep(2)
    print("Starting command %d out of %d: %s" % (i + 1, len(commands_to_run), commands_to_run[i]))
    local_shell.detached_exec(commands_to_run[i])

# Awaiting final completion before exiting
print("Waiting completion of the last %d..." % max_num_processes)
while local_shell.count_screens() > 0:
    time.sleep(2)
print("Finished.")
