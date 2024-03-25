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
import tempfile
import matplotlib.pyplot as plt
import pandas as pd
import ast
import numpy as np


def parse_flow_file(filename):
    """
    Parses a flow file and creates a dictionary representing the graph.

    Args:
        filename: The name of the file containing the flow data.

    Returns:
        A dictionary where keys are nodes and values are dictionaries mapping outgoing nodes to their capacities.
    """
    flow_dict = {}
    with open(filename) as f:
        next(f)
        next(f)
        flow_dict = ast.literal_eval(f.read())
    return flow_dict


def get_gs_outgoing_capacity(flow_dict):
    """
    Calculates the total outgoing capacity for each gateway in the flow_dict.

    Args:
        flow_dict: A dictionary representing the graph, where keys are nodes and values are dictionaries mapping outgoing nodes to their capacities.

    Returns:
        A dictionary where keys are nodes and values are the total outgoing capacity for that node.
    """
    outgoing_capacity = {}
    for node, edges in flow_dict.items():
        for neighbor, capacity in edges.items():
            if neighbor == 'T' and capacity > 0:
                if not node in outgoing_capacity.keys():
                    outgoing_capacity[node] = 0
                outgoing_capacity[node] += capacity
    return outgoing_capacity


def print_flow_mapping(base_output_dir, satellite_network_dir, dynamic_state_update_interval_ms, simulation_end_time_s, target_flow_time_s):
    
    local_shell = exputil.LocalShell()

    data_dir = base_output_dir + "/data"
    pdf_dir = base_output_dir + "/pdf"
    local_shell.make_full_dir(pdf_dir)
    local_shell.make_full_dir(data_dir)

    target_flow_time_ns = target_flow_time_s * 1000 * 1000 * 1000

    data_filename = data_dir + "/networkx_flow_" + str(target_flow_time_ns) + ".txt"

    pdf_dir = base_output_dir + "/pdf"
    pdf_filename = pdf_dir + "/networkx_flow_mapping_" + str(target_flow_time_s) + "_ut_capacity_" + str(user_terminal_gsl_capacity)+ "_mbps_" + "gs_capacity_" + str(ground_station_gsl_capacity) + "_mbps_" + str(dynamic_state_update_interval_ms) + "ms_for_" + str(simulation_end_time_s) + "s" + ".pdf"

    flow_dict = parse_flow_file(data_filename)
    outgoing_capacity = get_gs_outgoing_capacity(flow_dict)

    # Extract node names and capacities
    node_names = list(outgoing_capacity.keys())
    capacities = list(outgoing_capacity.values())

    print(len(node_names))
    print(len(capacities))

    # Create a bar chart
    plt.rcParams.update({'font.size': 5})
    plt.figure(figsize=(10, 3))  # width:20, height:3
    plt.xlabel("Node")
    plt.ylabel("Total Incoming Capacity")
    plt.title("Incoming Capacity per Gateway")
    plt.bar(range(len(outgoing_capacity)), capacities, align='center', width=0.3)
    plt.xticks(range(len(outgoing_capacity)), node_names)  # Rotate x-axis labels for better readability
    plt.tight_layout()
    plt.savefig(pdf_filename)


    # tf = tempfile.NamedTemporaryFile(delete=False)
    # tf.close()
    # local_shell.copy_file("plot/plot_time_vs_networkx_flow.plt", tf.name)
    # local_shell.sed_replace_in_file_plain(tf.name, "[OUTPUT-FILE]", pdf_filename)
    # local_shell.sed_replace_in_file_plain(tf.name, "[DATA-FILE]", data_filename)

    # ut_demand_total = 0
    # for ut in user_terminals:
    #     ut_demand_total += ut_default_demand
    # local_shell.sed_replace_in_file_plain(tf.name, "UT_DEMAND_TOTAL", str(ut_demand_total))

    # local_shell.perfect_exec("gnuplot " + tf.name)
    # print("Total UT demand:", ut_demand_total)
    # print("Produced plot: " + pdf_filename)
    # local_shell.remove(tf.name)