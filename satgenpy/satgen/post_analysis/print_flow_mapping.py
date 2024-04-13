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

def get_satellite_num_connections(flow_dict, satellites):
    """
    Calculates the total user terminal connections for each satellite in the flow_dict.

    Args:
        flow_dict: A dictionary representing the graph, where keys are nodes and values are dictionaries mapping outgoing nodes to their capacities.

    Returns:
        A dictionary where keys are nodes and values are the total connections for that node.
    """
    connections = {}
    num_satellites = len(satellites)
    for node, edges in flow_dict.items():
        for neighbor, capacity in edges.items():
            if neighbor == 'S' or neighbor == 'T':
                continue
            # Skip ISLs and empty connections
            if int(neighbor) < num_satellites and int(node) > num_satellites and capacity > 0:
                if not neighbor in connections:
                    connections[neighbor] = 0
                connections[neighbor] += 1
    return connections

def get_satellite_traffic(flow_dict, satellites, outgoing=False):
    """
    Calculates the total user terminal connections for each satellite in the flow_dict.

    Args:
        flow_dict: A dictionary representing the graph, where keys are nodes and values are dictionaries mapping outgoing nodes to their capacities.

    Returns:
        A dictionary where keys are nodes and values are the total connections for that node.
    """
    connections = {}
    num_satellites = len(satellites)
    for node, edges in flow_dict.items():
        for neighbor, capacity in edges.items():
            if node == 'S' or node == 'T' or neighbor == 'S' or neighbor == 'T':
                continue
            if outgoing:
                # Calculate outgoing traffic from Satellites
                if int(node) < num_satellites and int(neighbor) >= num_satellites and capacity > 0:
                    if not node in connections:
                        connections[node] = 0
                    connections[node] += capacity
            else:
                # Calculate incoming traffic into Satellites
                if int(node) >= num_satellites and int(neighbor) < num_satellites and capacity > 0:
                    if not neighbor in connections:
                        connections[neighbor] = 0
                    connections[neighbor] += capacity
    return connections

def get_gs_outgoing_capacity(flow_dict):
    """
    Calculates the total outgoing capacity for each node in the flow_dict.

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

def get_gs_num_gsl(flow_dict, satellites):
    """
    Calculates the number of GSL for each ground station.

    Args:
        flow_dict: A dictionary representing the graph, where keys are nodes and values are dictionaries mapping outgoing nodes to their capacities.

    Returns:
        A dictionary where keys are nodes and values are the number of connections.
    """
    num_gsls = {}
    for node, edges in flow_dict.items():
        # Skip non-satellites
        if node == 'T' or node == 'S' or int(node) >= len(satellites):
            continue
        for neighbor, capacity in edges.items():
            if neighbor == 'T' or neighbor == 'S':
                continue
            if int(neighbor) >= len(satellites) and capacity > 0:
                if not neighbor in num_gsls.keys():
                    num_gsls[neighbor] = 0
                num_gsls[neighbor] += 1
    return num_gsls


def print_flow_mapping(base_output_dir, satellite_network_dir, dynamic_state_update_interval_ms, simulation_end_time_s, target_flow_time_s):
    '''
    Prints the number of user terminals connected to each satellite
    at a given time instance, and the total demand satisfied at each ground station.
    '''
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

    # Create a bar chart
    plt.rcParams.update({'font.size': 5})
    plt.figure(0, figsize=(10, 3))  # width:20, height:3
    plt.xlabel("Node")
    plt.ylabel("Total Incoming Capacity")
    plt.title("Incoming Capacity per Gateway at time "+ str(target_flow_time_s) + "s")
    plt.bar(range(len(outgoing_capacity)), capacities, align='center', width=0.3)
    plt.xticks(range(len(outgoing_capacity)), node_names)  # Rotate x-axis labels for better readability
    plt.tight_layout()
    plt.savefig(pdf_filename)

    # Satellite connections
    tles = read_tles(satellite_network_dir + "/tles.txt")
    satellites = tles["satellites"]
    connections = get_satellite_num_connections(flow_dict, satellites)

    # Extract node names and connections
    node_names = list(connections.keys())
    num_connections = list(connections.values())

    # Create a bar chart
    plt.figure(1, figsize=(10, 3))  # width:20, height:3
    plt.xlabel("Satelllite")
    plt.ylabel("User Terminals Connected")
    plt.title("Connections per Satellite at time " + str(target_flow_time_s) + "s")
    plt.bar(range(len(connections)), num_connections, align='center', width=0.3, color="green")
    plt.xticks(range(len(connections)), node_names)  # Rotate x-axis labels for better readability
    plt.tight_layout()

    pdf_filename = pdf_dir + "/networkx_connection_mapping_" + str(target_flow_time_s) + "_ut_capacity_" + str(user_terminal_gsl_capacity)+ "_mbps_" + "gs_capacity_" + str(ground_station_gsl_capacity) + "_mbps_" + str(dynamic_state_update_interval_ms) + "ms_for_" + str(simulation_end_time_s) + "s" + ".pdf"
    plt.savefig(pdf_filename)

    num_gsl_dict = get_gs_num_gsl(flow_dict, satellites)

    # Extract node names and connections
    ground_stations = list(num_gsl_dict.keys())
    num_gsls = list(num_gsl_dict.values())

    # Create a bar chart
    plt.figure(2, figsize=(10, 3))  # width:20, height:3
    plt.xlabel("GS")
    plt.ylabel("Number of GSLs")
    plt.title("Number of GSLs at " + str(target_flow_time_s) + "s")
    plt.bar(range(len(num_gsl_dict)), num_gsls, align='center', width=0.3, color="purple")
    plt.xticks(range(len(num_gsl_dict)), ground_stations)  # Rotate x-axis labels for better readability
    plt.tight_layout()

    pdf_filename = pdf_dir + "/networkx_gsl_connections_mapping_" + str(target_flow_time_s) + "_ut_capacity_" + str(user_terminal_gsl_capacity)+ "_mbps_" + "gs_capacity_" + str(ground_station_gsl_capacity) + "_mbps_" + str(dynamic_state_update_interval_ms) + "ms_for_" + str(simulation_end_time_s) + "s" + ".pdf"
    plt.savefig(pdf_filename)

    outgoing_demand_dict = get_satellite_traffic(flow_dict, satellites, outgoing=True)
    print("Num satellites with GSLs:", len(outgoing_demand_dict))

    # Extract node names and connections
    node_names = list(outgoing_demand_dict.keys())
    demands = list(outgoing_demand_dict.values())

    # Create a bar chart
    plt.figure(3, figsize=(10, 3))  # width:20, height:3
    plt.xlabel("Satelllite")
    plt.ylabel("Total Outgoing Demand")
    plt.title("Outgoing Traffic at each Satellite at time " + str(target_flow_time_s) + "s")
    plt.bar(range(len(outgoing_demand_dict)), demands, align='center', width=0.3, color="orange")
    plt.xticks(range(len(outgoing_demand_dict)), node_names)  # Rotate x-axis labels for better readability
    plt.tight_layout()

    pdf_filename = pdf_dir + "/networkx_satellite_traffic_mapping_isl_" + str(target_flow_time_s) + "_ut_capacity_" + str(user_terminal_gsl_capacity)+ "_mbps_" + "gs_capacity_" + str(ground_station_gsl_capacity) + "_mbps_" + str(dynamic_state_update_interval_ms) + "ms_for_" + str(simulation_end_time_s) + "s" + ".pdf"
    plt.savefig(pdf_filename)
