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

dirs = [
    "paper_data/starlink_550_isls_plus_grid_ground_stations_top_100_algorithm_free_one_only_over_isls/1000ms_for_6000s/manual/data/",
    "paper_data/starlink_550_no_phase_isls_plus_grid_ground_stations_top_100_algorithm_free_one_only_over_isls/1000ms_for_6000s/manual/data/",
    "paper_data/starlink_550_half_phase_isls_plus_grid_ground_stations_top_100_algorithm_free_one_only_over_isls/1000ms_for_6000s/manual/data/",
    "paper_data/starlink_550_third_phase_isls_plus_grid_ground_stations_top_100_algorithm_free_one_only_over_isls/1000ms_for_6000s/manual/data/",
    "paper_data/starlink_550_fourth_phase_isls_plus_grid_ground_stations_top_100_algorithm_free_one_only_over_isls/1000ms_for_6000s/manual/data/",
    "paper_data/starlink_550_third_phase_variant_isls_plus_grid_ground_stations_top_100_algorithm_free_one_only_over_isls/1000ms_for_6000s/manual/data/",
    "paper_data/starlink_550_fourth_phase_variant_isls_plus_grid_ground_stations_top_100_algorithm_free_one_only_over_isls/1000ms_for_6000s/manual/data/",
]

def load_data(src, dst):
    paths = []
    rtts = {}
    latencies = []


    for dir in dirs:
        file = "networkx_rtt_" + str(src) + "_to_" + str(dst) + ".txt"
        f = dir + file
        latency = []
        with open(f) as csvfile:
            spamreader = csv.reader(csvfile, delimiter=',',quotechar='"',quoting=csv.QUOTE_ALL, skipinitialspace=True)

            for row in spamreader:
                t = int(int(row[0]) / 1000000000)
                if t >= 200:
                    break
                
                latency.append(float(row[1]) / 1000000)
                
        latencies.append(np.array(latency))

    return np.array(latencies)

if __name__ == '__main__':
    
    plt.ylabel("RTT (ms)", fontsize=18)
    plt.xlabel("Time (seconds)", fontsize=18)
    
    plt_colors = ["b-", "r-", "g-", "m-", "y-",  "c-", "b-", "r-", "g-", "m-", "y-", "c-","b-"]
    path_colors = ["b--", "r--", "g--", "m--", "y--",  "c--", "b--", "r--", "g--", "m--", "y--", "c--", "b--"]
    path_colors = ["brown",  "blue", "red", "darkorange", "cyan", "darkviolet", "chocolate", "gold", "fuchsia", "tan", "lawngreen", "", "turquoise", "teal", "tan"]
    # x = np.arange(0, total_time)

    latencies = load_data(1593,1611)
    median_latencies = np.median(latencies, axis=1)
    print(median_latencies)


    # print(list(latencies))
    # plt.plot(x[:200], latencies, "k-", linewidth=3, alpha=0.5)

    # data = np.genfromtxt("rtt_instance.txt", delimiter=",")
    # for i in range(data.shape[0] - 1):
    #     rtt = data[i]
    #     idxs = np.argwhere(rtt > 0)
    #     plt.plot(x[idxs], rtt[idxs], path_colors[i], linestyle='--')

    # latencies = data[-1]
    # plt.plot(x[:200], latencies[:200], "k-", linewidth=3, alpha=0.3)

    # # plt.legend(fontsize=14, loc="lower right")
    # plt.yticks(fontsize=14)
    # plt.xticks([0,25,50,75,100,125,150,175,200], fontsize=14)
    # plt.xticks(fontsize=14)
    # # plt.title("Frequent path switching for Jakarta to Bogotá", fontsize=18)
    # plt.grid(linewidth=0.5, linestyle=':')
    # plt.tight_layout()

            
    # base_file = "paper_plots/newyorkLondon"
    # png_file = base_file + ".png"
    # pdf_file = base_file + ".pdf"
    # plt.savefig(png_file)
    # plt.savefig(pdf_file)