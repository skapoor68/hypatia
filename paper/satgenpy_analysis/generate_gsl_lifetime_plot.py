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

def load_data(src=1584):
    ratio = []
    dir = "graphs/starlink_550_isls_plus_grid_ground_stations_top_100_algorithm_free_one_only_over_isls/1000ms/"
    total_time = 6000
    nodes = list(range(1584))
    nodes.append(src)
    graphs = {}
    lifetimes = []
    gsl_times = {}
    for tt in range(total_time):
        graph_path = dir + "graph_" + str(tt * 1000*1000*1000) + ".txt"
        graph = nx.read_gpickle(graph_path).subgraph(nodes)
        print(len(list(graph[src].keys())))
        for nbr in graph[src].keys():
            if nbr in gsl_times:
                gsl_times[nbr].append(tt)
            else:
                gsl_times[nbr] = [tt]

        sats_not_in_range = []
        for sat in gsl_times.keys():
            if gsl_times[sat][-1] != tt:
                sats_not_in_range.append(sat)

        for i in range(len(sats_not_in_range)):
            lifetimes.append(len(gsl_times[sats_not_in_range[i]]))
            del gsl_times[sats_not_in_range[i]]
            
    return np.array(lifetimes)

if __name__ == '__main__':

    lifetimes = load_data()
        
    print("Mean, 25th Percentile, Median, 75th Percentile, 90th Percentile, Max, Min, Std")
    print(np.mean(lifetimes), np.percentile(lifetimes, 25), np.median(lifetimes), np.percentile(lifetimes, 75), np.percentile(lifetimes, 90),  np.max(lifetimes), np.min(lifetimes), np.std(lifetimes), sep=',')
    count, bins_count = np.histogram(lifetimes, bins=1000000)
    pdf_lifetimes = count / sum(count)
    cdf_lifetimes = np.cumsum(pdf_lifetimes)

    plt.figure(figsize=(6.4,3.2))
    idxs = np.nonzero(cdf_lifetimes < 0.99999)
    plt.plot(bins_count[idxs], cdf_lifetimes[idxs], "b-")
        
    plt.xlabel("GSL Lifetime (seconds)", fontsize=18)
    plt.ylabel("CDF", fontsize=18)
    # plt.legend(fontsize=14, loc="lower right")
    plt.yticks([0, 0.2,0.4,0.6,0.8,1], fontsize=14)
    plt.xticks(fontsize=14)
    plt.xticks(fontsize=14)
    plt.grid(linewidth=0.5, linestyle=':')
    plt.tight_layout()

    base_file = "paper_plots/gslLifetimes"
    png_file = base_file + ".png"
    pdf_file = base_file + ".pdf"
    plt.savefig(png_file)
    plt.savefig(pdf_file)