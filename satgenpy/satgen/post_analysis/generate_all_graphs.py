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
import json
from astropy import units as u
from satgen.distance_tools import *

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
                         simulation_start_time_s, simulation_end_time_s, n_shells = 1, use_capacity=False):

    print(simulation_start_time_s, simulation_end_time_s)

    # Dynamic state dir can be inferred
    satellite_network_dynamic_state_dir = "%s/dynamic_state_%dms_for_%ds" % (
        satellite_network_dir, dynamic_state_update_interval_ms, simulation_end_time_s
    )

    # Variables (load in for each thread such that they don't interfere)
    ground_stations = read_ground_stations_extended(satellite_network_dir + "/ground_stations.txt")
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
        print(num_orbits, num_sats_per_orbit, max_gsl_length_m, max_isl_length_m, len(satellites))

    isl_capacity = 1000000
    gsl_capacity = 800000

    for t in range(simulation_start_time_ns, simulation_end_time_ns, dynamic_state_update_interval_ns):
        print(t)
        graph_path_filename = base_output_dir + "/graph_" + str(t) + ".txt"
        # Time
        time = epoch + t * u.ns

        # Graph
        sat_net_graph_with_gs = nx.Graph()

        # ISLs
        for (a,b) in list_isls:            
            if n_shells == 1:
                max_length = max_isl_length_m
            else:
                max_length = max_isl_length_m[satellites_shell_idx[a]]

            # Only ISLs which are close enough are considered
            sat_distance_m = distance_m_between_satellites(satellites[a], satellites[b], str(epoch), str(time))
            if sat_distance_m <= max_length:
                if use_capacity:
                    sat_net_graph_with_gs.add_edge(
                        a, b, weight=sat_distance_m, capacity=isl_capacity
                    )
                else:
                    sat_net_graph_with_gs.add_edge(
                        a, b, weight=sat_distance_m
                    )

        # GSLs
        for ground_station in ground_stations:
            # Find satellites in range
            for sid in range(len(satellites)):
                if n_shells == 1:
                    max_length = max_gsl_length_m
                else:                    
                    max_length = max_gsl_length_m[satellites_shell_idx[sid]]
                
                distance_m = distance_m_ground_station_to_satellite(ground_station, satellites[sid], str(epoch), str(time))
                if distance_m <= max_length:
                    if use_capacity:
                        sat_net_graph_with_gs.add_edge(len(satellites) + ground_station["gid"], sid, weight=distance_m, capacity=gsl_capacity)
                    else:
                        sat_net_graph_with_gs.add_edge(len(satellites) + ground_station["gid"], sid, weight=distance_m)

        nx.write_gpickle(sat_net_graph_with_gs, graph_path_filename)