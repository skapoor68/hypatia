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
import matplotlib.pyplot as plt
import pandas as pd

def print_max_flow_for_src(base_output_dir, graphs, satellites, ground_stations, user_terminals, dynamic_state_update_interval_ns, simulation_end_time_ns):
    
    local_shell = exputil.LocalShell()

    data_dir = base_output_dir + "/data"
    pdf_dir = base_output_dir + "/pdf"
    local_shell.make_full_dir(pdf_dir)
    local_shell.make_full_dir(data_dir)

    dynamic_state_update_interval_ms = dynamic_state_update_interval_ns / 1000 /1000
    simulation_end_time_s = simulation_end_time_ns / 1000 / 1000 / 1000

    data_filename = data_dir + "/networkx_all_flow_" + str(dynamic_state_update_interval_ms) +"ms_for_" + str(simulation_end_time_s) + "s" ".txt"

    flow_list = []
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
                # graph.add_edge(source, len(satellites) + len(ground_stations) + ut["uid"], capacity=ut["demand"])
                graph.add_edge(source, len(satellites) + len(ground_stations) + ut["uid"], capacity=ut_default_demand)
        
            
            # Add edges from sinks to super-sink
            for gs in ground_stations:
                # Ground stations to sink has unbounded limit
                graph.add_edge(len(satellites) + gs["gid"], sink, capacity=ground_station_capacity)

            # Find the max flow (demand satisfied)
            # flow_value, flow_dict = nx.maximum_flow(graph, source, sink) 

            # Find the max flow (demand satisfied) using the minimum cost (distance)
            min_cost_flow_dict = nx.max_flow_min_cost(graph, source, sink)   
            min_cost = nx.cost_of_flow(G=graph, flowDict=min_cost_flow_dict)
            min_cost_flow_value = sum((min_cost_flow_dict[u][sink] for u in graph.predecessors(sink)))

            data_flow_file.write("flow value:" + str(min_cost_flow_value) + "\n" + "flow_dict:\n")
            data_flow_file.write(str(min_cost_flow_dict))

            flow_list.append((t, min_cost_flow_value))   

            # Plot the graph with only edges used for flow
            # selected_edges = [(u,v) for u,v,e in graph.edges(data=True) if flow_dict[u][v] > 0]
            # selected_nodes = [n for n,v in graph.nodes(data=True) if len(flow_dict[n].values()) > 0 and max(flow_dict[n].values()) > 0]
            # # for python 2.x:
            # plt.bar(range(len(D)), D.values(), align='center')  # python 2.x
            # plt.xticks(range(len(D)), D.keys())  # in python 2.x


    with open(data_filename, "w+") as flow_value_file:
        for i in range(len(flow_list)):
            flow_value_file.write("%d,%.10f\n" % (flow_list[i][0], flow_list[i][1]))

    pdf_dir = base_output_dir + "/pdf"
    pdf_filename = pdf_dir + "/time_vs_networkx_flow_num_ut_" + str(len(user_terminals)) + "_ut_capacity_"+ str(user_terminal_gsl_capacity)+ "_mbps_num_gs_" + str(len(ground_stations)) + "_gs_capacity_" + str(ground_station_gsl_capacity) + "_mbps_" + str(dynamic_state_update_interval_ms) + "ms_for_" + str(simulation_end_time_s) + "s" + ".pdf"
    tf = tempfile.NamedTemporaryFile(delete=False)
    tf.close()
    local_shell.copy_file("plot/plot_time_vs_networkx_flow.plt", tf.name)
    local_shell.sed_replace_in_file_plain(tf.name, "[OUTPUT-FILE]", pdf_filename)
    local_shell.sed_replace_in_file_plain(tf.name, "[DATA-FILE]", data_filename)

    ut_demand_total = 0
    for ut in user_terminals:
        ut_demand_total += ut_default_demand
    local_shell.sed_replace_in_file_plain(tf.name, "UT_DEMAND_TOTAL", str(ut_demand_total))

    local_shell.perfect_exec("gnuplot " + tf.name)
    print("Total UT demand:", ut_demand_total)
    print("Produced plot: " + pdf_filename)
    local_shell.remove(tf.name)

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
    print_max_flow_for_src(base_output_dir, graphs, satellites, ground_stations, user_terminals, dynamic_state_update_interval_ns, simulation_end_time_ns)
    #     pool.apply_async(print_routes_and_rtt_for_src, (s, graphs, satellites, ground_stations, data_dir, dynamic_state_update_interval_ns, simulation_end_time_ns))

    # pool.close()
    # pool.join()

    


