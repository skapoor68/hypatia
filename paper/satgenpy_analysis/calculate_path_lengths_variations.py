import os, sys
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.ticker as tk
import numpy as np
from collections import OrderedDict
from matplotlib.ticker import FormatStrFormatter
from matplotlib.collections import LineCollection
from datetime import datetime
import csv
import scipy
import networkx as nx
sys.path.append("../../satgenpy")
from satgen import *

total_time = 200

def calculate_path_lengths(graph, paths):
    lengths = [0] * 1000
    
    i = 0
    for path in paths:
        lengths[i] = compute_path_length_with_graph(path, graph) * 2
        i += 1
        if i >= 1000:
            break

    return np.array(lengths)

def get_all_paths_lengths(graph):
    path_lengths = []

    start_time = 0
    end_time = 200*1000*1000*1000

    for src in range(1584, 1684):
        for dst in range(src + 1, 1684):
            nodes = list(range(1584))
            nodes.append(src)
            nodes.append(dst)
            
            sat_only_graph = graph.subgraph(nodes)
            path_lengths.append(calculate_path_lengths(graphs[i], nx.shortest_simple_paths(sat_only_graph, src, dst, weight="weight")))

    return np.array(path_lengths) * 1000.0 / 299792458.0


if __name__ == '__main__':
    tt = int(sys.argv[1])

    tt = tt*1000*1000*1000
    fname = "path_length_variation_1000/paths_" + str(tt) + ".txt"
    
    graph_path = "graphs/starlink_550_isls_plus_grid_ground_stations_top_100_algorithm_free_one_only_over_isls/1000ms/graph_" + str(tt) + ".txt"
    graph = nx.read_gpickle(graph_path)

    path_lengths = []
    for src in range(1584, 1684):
        for dst in range(src + 1, 1684):
            nodes = list(range(1584))
            nodes.append(src)
            nodes.append(dst)
            
            sat_only_graph = graph.subgraph(nodes)
            path_lengths.append(calculate_path_lengths(graph, nx.shortest_simple_paths(sat_only_graph, src, dst, weight="weight")))

    ratios = [2,5,10,15]
    path_lengths = np.array(path_lengths) * 1000.0 / 299792458.0
    path_lengths = np.divide(path_lengths.T, path_lengths[:,0]).T
    # path_lengths = path_lengths[:, [1,4,9,14]]
    
    np.savetxt(fname, path_lengths, fmt="%4f")
    
