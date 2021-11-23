import math
import networkx as nx
from copy import deepcopy

frac = 1.2

def validate_prev_path_sat_gs_without_gs_relaying(prev_path, graph, possible_dst_satellites, distance_to_ground_station_m, max_gsl_length_m, max_isl_length_m):
    if prev_path is None:
        return False
    if not nx.is_simple_path(graph, prev_path[:-1]):
        return False
    
    last_hop_sat = prev_path[-2]
    distance_dst_sat_to_dst_m = -1
    for (dist,sat) in possible_dst_satellites:
        if sat is last_hop_sat:
            distance_dst_sat_to_dst_m = dist
    
    if distance_dst_sat_to_dst_m == -1 or distance_dst_sat_to_dst_m > max_gsl_length_m:
        return False
    
    # compute path length hop by hop, and also validate the isl lengths
    isl_path_length_m = 0.0
    for i in range(1, len(prev_path) - 1):
        from_node_id = prev_path[i - 1]
        to_node_id = prev_path[i]

        dist = graph.get_edge_data(from_node_id, to_node_id)["weight"]
        if dist > max_isl_length_m:
            return False

        isl_path_length_m += dist

    return isl_path_length_m + distance_dst_sat_to_dst_m <= frac * distance_to_ground_station_m

def validate_prev_path_gs_gs_without_gs_relaying(prev_path, graph, best_distance, dist_satellite_to_ground_station, max_gsl_length_m, max_isl_length_m):
    if prev_path is None:
        return False
    if not nx.is_simple_path(graph, prev_path[1:-1]):
        return False
    distance_src_to_src_sat_m = dist_satellite_to_ground_station[(prev_path[1], prev_path[0])]
    if distance_src_to_src_sat_m > max_gsl_length_m:
        return False
    distance_dst_sat_to_dst_m = dist_satellite_to_ground_station[(prev_path[-2], prev_path[-1])]
    if distance_dst_sat_to_dst_m > max_gsl_length_m:
        return False
    # print("inside validate prev_path", prev_path, distance_src_to_src_sat_m, distance_dst_sat_to_dst_m)
    # compute path length hop by hop, and also validate the isl lengths
    isl_path_length_m = 0.0
    for i in range(2, len(prev_path) - 1):
        from_node_id = prev_path[i - 1]
        to_node_id = prev_path[i]

        dist = graph.get_edge_data(from_node_id, to_node_id)["weight"]
        if dist > max_isl_length_m:
            return False

        isl_path_length_m += dist

    return isl_path_length_m + distance_dst_sat_to_dst_m + distance_src_to_src_sat_m <= frac * best_distance

