from .graph_tools import *
from satgen.isls import *
from satgen.ground_stations import *
from satgen.tles import *
import networkx as nx
from satgen.distance_tools import *
from satgen.user_terminals import *
import random
import sys

def oracle_multiple_gsls(graph_dir, satellite_network_dir, dynamic_state_update_interval_ms, simulation_start_time_s,
                         simulation_end_time_s, failure_type='None', num_failures=0):
    
    ground_stations = read_ground_stations_extended(satellite_network_dir + "/ground_stations.txt")
    user_terminals = read_user_terminals_extended(satellite_network_dir + "/user_terminals.txt")

    tles = read_tles(satellite_network_dir + "/tles.txt")
    satellites = tles["satellites"]
    epoch = tles["epoch"]

    simulation_start_time_ns = simulation_start_time_s * 1000 * 1000 * 1000
    simulation_end_time_ns = simulation_end_time_s * 1000 * 1000 * 1000
    dynamic_state_update_interval_ns = dynamic_state_update_interval_ms * 1000 * 1000

    global_schedule_counter = 0

    for t in range(simulation_start_time_ns, simulation_end_time_ns, dynamic_state_update_interval_ns):
        time = epoch + t * u.ns
        time_seconds = t / 1000 / 1000 / 1000
        global_schedule_counter = time_seconds % satellite_handoff_seconds

        # Load graph
        graph_path = graph_dir + "/graph_" + str(t) + ".txt"
        graph = nx.read_gpickle(graph_path)

        # Initialize capacity dictionaries
        satellite_capacities = {}
        ground_station_capacities = {}
        for sat_index in range(len(satellites)):
            satellite_capacities[sat_index] = {'ut_capacity': 0, 'gs_capacity': 0}
        for gs_index in range(len(ground_stations)):
            ground_station_capacities[gs_index] = 0

        # Filter first hop UT to satellite GSLs
        for ut in user_terminals:
            # Get list of satellites this UT is connected to
            ut_id = len(satellites) + len(ground_stations) + ut["uid"]
            ut_neighbor_ids = list(graph.neighbors(ut_id))

            # Get current connection
            current_connection = ut["sid"]

            # If a current connection exists from a prior time step that is not at capacity and it is not a multiple of 15 seconds
            if global_schedule_counter != 0 and current_connection is not None and satellite_capacities[current_connection]['ut_capacity'] <= ut_gsl_max_capacity:
                ut["sid"] = current_connection
                satellite_capacities[current_connection]['ut_capacity'] += ut_default_demand
                # Remove all other links
                for sat_id in ut_neighbor_ids:
                    if sat_id != current_connection:
                        graph.remove_edge(len(satellites) + len(ground_stations) + ut["uid"], sat_id)

                continue

            # Filter satellites not at capacity
            ut_neighbors_with_capacity = [sat for sat in ut_neighbor_ids if satellite_capacities[sat]['ut_capacity'] < ut_gsl_max_capacity]

            # Find closest neighboring satellite not at capacity
            closest_distance = float('inf')
            closest_sat_id = None
            for sat_id in ut_neighbors_with_capacity:
                dist_m = graph.get_edge_data(ut_id, sat_id)['weight']
                if dist_m < closest_distance:
                    closest_distance = dist_m
                    closest_sat_id = sat_id

            # Remove links to other satellites
            if closest_sat_id is not None:
                for sat_id in ut_neighbor_ids:
                    if sat_id != closest_sat_id:
                        graph.remove_edge(ut_id, sat_id)

                satellite_capacities[closest_sat_id]['ut_capacity'] += ut_default_demand
                ut["sid"] = closest_sat_id

       # Filter last hop satellite to GS GSLs
        for gs in ground_stations:
            # Get list of satellites this GS is connected to
            gs_id = len(satellites) + gs["gid"]
            gs_neighbor_ids = list(graph.neighbors(gs_id))

            # Filter out satellites at capacity
            gs_neighbors_with_capacity = [
                sat for sat in gs_neighbor_ids if 
                satellite_capacities[sat]['gs_capacity'] < ground_station_gsl_capacity and 
                ground_station_capacities[gs["gid"]] < ground_station_capacity
            ]

            # Connect GS to all satellites not at capacity
            for sat_id in gs_neighbor_ids:
                if sat_id in gs_neighbors_with_capacity:
                    # Increase capacity usage for satellite and ground station
                    satellite_capacities[sat_id]['gs_capacity'] += ground_station_gsl_capacity
                    ground_station_capacities[gs['gid']] += ground_station_gsl_capacity
                else:
                    # Remove links from satellites at capacity
                    graph.remove_edge(gs_id, sat_id)

        # Edge failure simulation
        if failure_type == 'Betweenness':
            # Fail the top `num_failures` links with the highest betweenness centrality
            terminals = list(range(len(satellites) + len(ground_stations), len(satellites) + len(ground_stations) + len(user_terminals)))
            gateways =  list(range(len(satellites), len(satellites) + len(ground_stations)))
            bottleneck_edges = nx.edge_betweenness_centrality_subset(graph, sources=terminals, targets=gateways, weight='weight')
            sorted_edges = sorted(bottleneck_edges.items(), key=lambda item: item[1], reverse=True)
            top_bottleneck_edges = [edge[0] for edge in sorted_edges[:num_failures]]
            graph.remove_edges_from(top_bottleneck_edges)
        elif failure_type == 'Random':
            # Fail `num_failures` random edges
            edges = list(graph.edges())
            failed_edges = random.sample(edges, num_failures)
            graph.remove_edges_from(failed_edges)
            
        # Add source and sink nodes
        source = "S"
        sink = "T"
        graph.add_node(source)
        graph.add_node(sink)
        
        for ut in user_terminals:
            graph.add_edge(source, len(satellites) + len(ground_stations) + ut["uid"], capacity=ut_default_demand, weight=0)
        
        for gs in ground_stations:
            graph.add_edge(len(satellites) + gs["gid"], sink, capacity=ground_station_capacity, weight=0)

        # Calculate max flow
        max_flow = nx.maximum_flow_value(graph, source, sink)
        print(f"Max flow at time {time_seconds}: {max_flow}")

def main():
    args = sys.argv[1:]
    if len(args) == 7:
        oracle_multiple_gsls(args[0],        # graph_dir
                             args[1],        # satellite_network_dir
                             int(args[2]),   # dynamic state update interval ms
                             int(args[3]),   # simulation start time s
                             int(args[4]),   # simulation end time s
                             args[5],        # failure_type
                             int(args[6]))   # num_failures
    else:
        print("Invalid argument selection for oracle_multiple_gsls.py")

if __name__ == "__main__":
    main()