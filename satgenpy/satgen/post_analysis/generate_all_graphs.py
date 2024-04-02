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
import numpy as np
import time
import tempfile
import json
from astropy import units as u
from satgen.distance_tools import *
from satgen.simulate_failures import *

def generate_satellite_shell_index(num_satellites, num_orbits, num_sats_per_orbit):
    satellites_shell_idx = {}
    idx = 0
    sats_so_far = 0
    for i in range(num_satellites):
        if i == (num_orbits[idx] * num_sats_per_orbit[idx]) + sats_so_far:
            idx += 1
        
        satellites_shell_idx[i] = idx

    return satellites_shell_idx

def generate_all_graphs(base_output_dir, satellite_network_dir, dynamic_state_update_interval_ms,
                         simulation_start_time_s, simulation_end_time_s, n_shells = 1, allow_multiple_gsl=False):

    print(simulation_start_time_s, simulation_end_time_s)

    # Dynamic state dir can be inferred
    satellite_network_dynamic_state_dir = "%s/dynamic_state_%dms_for_%ds" % (
        satellite_network_dir, dynamic_state_update_interval_ms, simulation_end_time_s
    )

    # Variables (load in for each thread such that they don't interfere)
    ground_stations = read_ground_stations_extended(satellite_network_dir + "/ground_stations.txt")
    user_terminals = read_user_terminals_extended(satellite_network_dir + "/user_terminals.txt")

    tles = read_tles(satellite_network_dir + "/tles.txt")
    satellites = tles["satellites"]
    list_isls = read_isls(satellite_network_dir + "/isls.txt", len(satellites))
    epoch = tles["epoch"]
    description = exputil.PropertiesConfig(satellite_network_dir + "/description.txt")

    failure_table = parse_failure_file("~/hypatia-robin/paper/satellite_networks_state/input_data/failure_config_1.txt") # Specify failure configuration here

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
        print(num_orbits, num_sats_per_orbit, max_gsl_length_m, max_isl_length_m, len(satellites))

    # Global scheduling counter. Once it reaches 15 seconds, re-allocation happens.
    schedule_count = 0
    for t in range(simulation_start_time_ns, simulation_end_time_ns, dynamic_state_update_interval_ns):
        print(t)
        graph_path_filename = base_output_dir + "/graph_" + str(t) + ".txt"
        # Time
        time = epoch + t * u.ns
        time_seconds = t / 1000 / 1000 / 1000
        schedule_count = time_seconds % satellite_handoff_seconds
        print("schedule count:", schedule_count)

        # Graph
        sat_net_graph_with_gs = nx.DiGraph()

        # ISLs
        for (a,b) in list_isls:
            if (a, b) in failure_table["ISL"] and failure_table["ISL"][(a, b)][0] <= t <= failure_table["ISL"][(a, b)][1]:
                continue
            if a in failure_table["SAT"] and failure_table["SAT"][a][0] <= t <= failure_table["SAT"][a][1]:
                continue
            if b in failure_table["SAT"] and failure_table["SAT"][b][0] <= t <= failure_table["SAT"][b][1]:
                continue    
            if n_shells == 1:
                max_length = max_isl_length_m
            else:
                max_length = max_isl_length_m[satellites_shell_idx[a]]

            # Only ISLs which are close enough are considered
            sat_distance_m = distance_m_between_satellites(satellites[a], satellites[b], str(epoch), str(time))
            if sat_distance_m <= max_length:
                rounded_dist = round(sat_distance_m)
                sat_net_graph_with_gs.add_edge(
                    a, b, weight=rounded_dist, capacity=isl_capacity
                )
                sat_net_graph_with_gs.add_edge(
                    b, a, weight=rounded_dist, capacity=isl_capacity
                )

        # GSLs
        # Each Satellite can only connect to one ground station at a time unless allow_multiple_gsl is enabled
        for sid in range(len(satellites)):
            if sid in failure_table["SAT"] and failure_table["SAT"][sid][0] <= t <= failure_table["SAT"][sid][1]:
                continue
            min_dist = float('inf')
            nearest_gid = -1
            satellite = satellites[sid]
            # Find ground stations in range and connect to nearest
            for gid in range(len(ground_stations)):
                ground_station = ground_stations[gid]
                if n_shells == 1:
                    max_length = max_gsl_length_m
                else:                    
                    max_length = max_gsl_length_m[satellites_shell_idx[sid]]
                
                distance_m = distance_m_ground_station_to_satellite(ground_station, satellite, str(epoch), str(time))

                if sat_net_graph_with_gs.has_node(len(satellites) + gid) and sat_net_graph_with_gs.degree(len(satellites)+gid, "capacity") >= ground_station_capacity:
                    # if this ground station is at full capacity, don't connect to it
                    continue
                
                # If multiple GSL connections is enabled, connect to every GS within range.
                if allow_multiple_gsl:
                    sat_net_graph_with_gs.add_edge(sid, len(satellites) + gid, weight=rounded_dist, capacity=ground_station_gsl_capacity)
                # Single GSL connection to nearest GS
                elif distance_m <= max_length and distance_m < min_dist:
                    min_dist = distance_m
                    nearest_gid = gid

            if nearest_gid != -1:
                rounded_dist = round(min_dist)
                
                sat_net_graph_with_gs.add_edge(sid, len(satellites) + nearest_gid, weight=rounded_dist, capacity=ground_station_gsl_capacity)


        # Each User Terminal can only connect to one satellite at a time
        for user_terminal in user_terminals:
            # Check current connection
            current_connection = user_terminal["sid"]
            if current_connection:
                if n_shells == 1:
                    max_length = max_gsl_length_m
                else:                    
                    max_length = max_gsl_length_m[satellites_shell_idx[current_connection]]

                distance_m = distance_m_ground_station_to_satellite(user_terminal, satellites[current_connection], str(epoch), str(time))
                if distance_m > max_length or (current_connection in failure_table["SAT"] and failure_table["SAT"][current_connection][0] <= t <= failure_table["SAT"][current_connection][1]):
                    # Current connection is out of range or failing
                    # Disconnect the satellite
                    user_terminal["sid"] = None
                elif schedule_count != 0:
                    # Current connection is still in range and active
                    # If it's not time to reallocate, keep this connection.
                    sat_net_graph_with_gs.add_edge(len(satellites) + len(ground_stations) + user_terminal["uid"], current_connection, weight=rounded_dist, capacity=user_terminal_gsl_capacity, ut_demand=ut_default_demand)
                    continue

            # Current connection is out of range
            # Find satellites in range and connect to nearest
            min_dist = float('inf')
            nearest_sid = -1
            for sid in range(len(satellites)):
                if sid in failure_table["SAT"] and failure_table["SAT"][sid][0] <= t <= failure_table["SAT"][sid][1]:
                    # Skip satellites that are failing
                    # Check for failing current connection is moved earlier
                    # if sid == user_terminal["sid"]: # if the UT is connected to a failed satellite
                    #     user_terminal["sid"] = None # disconnect the UT from the failed satellite
                    continue
                if n_shells != 1:            
                    max_length = max_gsl_length_m[satellites_shell_idx[sid]]
                
                distance_m = distance_m_ground_station_to_satellite(user_terminal, satellites[sid], str(epoch), str(time))

                if sat_net_graph_with_gs.degree(sid, "ut_demand") >= satellite_max_capacity:
                    # if this satellite has full capacity, don't connect to it
                    continue

                if distance_m <= max_length and distance_m < min_dist:
                    min_dist = distance_m
                    nearest_sid = sid

            if nearest_sid != -1:
                rounded_dist = round(min_dist)
                user_terminal["sid"] = nearest_sid
                
                sat_net_graph_with_gs.add_edge(len(satellites) + len(ground_stations) + user_terminal["uid"], nearest_sid, weight=rounded_dist, capacity=user_terminal_gsl_capacity, ut_demand=ut_default_demand)

            # elif user_terminal["hop_count"] > 1:
            #     # Connected satellite exists and has hop count remaining, decrease hop count
            #     user_terminal["hop_count"] -= 1
            #     # Keep the connection
            #     sat_net_graph_with_gs.add_edge(len(satellites) + len(ground_stations) + user_terminal["uid"], user_terminal["sid"], weight=rounded_dist, capacity=user_terminal_gsl_capacity, ut_demand=ut_default_demand)

            # else:
            #     # Connected satellite exists but out of hop count
            #     # Connect to new satellite and reset hop count
            #     user_terminal["sid"] = nearest_sid
            #     user_terminal["hop_count"] = satellite_handoff_seconds

                # sat_net_graph_with_gs.add_edge(len(satellites) + len(ground_stations) + user_terminal["uid"], nearest_sid, weight=rounded_dist, capacity=user_terminal_gsl_capacity, ut_edmand=ut_default_demand)

        nx.write_gpickle(sat_net_graph_with_gs, graph_path_filename)