def calculate_fstate_shortest_path_without_gs_relaying(
        output_dynamic_state_dir,
        time_since_epoch_ns,
        num_satellites,
        num_ground_stations,
        sat_net_graph_only_satellites_with_isls,
        num_isls_per_sat,
        gid_to_sat_gsl_if_idx,
        ground_station_satellites_in_range_candidates,
        sat_neighbor_to_if,
        prev_fstate,
        enable_verbose_logs,
        max_gsl_length_m,
        max_isl_length_m,
        prev_paths
):

    # Calculate shortest path distances
    if enable_verbose_logs:
        print("  > Calculating Floyd-Warshall for graph without ground-station relays")
    # (Note: Numpy has a deprecation warning here because of how networkx uses matrices)
    dist_sat_net_without_gs = nx.floyd_warshall_numpy(sat_net_graph_only_satellites_with_isls)
    shortest_paths_without_gs = dict(nx.all_pairs_shortest_path(sat_net_graph_only_satellites_with_isls))
    # Forwarding state
    fstate = {}

    # Now write state to file for complete graph
    output_filename = output_dynamic_state_dir + "/fstate_" + str(frac) + "_" + str(time_since_epoch_ns) + ".txt"
    if enable_verbose_logs:
        print("  > Writing forwarding state to: " + output_filename)
    with open(output_filename, "w+") as f_out:

        # Satellites to ground stations
        # From the satellites attached to the destination ground station,
        # select the one which promises the shortest path to the destination ground station (getting there + last hop)
        dist_satellite_to_ground_station = {}
        for curr in range(num_satellites):
            for dst_gid in range(num_ground_stations):
                dst_gs_node_id = num_satellites + dst_gid

                if (curr, dst_gs_node_id) in prev_paths:
                    prev_path, prev_ts_next_hop = prev_paths[(curr, dst_gs_node_id)]
                else:
                    prev_path, prev_ts_next_hop = None, (-1, -1, -1)
                # Among the satellites in range of the destination ground station,
                # find the one which promises the shortest distance
                possible_dst_sats = ground_station_satellites_in_range_candidates[dst_gid]
                
                possibilities = []
                for b in possible_dst_sats:
                    if not math.isinf(dist_sat_net_without_gs[(curr, b[1])]):  # Must be reachable
                        possibilities.append(
                            (
                                dist_sat_net_without_gs[(curr, b[1])] + b[0],
                                b[1]
                            )
                        )
                possibilities = list(sorted(possibilities))
                # if dst_gs_node_id == 1229:
                #     print(possible_dst_sats, possibilities)

                # By default, if there is no satellite in range for the
                # destination ground station, it will be dropped (indicated by -1)
                next_hop_decision = (-1, -1, -1)
                distance_to_ground_station_m = float("inf")
                if len(possibilities) > 0:
                    dst_sat = possibilities[0][1]
                    distance_to_ground_station_m = possibilities[0][0]
                    distance_dst_sat_to_dst_m = possibilities[0][0] - dist_sat_net_without_gs[(curr, dst_sat)]
                    best_path = deepcopy(shortest_paths_without_gs[curr][dst_sat])
                    # If the current node is not that satellite, determine how to get to the satellite
                    # This needs to be done since here it is assumed that a ground station can connect to only one satellite at a time
                    if curr != dst_sat:

                        # Among its neighbors, find the one which promises the
                        # lowest distance to reach the destination satellite
                        best_distance_m = 1000000000000000                        
                        for neighbor_id in sat_net_graph_only_satellites_with_isls.neighbors(curr):
                            distance_m = (
                                    sat_net_graph_only_satellites_with_isls.edges[(curr, neighbor_id)]["weight"]
                                    +
                                    dist_sat_net_without_gs[(neighbor_id, dst_sat)]
                            )
                            if distance_m < best_distance_m:
                                next_hop_decision = (
                                    neighbor_id,
                                    sat_neighbor_to_if[(curr, neighbor_id)],
                                    sat_neighbor_to_if[(neighbor_id, curr)]
                                )
                                best_distance_m = distance_m

                    else:
                        # This is the destination satellite, as such the next hop is the ground station itself
                        next_hop_decision = (
                            dst_gs_node_id,
                            num_isls_per_sat[dst_sat] + gid_to_sat_gsl_if_idx[dst_gid],
                            0
                        )
                        
                        best_distance_m = 0
                    # print(curr, dst_gs_node_id, prev_path, best_path, distance_dst_sat_to_dst_m, distance_to_ground_station_m)
                    # The last satellite hop could be any satellite so no need to enforce that constraint
                    # best_distance is distance till the last hop
                    if validate_prev_path_sat_gs_without_gs_relaying(prev_path, sat_net_graph_only_satellites_with_isls, ground_station_satellites_in_range_candidates[dst_gid], distance_to_ground_station_m, max_gsl_length_m, max_isl_length_m):
                        next_hop_decision = deepcopy(prev_ts_next_hop)
                        dist_satellite_to_ground_station[(curr, dst_gs_node_id)] = nx.classes.function.path_weight(sat_net_graph_only_satellites_with_isls, prev_path[:-1], "weight") + distance_dst_sat_to_dst_m
                    else:
                        best_path.append(dst_gs_node_id)
                        dist_satellite_to_ground_station[(curr, dst_gs_node_id)] = distance_to_ground_station_m
                        prev_paths[(curr, dst_gs_node_id)] = (deepcopy(best_path), deepcopy(next_hop_decision))

                # In any case, save the distance of the satellite to the ground station to re-use
                # when we calculate ground station to ground station forwarding
                if (curr, dst_gs_node_id) not in dist_satellite_to_ground_station:
                    print("infinte distance", curr, dst_gs_node_id)
                    dist_satellite_to_ground_station[(curr, dst_gs_node_id)] = math.inf

                # Write to forwarding state
                if not prev_fstate or prev_fstate[(curr, dst_gs_node_id)] != next_hop_decision:
                    f_out.write("%d,%d,%d,%d,%d\n" % (
                        curr,
                        dst_gs_node_id,
                        next_hop_decision[0],
                        next_hop_decision[1],
                        next_hop_decision[2]
                    ))
                fstate[(curr, dst_gs_node_id)] = next_hop_decision

        # Ground stations to ground stations
        # Choose the source satellite which promises the shortest path
        for src_gid in range(num_ground_stations):
            for dst_gid in range(num_ground_stations):
                if src_gid != dst_gid:
                    src_gs_node_id = num_satellites + src_gid
                    dst_gs_node_id = num_satellites + dst_gid

                    if (src_gs_node_id, dst_gs_node_id) in prev_paths:
                        prev_path, prev_ts_next_hop = prev_paths[(src_gs_node_id, dst_gs_node_id)]
                    else:
                        prev_path, prev_ts_next_hop = None, (-1,-1,-1)

                    # Among the satellites in range of the source ground station,
                    # find the one which promises the shortest distance
                    possible_src_sats = ground_station_satellites_in_range_candidates[src_gid]
                    possibilities = []
                    best_path = None
                    for a in possible_src_sats:
                        if (a[1], dst_gs_node_id) in dist_satellite_to_ground_station and not math.isinf(dist_satellite_to_ground_station[(a[1], dst_gs_node_id)]):
                            possibilities.append(
                                (
                                    a[0] + dist_satellite_to_ground_station[(a[1], dst_gs_node_id)],
                                    a[1]
                                )
                            )
                    possibilities = sorted(possibilities)

                    # By default, if there is no satellite in range for one of the
                    # ground stations, it will be dropped (indicated by -1)
                    distance_dst_sat_to_dst_m = 100000000000
                    distance_src_to_src_sat_m = 100000000000
                    next_hop_decision = (-1, -1, -1)
                    if len(possibilities) > 0:
                        src_sat_id = possibilities[0][1]
                        next_hop_decision = (
                            src_sat_id,
                            0,
                            num_isls_per_sat[src_sat_id] + gid_to_sat_gsl_if_idx[src_gid]
                        )

                        # Since we just calculated the shortest paths from sat to gs, we can use it here.
                        best_path = deepcopy(prev_paths[(src_sat_id, dst_gs_node_id)][0])
                        best_distance_m = possibilities[0][0]
                    # print(src_gs_node_id, dst_gs_node_id, prev_path)
                    if validate_prev_path_gs_gs_without_gs_relaying(prev_path, sat_net_graph_only_satellites_with_isls, best_distance_m, dist_satellite_to_ground_station, max_gsl_length_m, max_isl_length_m):
                        next_hop_decision = deepcopy(prev_ts_next_hop)
                    else:
                        if best_path is not None:
                            best_path.insert(0, src_gs_node_id)
                        prev_paths[(src_gs_node_id, dst_gs_node_id)] = (deepcopy(best_path), deepcopy(next_hop_decision))

                    # Update forwarding state
                    if not prev_fstate or prev_fstate[(src_gs_node_id, dst_gs_node_id)] != next_hop_decision:
                        f_out.write("%d,%d,%d,%d,%d\n" % (
                            src_gs_node_id,
                            dst_gs_node_id,
                            next_hop_decision[0],
                            next_hop_decision[1],
                            next_hop_decision[2]
                        ))
                    fstate[(src_gs_node_id, dst_gs_node_id)] = next_hop_decision

    # Finally return result
    return fstate


