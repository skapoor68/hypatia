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
from satgen.user_terminals import *
from satgen.tles import *
import exputil
import copy
import tempfile
from multiprocessing.pool import ThreadPool
import threading
import math

def print_max_flow_for_src(graphs, satellites, ground_stations, user_terminals, data_dir, dynamic_state_update_interval_ns, simulation_end_time_ns):
    src = 0
    # Step 1. Assign the super source and super sink nodes
    for t in range(0, simulation_end_time_ns, dynamic_state_update_interval_ns):
        data_flow_filename = data_dir + "/networkx_flow_" + str(t) + ".txt"
        with open(data_flow_filename, "w+") as data_flow_file:
            # Get the graph at this time
            graph = graphs[t]

            # Add the super-source and super-sinks into the graph
            source = "S"
            sink = "T"
            graph.add_node(source)
            graph.add_node(sink)

            # Add edges from super-source to sources
            for ut in user_terminals:
                # Source to user terminals is capped at each user terminal's demand
                graph.add_edge(source, len(satellites) + len(ground_stations) + ut["uid"], capacity=ut["demand"])
            
            # Add edges from sinks to super-sink
            for gs in ground_stations:
                # Ground stations to sink has unbounded limit
                graph.add_edge(len(satellites) + gs["gid"], sink, capacity=float('inf'))

            flow_value, flow_dict = nx.maximum_flow(graph, source, sink)
            data_flow_file.write("flow value:" + str(flow_value) + "\n" + "flow_dict:\n")
            data_flow_file.write(str(flow_dict))
            


def print_all_max_flows(base_output_dir, satellite_network_dir, graph_dir, dynamic_state_update_interval_ms,
                         simulation_end_time_s):

    # Local shell
    local_shell = exputil.LocalShell()

    # Dynamic state dir can be inferred
    # satellite_network_dynamic_state_dir = "%s/dynamic_state_%dms_for_%ds" % (
    #     satellite_network_dir, dynamic_state_update_interval_ms, simulation_end_time_s
    # )

    # Default output dir assumes it is done manual
    pdf_dir = base_output_dir + "/pdf"
    data_dir = base_output_dir + "/data"
    local_shell.make_full_dir(pdf_dir)
    local_shell.make_full_dir(data_dir)

    # Variables (load in for each thread such that they don't interfere)
    ground_stations = read_ground_stations_extended(satellite_network_dir + "/ground_stations.txt")
    user_terminals = read_user_terminals_extended(satellite_network_dir + "/user_terminals.txt")
    tles = read_tles(satellite_network_dir + "/tles.txt")
    satellites = tles["satellites"]

    # Derivatives
    simulation_end_time_ns = simulation_end_time_s * 1000 * 1000 * 1000
    dynamic_state_update_interval_ns = dynamic_state_update_interval_ms * 1000 * 1000
    # max_gsl_length_m = exputil.parse_positive_float(description.get_property_or_fail("max_gsl_length_m"))
    # max_isl_length_m = exputil.parse_positive_float(description.get_property_or_fail("max_isl_length_m"))

    # Write data file
    # For each time moment
    print("inside all_paths")

    graphs = {}

    for t in range(0, simulation_end_time_ns, dynamic_state_update_interval_ns):
        print(t)

        graph_path = graph_dir + "/graph_" + str(t) + ".txt"
        # print(graph_path)
        graphs[t] = nx.read_gpickle(graph_path)
        # sat_only_graphs[t] = graphs[t].subgraph(list(range(len(satellites))))
        # distances[t] = nx.floyd_warshall_numpy(sat_only_graphs[t])
        # shortest_paths[t] = dict(nx.all_pairs_shortest_path(graphs[t]))

    print("all graphs loaded")
    print_max_flow_for_src(graphs, satellites, ground_stations, user_terminals, data_dir, dynamic_state_update_interval_ns, simulation_end_time_ns)
    #     pool.apply_async(print_routes_and_rtt_for_src, (s, graphs, satellites, ground_stations, data_dir, dynamic_state_update_interval_ns, simulation_end_time_ns))

    # pool.close()
    # pool.join()

    


