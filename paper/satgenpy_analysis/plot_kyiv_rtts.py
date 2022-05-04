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
    times = []
    latencies = []

    dir = "paper_data/starlink_550_isls_plus_grid_ground_stations_kyiv_algorithm_free_one_only_over_isls/1000ms_for_200s/manual/data/"
    file = "networkx_path_" + str(src) + "_to_" + str(dst) + ".txt"
    f = dir + file
    with open(f) as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',',quotechar='"',quoting=csv.QUOTE_ALL, skipinitialspace=True)

        for row in spamreader:
            t = int(int(row[0]) / 1000000000)
            if t >= 200:
                break
            times.append(t)

    file = "networkx_rtt_" + str(src) + "_to_" + str(dst) + ".txt"
    f = dir + file
    with open(f) as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',',quotechar='"',quoting=csv.QUOTE_ALL, skipinitialspace=True)

        for row in spamreader:
            t = int(int(row[0]) / 1000000000)
            if t >= 200:
                break
            latency = float(row[1]) / 1000000
            latencies.append(latency)

    return times, latencies

def get_linewidth(utilization):
    return 1


if __name__ == '__main__':
    times, latencies = load_data(1584,1585)
    print(times)
    x = np.arange(0, total_time)
    plt.plot(x[:200], latencies, "b-D", markevery=list(times[1:]), label="Kyiv-Cairo")

    times, latencies = load_data(1584,1588)
    print(times)
    plt.plot(x[:200], latencies, "--r*", markevery=list(times[1:]), label="Kyiv-Delhi")
    # times.append(200)
    # plt.plot(bins_count[1:], pdf, color="red", label="PDF")
    plt.ylabel("RTT (ms)")
    plt.xlabel("Time (seconds)")
    
    plt_colors = ["b-", "r-", "g-", "m-", "y-",  "c-", "b-", "r-", "g-", "m-", "y-", "c-","b-"]
    path_colors = ["b--", "r--", "g--", "m--", "y--",  "c--", "b--", "r--", "g--", "m--", "y--", "c--", "b--"]
    

    
    plt.legend(fontsize=14, loc="lower right")
    plt.yticks(fontsize=14)
    plt.xticks([0,25,50,75,100,125,150,175,200], fontsize=14)
    plt.xticks(fontsize=14)
    plt.title("RTTs for paths originating from Kyiv", fontsize=18)
    plt.grid(linewidth=0.5, linestyle=':')
    plt.tight_layout()

            
    base_file = "paper_plots/kyivInstances"
    png_file = base_file + ".png"
    pdf_file = base_file + ".pdf"
    plt.savefig(png_file)
    plt.savefig(pdf_file)