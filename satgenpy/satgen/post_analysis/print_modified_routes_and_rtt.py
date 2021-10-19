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

from .graph_tools import *
from satgen.isls import *
from satgen.ground_stations import *
from satgen.tles import *
import exputil
import networkx as nx
import numpy as np
import time
import tempfile


def print_modified_routes_and_rtt(base_output_dir, satellite_network_dir, dynamic_state_update_interval_ms,
                         simulation_end_time_s, src, dst, satgenpy_dir_with_ending_slash):

    # Local shell
    local_shell = exputil.LocalShell()

    # Dynamic state dir can be inferred
    satellite_network_dynamic_state_dir = "%s/dynamic_state_%dms_for_%ds" % (
        satellite_network_dir, dynamic_state_update_interval_ms, simulation_end_time_s
    )

    # Default output dir assumes it is done manual
    pdf_dir = base_output_dir + "/pdf"
    data_dir = base_output_dir + "/data"
    local_shell.make_full_dir(pdf_dir)
    local_shell.make_full_dir(data_dir)

    # Variables (load in for each thread such that they don't interfere)
    ground_stations = read_ground_stations_extended(satellite_network_dir + "/ground_stations.txt")
    tles = read_tles(satellite_network_dir + "/tles.txt")
    satellites = tles["satellites"]
    list_isls = read_isls(satellite_network_dir + "/isls.txt", len(satellites))
    epoch = tles["epoch"]
    description = exputil.PropertiesConfig(satellite_network_dir + "/description.txt")

    # Derivatives
    simulation_end_time_ns = simulation_end_time_s * 1000 * 1000 * 1000
    dynamic_state_update_interval_ns = dynamic_state_update_interval_ms * 1000 * 1000
    max_gsl_length_m = exputil.parse_positive_float(description.get_property_or_fail("max_gsl_length_m"))
    max_isl_length_m = exputil.parse_positive_float(description.get_property_or_fail("max_isl_length_m"))

    # paths
    # path_list_per_pair = []
    # path_invalidation_ts = []
    # for i in range(len(ground_stations)):
    #     temp_list = []
    #     ts = []
    #     for j in range(len(ground_stations)):
    #         temp_list.append([])
    #         ts.append(0)
    #     path_list_per_pair.append(temp_list)
    #     path_invalidation_ts.append(ts)

    # Write data file

    data_path_filename = data_dir + "/networkx_path_" + str(src) + "_to_" + str(dst) + ".txt"
    # with open(data_path_filename, "w+") as data_path_file:

    # For each time moment
    # fstate = {}
    graphs = {}
    current_path = []
    rtt_ns_list = []
    for t in range(0, simulation_end_time_ns, dynamic_state_update_interval_ns):
        tt = time.time()
        print(tt)
        # current_fstate = {}
        # with open(satellite_network_dynamic_state_dir + "/fstate_" + str(t) + ".txt", "r") as f_in:
        #     for line in f_in:
        #         spl = line.split(",")
        #         current = int(spl[0])
        #         destination = int(spl[1])
        #         next_hop = int(spl[2])
        #         current_fstate[(current, destination)] = next_hop
        # fstate[t] = current_fstate
        graphs[t] = construct_graph_with_distances(epoch, t, satellites, ground_stations,
                                                    list_isls, max_gsl_length_m, max_isl_length_m)
        print(t, time.time() - tt)
        
    print("graph computation done")
    t = 0
    paths = []
    invalidation_ts = 0
    while(t < simulation_end_time_ns):
        if t == invalidation_ts:
            shortest_paths = k_shortest_paths(graphs[t], src, dst, 100, "weight")
            print(len(shortest_paths))
            validation_bools = np.full((100,), True)
            path_lives = np.zeros(100)
            valid_length = 1.5 * compute_path_length_with_graph(shortest_paths[0], graphs[t])
            it = t + dynamic_state_update_interval_ns
            # best_path = []
            while it < simulation_end_time_ns:
                flag = False
                for i in range(100):
                    if validation_bools[i]:
                        if not nx.is_simple_path(graphs[it], shortest_paths[i]):
                            validation_bools[i] = False
                            continue
                        else:
                            length = compute_path_length_with_graph(shortest_paths[i], graphs[it])
                            if length < valid_length:
                                flag = True
                                path_lives[i] = it
                            else:
                                validation_bools[i] = False
                    
                if not flag:
                    break

            longest_living_path = np.argmax(path_lives)
            paths.append(shortest_paths[longest_living_paths])
            invalidation_ts = path_lives[longest_living_path]
        
        curr_path = paths[-1]
        shortest_path = k_shortest_paths(graphs[t], src, dst, 1, "weight")[0]
        print(t, compute_path_length_with_graph(curr_path, graphs[t]), compute_path_length_with_graph(shortest_path, graphs[t]))
        print(t, shortest_paths)
        t = t + dynamic_state_update_interval_ns
        
            

        #         # Calculate path length
        #         path_there = get_path(src, dst, fstate)
        #         path_back = get_path(dst, src, fstate)
        #         if path_there is not None and path_back is not None:
        #             length_src_to_dst_m = compute_path_length_without_graph(path_there, epoch, t, satellites,
        #                                                                     ground_stations, list_isls,
        #                                                                     max_gsl_length_m, max_isl_length_m)
        #             length_dst_to_src_m = compute_path_length_without_graph(path_back, epoch, t,
        #                                                                     satellites, ground_stations, list_isls,
        #                                                                     max_gsl_length_m, max_isl_length_m)
        #             rtt_ns = (length_src_to_dst_m + length_dst_to_src_m) * 1000000000.0 / 299792458.0
        #         else:
        #             length_src_to_dst_m = 0.0
        #             length_dst_to_src_m = 0.0
        #             rtt_ns = 0.0

        #         # Add to RTT list
        #         rtt_ns_list.append((t, rtt_ns))

        #         # Only if there is a new path, print new path
        #         new_path = get_path(src, dst, fstate)
        #         if current_path != new_path:

        #             # This is the new path
        #             current_path = new_path

        #             # Write change nicely to the console
        #             print("Change at t=" + str(t) + " ns (= " + str(t / 1e9) + " seconds)")
        #             print("  > Path..... " + (" -- ".join(list(map(lambda x: str(x), current_path)))
        #                                       if current_path is not None else "Unreachable"))
        #             print("  > Length... " + str(length_src_to_dst_m + length_dst_to_src_m) + " m")
        #             print("  > RTT...... %.2f ms" % (rtt_ns / 1e6))
        #             print("")

        #             # Write to path file
        #             data_path_file.write(str(t) + "," + ("-".join(list(map(lambda x: str(x), current_path)))
        #                                                  if current_path is not None else "Unreachable") + "\n")

        # # Write data file
        # data_filename = data_dir + "/networkx_rtt_" + str(src) + "_to_" + str(dst) + ".txt"
        # with open(data_filename, "w+") as data_file:
        #     for i in range(len(rtt_ns_list)):
        #         data_file.write("%d,%.10f\n" % (rtt_ns_list[i][0], rtt_ns_list[i][1]))

        # # Make plot
        # pdf_filename = pdf_dir + "/time_vs_networkx_rtt_" + str(src) + "_to_" + str(dst) + ".pdf"
        # tf = tempfile.NamedTemporaryFile(delete=False)
        # tf.close()
        # local_shell.copy_file(satgenpy_dir_with_ending_slash + "plot/plot_time_vs_networkx_rtt.plt", tf.name)
        # local_shell.sed_replace_in_file_plain(tf.name, "[OUTPUT-FILE]", pdf_filename)
        # local_shell.sed_replace_in_file_plain(tf.name, "[DATA-FILE]", data_filename)
        # local_shell.perfect_exec("gnuplot " + tf.name)
        # print("Produced plot: " + pdf_filename)
        # local_shell.remove(tf.name)


