def find_all_paths(flow_dict, current_node, sink, path=[]):
    path = path + [current_node]
    if current_node == sink:
        return [path]
    all_paths = []
    next_nodes = flow_dict[current_node]
    for next_node, flow in next_nodes.items():
        if flow > 0:
            new_paths = find_all_paths(flow_dict, next_node, sink, path)
            for new_path in new_paths:
                all_paths.append(new_path)
    return all_paths