def calculate_fstate_shortest_path_with_gs_relaying(
        output_dynamic_state_dir,
        time_since_epoch_ns,
        num_satellites,
        num_ground_stations,
        sat_net_graph,
        num_isls_per_sat,
        gid_to_sat_gsl_if_idx,
        sat_neighbor_to_if,
        prev_fstate,
        enable_verbose_logs,
        prev_paths
):

    # Calculate shortest paths
    if enable_verbose_logs:
        print("  > Calculating Floyd-Warshall for graph including ground-station relays")
    # (Note: Numpy has a deprecation warning here because of how networkx uses matrices)
    dist_sat_net = nx.floyd_warshall_numpy(sat_net_graph)
    shortest_paths = dict(nx.all_pairs_shortest_path(sat_net_graph))
    print(dist_sat_net)
    print(shortest_paths)
    for node in (list(sat_net_graph.nodes)):
        print(node, sat_net_graph.edges(node))
    # Forwarding state
    fstate = {}

    # Now write state to file for complete graph
    output_filename = output_dynamic_state_dir + "/fstate_" + str(frac) + "_" + str(time_since_epoch_ns) + ".txt"
    if enable_verbose_logs:
        print("  > Writing forwarding state to: " + output_filename)
    with open(output_filename, "w+") as f_out:

        # Satellites and ground stations to ground stations
        for current_node_id in range(num_satellites + num_ground_stations):
            print(shortest_paths[current_node_id])
            for dst_gid in range(num_ground_stations):
                dst_gs_node_id = num_satellites + dst_gid

                # Cannot forward to itself
                if current_node_id != dst_gs_node_id:

                    if (current_node_id, dst_gs_node_id) in prev_paths:
                        prev_path, prev_ts_next_hop = prev_paths[(current_node_id, dst_gs_node_id)]
                    else:
                        prev_path, prev_ts_next_hop = None, (-1,-1,-1)

                    # Among its neighbors, find the one which promises the
                    # lowest distance to reach the destination satellite
                    next_hop_decision = (-1, -1, -1)
                    best_distance_m = 1000000000000000
                    best_path = None
                    for neighbor_id in sat_net_graph.neighbors(current_node_id):

                        # Any neighbor must be reachable
                        if math.isinf(dist_sat_net[(current_node_id, neighbor_id)]):
                            raise ValueError("Neighbor cannot be unreachable")

                        # Calculate distance = next-hop + distance the next hop node promises
                        distance_m = (
                            sat_net_graph.edges[(current_node_id, neighbor_id)]["weight"]
                            +
                            dist_sat_net[(neighbor_id, dst_gs_node_id)]
                        )
                        if (
                                not math.isinf(dist_sat_net[(neighbor_id, dst_gs_node_id)])
                                and
                                distance_m < best_distance_m
                        ):

                            # Check node identifiers to determine what are the
                            # correct interface identifiers
                            if current_node_id >= num_satellites and neighbor_id < num_satellites:  # GS to sat.
                                my_if = 0
                                next_hop_if = (
                                    num_isls_per_sat[neighbor_id]
                                    +
                                    gid_to_sat_gsl_if_idx[current_node_id - num_satellites]
                                )

                            elif current_node_id < num_satellites and neighbor_id >= num_satellites:  # Sat. to GS
                                my_if = (
                                    num_isls_per_sat[current_node_id]
                                    +
                                    gid_to_sat_gsl_if_idx[neighbor_id - num_satellites]
                                )
                                next_hop_if = 0

                            elif current_node_id < num_satellites and neighbor_id < num_satellites:  # Sat. to sat.
                                my_if = sat_neighbor_to_if[(current_node_id, neighbor_id)]
                                next_hop_if = sat_neighbor_to_if[(neighbor_id, current_node_id)]

                            else:  # GS to GS
                                raise ValueError("GS-to-GS link cannot exist")

                            # Write the next-hop decision
                            next_hop_decision = (
                                neighbor_id,  # Next-hop node identifier
                                my_if,        # My outgoing interface id
                                next_hop_if   # Next-hop incoming interface id
                            )

                            # Update best distance found
                            best_distance_m = distance_m
                           
                    if prev_path is not None and nx.is_simple_path(sat_net_graph, prev_path) and nx.classes.function.path_weight(sat_net_graph, prev_path) <= frac * best_distance_m:
                        next_hop_decision = deepcopy(prev_ts_next_hop)
                    else:
                        best_path = shortest_paths[current_node_id][dst_gs_node_id]
                        prev_paths[(current_node_id, dst_gs_node_id)] = (deepcopy(best_path), deepcopy(next_hop_decision))

                    # Write to forwarding state
                    if not prev_fstate or prev_fstate[(current_node_id, dst_gs_node_id)] != next_hop_decision:
                        f_out.write("%d,%d,%d,%d,%d\n" % (
                            current_node_id,
                            dst_gs_node_id,
                            next_hop_decision[0],
                            next_hop_decision[1],
                            next_hop_decision[2]
                        ))
                    fstate[(current_node_id, dst_gs_node_id)] = next_hop_decision

    # Finally return result
    return fstate
