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
import copy
import tempfile
from multiprocessing.pool import ThreadPool
import threading
import csv


def calculate_path_latencies(graphs, path, dynamic_state_update_interval_ns, simulation_end_time_ns):
    latencies = [-1] * int(simulation_end_time_ns / dynamic_state_update_interval_ns)
    i = 0
    for t in range(0, simulation_end_time_ns, dynamic_state_update_interval_ns):
        if graphs[t].has_node(path[0]) and graphs[t].has_node(path[-1]) and nx.is_simple_path(graphs[t], path):
            path_length = compute_path_length_with_graph(path, graphs[t])
            latencies[i] = (2 * path_length) * 1000000000.0 / 299792458.0
        
        i += 1

    return latencies

def calculate_path_life(latency):
    start = -1

    for i in range(len(latency)):
        if latency[i] != -1:
            if start == -1:
                start = i

        else:
            if start != -1:
                return i - start

    if start == -1:
        return -1
    return len(latency) - start



def print_path_life(base_output_dir, satellite_network_dir, graph_dir, dynamic_state_update_interval_ms,
                         simulation_end_time_s, start, end, satgenpy_dir_with_ending_slash):

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
    # max_gsl_length_m = exputil.parse_positive_float(description.get_property_or_fail("max_gsl_length_m"))
    # max_isl_length_m = exputil.parse_positive_float(description.get_property_or_fail("max_isl_length_m"))

    # Write data file
    # For each time moment
    print("inside all_paths")

    graphs = {}
    distances = {}
    shortest_paths = {}
    for t in range(0, simulation_end_time_ns, dynamic_state_update_interval_ns):
        print(t)
        num_path_changes = 0

        graph_path = graph_dir + "/graph_" + str(t) + ".txt"
        # print(graph_path)
        graphs[t] = nx.read_gpickle(graph_path)
        # distances[t] = nx.floyd_warshall_numpy(graphs[t])
        # shortest_paths[t] = dict(nx.all_pairs_shortest_path(graphs[t]))

    print("all graphs loaded")

    for s in range(start, end):
        src = s + len(satellites)
        for d in range(s + 1, len(ground_stations)):                
            dst = d + len(satellites)
            print("src ", src, "dst ", dst)
            current_path = []
            rtt_ns_list = []
            f = data_dir + "/networkx_path_" + str(src) + "_to_" + str(dst) + ".txt"
            latencies = {}
            path_active_times = {}
            
            with open(f) as csvfile:
                spamreader = csv.reader(csvfile, delimiter=',',quotechar='"',quoting=csv.QUOTE_ALL, skipinitialspace=True)

                current_path = ""
                current_start = 0
                for row in spamreader:
                    if current_path != "":
                        current_end = int(row[0]) / 1000000000
                        if current_path in path_active_times:
                            print("path repeated", current_path)
                            path_active_times[current_path] += (current_end - current_start)
                        else:
                            path_active_times[current_path] = (current_end - current_start)
                    current_start = int(row[0]) / 1000000000
                    path = list(row[1].split("-"))
                    path = [int(i) for i in path]
                    latencies[row[1]] = calculate_path_latencies(graphs, path, dynamic_state_update_interval_ns, simulation_end_time_ns)
                    current_path = row[1]

                if current_path in path_active_times:
                    print("path repeated", current_path)
                    path_active_times[current_path] += (6000 - current_start)
                else:
                    path_active_times[current_path] = (6000 - current_start)

            data_path_filename = data_dir + "/networkx_life_of_path_" + str(src) + "_to_" + str(dst) + ".txt"
            print()
            with open(data_path_filename, "w+") as data_path_file:
                for path in path_active_times.keys():
                    active_time = path_active_times[path]
                    latency = latencies[path]
                    path_life = calculate_path_life(latency)
                    data_path_file.write(path + "," + str(active_time) + "," + str(path_life) + "," + 
                        ("_".join(list(map(lambda x: str(x), latency))) if current_path is not None else "Unreachable") + "\n")