import os, sys
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.ticker as tk
import numpy as np
from collections import OrderedDict
from matplotlib.ticker import FormatStrFormatter
from datetime import datetime
import csv
import scipy
import networkx as nx
sys.path.append("../../satgenpy")
from satgen import *

total_time = 200

def calculate_path_lengths(graphs, path):
    lengths = [0] * total_time

    for i in range(total_time):
        if nx.is_simple_path(graphs[i], path):
            lengths[i] = compute_path_length_with_graph(path, graphs[i])

    return lengths

def load_data(graphs):
    num_paths = 0
    path_dictionary = {}
    path_utilization = np.zeros((1,200))
    path_lengths = []

    dir = "paper_data/starlink_550_isls_plus_grid_ground_stations_newyork_london_1600_algorithm_free_one_only_over_isls/1000ms_for_200s/manual/data/"
    for file in os.listdir(dir):
        if file.startswith("networkx_path_"):
            f = dir + file
            with open(f) as csvfile:
                spamreader = csv.reader(csvfile, delimiter=',',quotechar='"',quoting=csv.QUOTE_ALL, skipinitialspace=True)

                prev_time = -1
                prev_path = ""
                for row in spamreader:
                    if prev_time == -1:
                        prev_time = int(int(row[0]) / 1000000000)
                        prev_path = row[1]
                        continue
                    
                    t = int(int(row[0]) / 1000000000)
                    path_time = t - prev_time
                    # print(prev_path, prev_time, t)
                    if prev_path in path_dictionary:
                        idx = path_dictionary[prev_path]
                        path_utilization[idx + 1][prev_time:t] += 1
                        # print(list(path_utilization[idx]))
                    else:
                        new_path = np.zeros((200,))
                        new_path[prev_time:t] += 1
                        # print(prev_time, t, list(new_path))
                        path_utilization = np.vstack([path_utilization, new_path])
                        # print(list(path_utilization[num_paths + 1]))
                        path = list(prev_path.split("-"))
                        path = [int(i) for i in path]
                        path.insert(0, 1584+1599)
                        path.append(1584+1599+1600)
                        path_lengths.append(calculate_path_lengths(graphs,path))
                        path_dictionary[prev_path] = num_paths
                        num_paths += 1

                    prev_time = t
                    prev_path = row[1]

    # print(num_paths)
    return path_dictionary, path_utilization[1:].astype(int), path_lengths

def get_linewidth(utilization):
    if utilization == 1600:
        return 16
    if utilization > 1500:
        return 10
    if utilization > 1400:
        return 6
    if utilization > 1200:
        return 3
    if utilization > 300:
        return 1
    if utilization > 100:
        return 0.5
    else:
        return 0


if __name__ == '__main__':
    graphs = [None] * total_time

    for i in range(total_time):
        graph_path = "graphs/starlink_550_isls_plus_grid_ground_stations_newyork_london_1600_algorithm_free_one_only_over_isls/1000ms/graph_" + str(i*1000*1000*1000) + ".txt"
        graphs[i] = nx.read_gpickle(graph_path)

    path_dictionary, path_utilization, path_lengths = load_data(graphs)
    # plt.plot(bins_count[1:], pdf, color="red", label="PDF")
    plt.ylabel("Length (km)")
    plt.xlabel("Time (seconds)")
    
    plt_colors = ["b-", "r-", "g-", "m-", "y-", "k-"]
    path_colors = ["b--", "r--", "g--", "m--", "y--", "k--"]
    i = 0
    print(path_dictionary)
    for path in path_lengths:
        x = np.arange(0, total_time)
        lengths = np.array(path)
        ids = np.nonzero(lengths)
        plt.plot(x[ids], lengths[ids] / 1000, path_colors[i])
        utilization = path_utilization[i]
        print(list(np.unique(utilization[np.nonzero(utilization)])))
        for t in range(200):
            if utilization[t] > 0:
                if lengths[t] == 0:
                    print(t, utilization[t], lengths[t], i)    
                    plt.plot([t, t+1], [lengths[t + 1] / 1000] * 2, plt_colors[i], linewidth=get_linewidth(utilization[t]))
                else:
                    plt.plot([t, t+1], [lengths[t] / 1000] * 2, plt_colors[i], linewidth=get_linewidth(utilization[t]))

            # elif utilization[t] * lengths[t] == 0:
            #     print(t, utilization[t], lengths[t], i)

        i += 1

    plt.grid()
            
    base_file = "path_utilization"
    png_file = base_file + ".png"
    pdf_file = base_file + ".pdf"
    plt.savefig(png_file)
    plt.savefig(pdf_file)