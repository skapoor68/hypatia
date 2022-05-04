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

def calculate_path_lengths(graphs, path):
    lengths = [0] * total_time
    start_time = 1200*1000*1000*1000
    end_time = 1400*1000*1000*1000
    for i in range(start_time, end_time, 1000*1000*1000):
        idx = (i // (1000*1000*1000)) - 1200
        if nx.is_simple_path(graphs[i], path):
            lengths[idx] = compute_path_length_with_graph(path, graphs[i]) * 2

    return lengths

def load_data(graphs):
    num_paths = 0
    path_dictionary = {}
    path_utilization = np.zeros((1,200))
    path_lengths = []
    latencies = []

    dir = "paper_data/starlink_550_isls_plus_grid_ground_stations_newyork_london_circular_algorithm_free_one_only_over_isls/1000ms_for_200s/manual/data/"
    for i in range(2001):
        src = 1584 + i
        dst = 1584 + i + 2001
        file = "networkx_path_" + str(src) + "_to_" + str(dst) + ".txt"
        f = dir + file
        with open(f) as csvfile:
            spamreader = csv.reader(csvfile, delimiter=',',quotechar='"',quoting=csv.QUOTE_ALL, skipinitialspace=True)

            prev_time = -1
            prev_path = ""
            for row in spamreader:
                if prev_time == -1:
                    prev_time = int(int(row[0]) / 1000000000) - 1200
                    prev_path = row[1]
                    continue
                
                t = int(int(row[0]) / 1000000000) - 1200
                path_time = t - prev_time
                # print(prev_path, prev_time, t)
                if prev_path in path_dictionary:
                    idx = path_dictionary[prev_path]
                    path_utilization[idx][prev_time:t] += 1
                    # print(idx, list(path_utilization[idx]))
                else:
                    if num_paths == 0:
                        path_utilization[0][prev_time:t] += 1
                        # print("new path", prev_time, t, list(path_utilization[0]))
                    else:
                        new_path = np.zeros((200,))
                        new_path[prev_time:t] += 1
                        # print(prev_time, t, list(new_path))
                        path_utilization = np.vstack([path_utilization, new_path])
                        # print(list(path_utilization[num_paths]))
                    path = list(prev_path.split("-"))
                    path = [int(i) for i in path]
                    path.insert(0, 1584+1599)
                    path.append(1584+1599+1600)
                    path_lengths.append(calculate_path_lengths(graphs,path))
                    path_dictionary[prev_path] = num_paths
                    num_paths += 1

                prev_time = t
                prev_path = row[1]

            if prev_path in path_dictionary:
                idx = path_dictionary[prev_path]
                path_utilization[idx][prev_time:] += 1
            else:
                new_path = np.zeros((200,))
                new_path[prev_time:t] += 1
                path_utilization = np.vstack([path_utilization, new_path])
                path = list(prev_path.split("-"))
                path = [int(i) for i in path]
                path.insert(0, 1584+1599)
                path.append(1584+1599+1600)
                path_lengths.append(calculate_path_lengths(graphs,path))
                path_dictionary[prev_path] = num_paths
                num_paths += 1

        
        file = "networkx_rtt_" + str(src) + "_to_" + str(dst) + ".txt"
        f = dir + file
        with open(f) as csvfile:
            latency = []
            spamreader = csv.reader(csvfile, delimiter=',',quotechar='"',quoting=csv.QUOTE_ALL, skipinitialspace=True)
            for row in spamreader:
                latency.append(float(row[1]))

            latency = np.array(latency)
            latencies.append(latency / 1000000)

    # print(num_paths)
    return path_dictionary, path_utilization.astype(int), path_lengths, np.array(latencies)

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
    graphs = {}
    start_time = 1200*1000*1000*1000
    end_time = 1400*1000*1000*1000
    for i in range(start_time, end_time, 1000*1000*1000):
        # idx = start_time + i*1000*1000*1000
        graph_path = "graphs/starlink_550_isls_plus_grid_ground_stations_newyork_london_circular_algorithm_free_one_only_over_isls/1000ms/graph_" + str(i) + ".txt"
        graphs[i] = nx.read_gpickle(graph_path)

    path_dictionary, path_utilization, path_lengths, latencies = load_data(graphs)
    # plt.plot(bins_count[1:], pdf, color="red", label="PDF")
    # fig, ax = plt.subplots()
    # ax.set_ylabel("RTT (ms)")
    # ax.set_xlabel("Time (seconds)")
    
    plt_colors = ["b", "r", "g", "m", "y", "k", "c"]
    path_colors = ["b--", "r--", "g--", "m--", "y--", "k--", "c--"]
    i = 0
    print(path_dictionary, path_utilization.shape)
    x = np.arange(0, total_time)
    deviations = np.linspace(-0.2,0.2,2001)
    for latency in latencies:
        plt.plot(x, latency + deviations[i], "grey", linewidth=3, alpha=0.5)
        i += 1

    i = 0
    for path in path_lengths:
        lengths = np.array(path)
        y = lengths * 1000.0 / 299792458.0
        ids = np.nonzero(lengths)
        plt.plot(x[ids], y[ids], path_colors[i])
        # utilization = path_utilization[i]
        # print(list(np.unique(utilization[np.nonzero(utilization)])))
        # points = np.array([x[ids], y[ids]]).T.reshape(-1, 1, 2)
        # segments = np.concatenate([points[:-1], points[1:]], axis=1)
        
        # lc = LineCollection(segments, linewidths=utilization[ids] / 200,color=plt_colors[i])
        # ax.add_collection(lc)
        
        # for t in range(200):
        #     if utilization[t] > 0:
        #         if lengths[t] == 0:
        #             print(t, utilization[t], lengths[t], i)    
        #             plt.plot([t, t+1], [lengths[t + 1]] * 2, plt_colors[i], linewidth=get_linewidth(utilization[t]))
        #         else:
        #             plt.plot([t, t+1], [lengths[t] * 1000.0 / 299792458.0] * 2, plt_colors[i], linewidth=get_linewidth(utilization[t]))

            # elif utilization[t] * lengths[t] == 0:
            #     print(t, utilization[t], lengths[t], i)

        i += 1

    
    plt.title("Utilization for the New York-London Route", fontsize=18)
    plt.xlabel("Time (seconds)", fontsize=18)
    plt.ylabel("RTT (ms)", fontsize=18)
    plt.yticks(fontsize=14)
    plt.xticks(fontsize=14)
    plt.grid(linewidth=0.5, linestyle=':')
    plt.tight_layout()
            
    base_file = "paper_plots/path_utilization"
    png_file = base_file + ".png"
    pdf_file = base_file + ".pdf"
    plt.savefig(png_file)
    plt.savefig(pdf_file)