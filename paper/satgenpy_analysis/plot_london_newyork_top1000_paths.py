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

    print("1000 paths done")

    return np.array(lengths)



if __name__ == '__main__':
    # graphs = {}
    start_time = 1200*1000*1000*1000
    end_time = 1400*1000*1000*1000
    # for i in range(start_time, end_time, 1000*1000*1000):
    #     # idx = start_time + i*1000*1000*1000
    graph_path = "graphs/starlink_550_isls_plus_grid_ground_stations_newyork_london_circular_bigger_algorithm_free_one_only_over_isls/1000ms/graph_" + str(start_time) + ".txt"
    graph = nx.read_gpickle(graph_path)

    src = 1584
    dst = 1584 + 2101
    
    nodes = list(range(1584))
    nodes.append(src)
    nodes.append(dst)
    # for i in range(start_time, end_time, 1000*1000*1000):
    sat_only_graph = graph.subgraph(nodes)
    paths = nx.shortest_simple_paths(sat_only_graph, src, dst, weight="weight")
    lengths = calculate_path_lengths(sat_only_graph, paths)

    lengths = np.array(lengths) * 1000.0 / 299792458.0

    path_colors = ["brown",  "blue", "red", "darkorange", "cyan", "darkviolet", "chocolate", "gold", "fuchsia", "tan", "lawngreen", "turquoise", "teal"]

    x = np.arange(0, 1000)
    # for i in range(15):
    #     rtts = top15_rtts[:, i]
    plt.plot(x, lengths, path_colors[0], linestyle='--')
    
    # plt.title("Utilization for the New York-London Route", fontsize=18)
    plt.xlabel("Path Rank", fontsize=18)
    plt.ylabel("RTT (ms)", fontsize=18)
    plt.yticks(fontsize=14)
    plt.xticks(fontsize=14)
    plt.grid(linewidth=0.5, linestyle=':')
    plt.tight_layout()
            
    base_file = "paper_plots/top15_paths"
    png_file = base_file + ".png"
    pdf_file = base_file + ".pdf"
    plt.savefig(png_file)
    plt.savefig(pdf_file)

    paths = list(paths)
    print("Number of paths:", len(paths))