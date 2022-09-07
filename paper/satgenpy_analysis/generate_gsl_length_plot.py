import os, sys
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.ticker as tk
import numpy as np
from collections import OrderedDict
from matplotlib.ticker import FormatStrFormatter
from datetime import datetime
import csv
import networkx as nx
import scipy

def load_data(src=3168):
    ratio = []
    dir = "graphs/starlink_2shells_isls_plus_grid_ground_stations_top_100_algorithm_free_one_only_over_isls/1000ms/"
    total_time = 6000
    nodes = list(range(1584))
    nodes.append(src)
    graphs = {}
    lengths = []
    for tt in range(total_time):
        graph_path = dir + "graph_" + str(tt * 1000*1000*1000) + ".txt"
        graph = nx.read_gpickle(graph_path).subgraph(nodes)
        print(len(list(graph[src].keys())))
        for x in graph[src].values():
            lengths.append(x["weight"])
        # lengths = lengths + list(graph[src].values().values())
        # print(lengths)
        # graphs[tt] = graph.subgraph(nodes)

    
    return np.array(lengths)

if __name__ == '__main__':

    # for i in range(1584, 1684):
    #     lengths = load_data(i) / 1000
    #     print(i, np.min(lengths))
        
    lengths = load_data() / 1000
    print("Mean, 25th Percentile, Median, 75th Percentile, 90th Percentile, Max, Min, Std")
    print(np.mean(lengths), np.percentile(lengths, 25), np.median(lengths), np.percentile(lengths, 75), np.percentile(lengths, 90),  np.max(lengths), np.min(lengths), np.std(lengths), sep=',')
    count, bins_count = np.histogram(lengths, bins=10000)
    pdf_lengths = count / sum(count)
    cdf_lengths = np.cumsum(pdf_lengths)

    # idxs = np.nonzero(cdf_lengths < 0.99999)
    plt.figure(figsize=(6.4,3.2))
    plt.plot(bins_count[1:], cdf_lengths, "m-")
        
    plt.xlabel("GSL Length (km)", fontsize=18)
    plt.ylabel("CDF", fontsize=18)
    # plt.legend(fontsize=14, loc="lower right")
    plt.yticks([0, 0.2,0.4,0.6,0.8,1], fontsize=14)
    plt.xticks(fontsize=14)
    plt.xticks(fontsize=14)
    plt.grid(linewidth=0.5, linestyle=':')
    plt.tight_layout()

    base_file = "paper_plots/gslLengths"
    png_file = base_file + ".png"
    pdf_file = base_file + ".pdf"
    plt.savefig(png_file)
    plt.savefig(pdf_file)