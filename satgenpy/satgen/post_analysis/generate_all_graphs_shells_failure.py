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
import networkx as nx
import json
from astropy import units as u
from satgen.distance_tools import *
from satgen.simulate_failures import *
import pickle

def generate_satellite_shell_index(num_satellites, num_orbits, num_sats_per_orbit):
    satellites_shell_idx = {}
    idx = 0
    sats_so_far = 0
    for i in range(num_satellites):
        if i == (num_orbits[idx] * num_sats_per_orbit[idx]) + sats_so_far:
            idx += 1
        
        satellites_shell_idx[i] = idx

    return satellites_shell_idx

def generate_all_graphs_shells_failure(base_output_dir, satellite_network_dir, dynamic_state_update_interval_ms,
                         simulation_start_time_s, simulation_end_time_s, n_shells = 1, failure_id=0, allow_multiple_gsl=True):

    print(f"Start time: {simulation_start_time_s}s. End time: {simulation_end_time_s}s")

    # Variables (load in for each thread such that they don't interfere)
    ground_stations = read_ground_stations_extended(satellite_network_dir + "/ground_stations.txt")
    user_terminals = read_user_terminals_extended(satellite_network_dir + "/user_terminals.txt")

    tles = read_tles(satellite_network_dir + "/tles.txt")
    satellites = tles["satellites"]
    list_isls = read_isls(satellite_network_dir + "/isls.txt", len(satellites))
    epoch = tles["epoch"]
    description = exputil.PropertiesConfig(satellite_network_dir + "/description.txt")

    # Derivatives
    simulation_start_time_ns = simulation_start_time_s * 1000 * 1000 * 1000
    simulation_end_time_ns = simulation_end_time_s * 1000 * 1000 * 1000
    dynamic_state_update_interval_ns = dynamic_state_update_interval_ms * 1000 * 1000
    if n_shells == 1:
        max_gsl_length_m = exputil.parse_positive_float(description.get_property_or_fail("max_gsl_length_m"))
        max_isl_length_m = exputil.parse_positive_float(description.get_property_or_fail("max_isl_length_m"))
    else:
        num_orbits = json.loads(description.get_property_or_fail("num_orbits"))
        num_sats_per_orbit = json.loads(description.get_property_or_fail("num_sats_per_orbit"))
        max_gsl_length_m = json.loads(description.get_property_or_fail("max_gsl_length_m"))
        max_isl_length_m = json.loads(description.get_property_or_fail("max_isl_length_m"))
        satellites_shell_idx = generate_satellite_shell_index(len(satellites), num_orbits, num_sats_per_orbit)
        # print(num_orbits, num_sats_per_orbit, max_gsl_length_m, max_isl_length_m, len(satellites))

    # Global scheduling counter. Once it reaches 15 seconds, re-allocation happens.
    schedule_count = 0
    for t in range(simulation_start_time_ns, simulation_end_time_ns, dynamic_state_update_interval_ns):
        print(f"Generating graph for t = {t}")
        graph_path_filename = base_output_dir + "/graph_" + str(t) + ".txt"
        # Time
        time = epoch + t * u.ns
        time_seconds = t / 1000 / 1000 / 1000
        schedule_count = time_seconds % satellite_handoff_seconds
        print("Global schedule count:", schedule_count)

        # Initialize nx graph
        graph = nx.DiGraph()
        isls = dict()

        # Initialize satellite and GS capacities
        satellite_capacities = {}
        ground_station_capacities = {}

        for satellite in range(len(satellites)):
            satellite_capacities[satellite] = {'ut_capacity': 0, 'gs_capacity': 0}

        for ground_station in range(len(ground_stations)):
            ground_station_capacities[ground_station] = {'gs_capacity': 0}      

        # ISLs
        for (a, b) in list_isls:
            if n_shells == 1:
                max_length = max_isl_length_m
            else:
                max_length = max_isl_length_m[satellites_shell_idx[a]]

            # Only ISLs which are close enough are considered
            sat_distance_m = distance_m_between_satellites(satellites[a], satellites[b], str(epoch), str(time))
            if sat_distance_m <= max_length:
                rounded_dist = round(sat_distance_m)
                graph.add_edge(
                    a, b, weight=rounded_dist, capacity=isl_capacity, type='isl'
                )
                graph.add_edge(
                    b, a, weight=rounded_dist, capacity=isl_capacity, type='isl'
                )
                # Creating mapping of satellites to its neighbors
                if not a in isls:
                    isls[a] = []
                isls[a].append(b)
                if not b in isls:
                    isls[b] = []
                isls[b].append(a)


        # UT to satellite GSLs
        for ut in user_terminals:
            current_connection = ut['sid']
            if current_connection is not None:
                if n_shells == 1:
                    max_length = max_gsl_length_m
                else:                    
                    max_length = max_gsl_length_m[satellites_shell_idx[current_connection]]
                distance_m = distance_m_ground_station_to_satellite(ut, satellites[current_connection], str(epoch), str(time))
                if distance_m > max_length:
                    # Current connection is out of range so disconnect it 
                    ut['sid'] = None
                elif schedule_count != 0 and graph.has_node(current_connection) and satellite_capacities[current_connection]['ut_capacity'] < ut_gsl_max_capacity:
                    # Current connection is in range and has available UT capacity
                    ut['sid'] = current_connection
                    satellite_capacities[current_connection]['ut_capacity'] += ut_default_demand
                    graph.add_edge(len(satellites) + len(ground_stations) + ut["uid"], current_connection, weight=distance_m, capacity=ut_default_demand, type='uplink_gsl')
                    continue

            # If current connection is None, out of range, or schedule_count is 0, establish a new connection
            min_dist = float('inf')
            first_hop_sat = -1
            for sid in range(len(satellites)):
                if n_shells == 1:
                    max_length = max_gsl_length_m
                else:                    
                    max_length = max_gsl_length_m[satellites_shell_idx[sid]]

                distance_m = distance_m_ground_station_to_satellite(ut, satellites[sid], str(epoch), str(time))
                # If the distance from UT to satellite is in range, the distance is the shortest so far, and the satellite has available UT capacity
                if distance_m <= max_length and distance_m < min_dist and satellite_capacities[sid]['ut_capacity'] < ut_gsl_max_capacity:
                    min_dist = distance_m
                    first_hop_sat = sid

            if first_hop_sat != -1:
                ut['sid'] = first_hop_sat
                satellite_capacities[first_hop_sat]['ut_capacity'] += ut_default_demand
                graph.add_edge(len(satellites) + len(ground_stations) + ut["uid"], first_hop_sat, weight=min_dist, capacity=ut_default_demand, type='uplink_gsl')

        # Satellite to GS GSLs
        # Satellites connect to all in range GSes with available capacity
        for sid in range(len(satellites)):
            for gs in range(len(ground_stations)):
                if n_shells == 1:
                    max_length = max_gsl_length_m
                else:                    
                    max_length = max_gsl_length_m[satellites_shell_idx[sid]]

                distance_m = distance_m_ground_station_to_satellite(ground_stations[gs], satellites[sid], str(epoch), str(time))
                # If the distance from GS to satellite is in range, the satellite has available GS capacity, and the GS has available capacity
                if distance_m <= max_length and satellite_capacities[sid]['gs_capacity'] < ground_station_gsl_capacity and ground_station_capacities[gs]['gs_capacity'] < ground_station_capacity:
                    satellite_capacities[sid]['gs_capacity'] += ut_default_demand
                    ground_station_capacities[gs]['gs_capacity'] += ut_default_demand
                    graph.add_edge(sid, len(satellites) + gs, weight=distance_m, capacity=ut_default_demand, type='downlink_gsl')   

        with open(graph_path_filename, 'wb') as f:
            pickle.dump(graph, f)