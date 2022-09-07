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

total_time = 201

def calculate_path_lengths(graphs, path):
    lengths = [0] * total_time

    for i in range(total_time):
        if nx.is_simple_path(graphs[i], path):
            lengths[i] = compute_path_length_with_graph(path, graphs[i])

    return lengths

def load_data(src, dst):
    paths = []
    rtts = {}
    latencies = []

    dir = "paper_data/starlink_550_isls_plus_grid_ground_stations_top_100_algorithm_free_one_only_over_isls/1000ms_for_6000s/manual/data/"
    greedy_dir = "paper_data/starlink_550_isls_plus_grid_ground_stations_top_100_algorithm_free_one_only_over_isls/greedy_1000ms_for_6000s/manual/data/"
    file = "networkx_path_0.2_" + str(src) + "_to_" + str(dst) + ".txt"
    f = greedy_dir + file
    with open(f) as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',',quotechar='"',quoting=csv.QUOTE_ALL, skipinitialspace=True)

        for row in spamreader:
            t = int(int(row[0]) / 1000000000)
            if t >= 200:
                break
            paths.append(row[1])
            
    file = "networkx_life_of_path_" + str(src) + "_to_" + str(dst) + ".txt"
    f = dir + file
    with open(f) as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',',quotechar='"',quoting=csv.QUOTE_ALL, skipinitialspace=True)

        for row in spamreader:
            if row[0] in paths:
                lengths = row[3].split("_")
                lengths = np.array([float(x) for x in lengths])
                # lengths = lengths * 1000.0 / 299792458.0
                rtts[row[0]] = lengths[:201] / 1000000

    file = "networkx_rtt_" + str(src) + "_to_" + str(dst) + ".txt"
    f = greedy_dir + file
    with open(f) as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',',quotechar='"',quoting=csv.QUOTE_ALL, skipinitialspace=True)

        for row in spamreader:
            t = int(int(row[0]) / 1000000000)
            if t >= 200:
                break
            latency = float(row[1]) / 1000000
            latencies.append(latency)

    return paths, rtts, latencies

def get_linewidth(utilization):
    return 1


if __name__ == '__main__':
    
    plt.ylabel("RTT (ms)", fontsize=18)
    plt.xlabel("Time (seconds)", fontsize=18)
    
    plt_colors = ["b-", "r-", "g-", "m-", "y-",  "c-", "b-", "r-", "g-", "m-", "y-", "c-","b-"]
    path_colors = ["b--", "r--", "g--", "m--", "y--",  "c--", "b--", "r--", "g--", "m--", "y--", "c--", "b--"]
    x = np.arange(0, total_time)

    paths, rtts, latencies = load_data(1610,1616)
    for i in range(len(paths)):
        rtt = rtts[paths[i]]
        # print(list(rtts[paths[i]]))
        idxs = np.argwhere(rtt > 0)
        plt.plot(x[idxs], rtt[idxs], path_colors[i])

    # print(list(latencies))
    plt.plot(x[:200], latencies, "k-", linewidth=3, alpha=0.5)

    # data = np.genfromtxt("rtt_instance.txt", delimiter=",")
    # for i in range(data.shape[0] - 1):
    #     rtt = data[i]
    #     idxs = np.argwhere(rtt > 0)
    #     plt.plot(x[idxs], rtt[idxs], path_colors[i])

    # latencies = data[-1]
    # plt.plot(x[:200], latencies[:200], "k-", linewidth=3, alpha=0.5)

    # plt.legend(fontsize=14, loc="lower right")
    plt.yticks(fontsize=14)
    plt.xticks([0,25,50,75,100,125,150,175,200], fontsize=14)
    plt.xticks(fontsize=14)
    # plt.title("Frequent path switching for Jakarta to Bogotá", fontsize=18)
    plt.grid(linewidth=0.5, linestyle=':')
    plt.tight_layout()

            
    base_file = "paper_plots/greedyJakartaBogota"
    png_file = base_file + ".png"
    pdf_file = base_file + ".pdf"
    plt.savefig(png_file)
    plt.savefig(pdf_file)