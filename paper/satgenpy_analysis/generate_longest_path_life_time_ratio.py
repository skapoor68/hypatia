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

constellations  = [
    "kuiper_630_isls_plus_grid_ground_stations_top_100_algorithm_free_one_only_over_isls",
    "starlink_550_isls_plus_grid_ground_stations_top_100_algorithm_free_one_only_over_isls",
    "telesat_1015_isls_plus_grid_ground_stations_top_100_algorithm_free_one_only_over_isls"
]

nice_name = {
    "kuiper_630_isls_plus_grid_ground_stations_top_100_algorithm_free_one_only_over_isls" : "Kuiper 630",
    "starlink_550_isls_plus_grid_ground_stations_top_100_algorithm_free_one_only_over_isls" : "Starlink 550",
    "telesat_1015_isls_plus_grid_ground_stations_top_100_algorithm_free_one_only_over_isls": "Telesat 1015"
}

file_name = {
    "kuiper_630_isls_plus_grid_ground_stations_top_100_algorithm_free_one_only_over_isls" : "kuiper",
    "starlink_550_isls_plus_grid_ground_stations_top_100_algorithm_free_one_only_over_isls" : "starlink",
    "telesat_1015_isls_plus_grid_ground_stations_top_100_algorithm_free_one_only_over_isls": "telesat"
}

patterns = {
    "kuiper_630_isls_plus_grid_ground_stations_top_100_algorithm_free_one_only_over_isls" : "r--",
    "starlink_550_isls_plus_grid_ground_stations_top_100_algorithm_free_one_only_over_isls" : "b-",
    "telesat_1015_isls_plus_grid_ground_stations_top_100_algorithm_free_one_only_over_isls": "g-."
}

gs_labels = {
    "kuiper_630_isls_plus_grid_ground_stations_top_100_algorithm_free_one_only_over_isls" : [1156,1256],
    "starlink_550_isls_plus_grid_ground_stations_top_100_algorithm_free_one_only_over_isls" : [1584,1684],
    "telesat_1015_isls_plus_grid_ground_stations_top_100_algorithm_free_one_only_over_isls": [351,451]
}

total_times = {
    "kuiper_630_isls_plus_grid_ground_stations_top_100_algorithm_free_one_only_over_isls" : 6000,
    "starlink_550_isls_plus_grid_ground_stations_top_100_algorithm_free_one_only_over_isls" : 6000,
    "telesat_1015_isls_plus_grid_ground_stations_top_100_algorithm_free_one_only_over_isls": 6600
}

constellation_line_numbers = {"kuiper_630_isls_plus_grid_ground_stations_top_100_algorithm_free_one_only_over_isls" : 0,
    "starlink_550_isls_plus_grid_ground_stations_top_100_algorithm_free_one_only_over_isls" : 1,
    "telesat_1015_isls_plus_grid_ground_stations_top_100_algorithm_free_one_only_over_isls": 2
    }

def calculate_path_life(constellation, lengths, t):
    return (lengths > 0).sum()
    start = t

    while(start >= 0):
        if lengths[start] == -1:
            break
        
        start -= 1

    end = t
    while(end < total_times[constellation]):
        if lengths[end] == -1:
            break

        end += 1

    return end - start + 1

def load_data(constellation):
    ratio = []
    dir = "paper_data/" + constellation + "/1000ms_for_" + str(total_times[constellation]) + "s/manual/data/"

    for src in range(gs_labels[constellation][0], gs_labels[constellation][1]):
        for dst in range(src + 1, gs_labels[constellation][1]):
            # print(src, dst)
            path_lengths = {}
            path_in_use_times = {}
            path_life_times = {}
            latencies = np.genfromtxt(dir + "networkx_rtt_" + str(src) + "_to_" + str(dst) + ".txt", delimiter=",")
            largest_rtt_time = latencies[np.argmax(latencies[:,1])][0] // 1000000000

            # print("largest_rtt_time", largest_rtt_time)

            longest_path = None
            longest_path_use_time = -1
            f = dir + "networkx_path_" + str(src) + "_to_" + str(dst) + ".txt"
            with open(f) as csvfile:
                spamreader = csv.reader(csvfile, delimiter=',',quotechar='"',quoting=csv.QUOTE_ALL, skipinitialspace=True)
                prev_path = None
                prev_time = -1
                for row in spamreader:
                    if prev_path == None:
                        prev_time = int(row[0])
                        prev_path = row[1]
                        continue

                    t = int(row[0]) // 1000000000
                    if t >= largest_rtt_time:
                        longest_path = prev_path
                        longest_path_use_time = t - prev_time
                        break

                    prev_time = t
                    prev_path = row[1]

                if longest_path_use_time == -1:
                    longest_path = prev_path
                    longest_path_use_time = total_times[constellation] - prev_time

            # print("longest_path",longest_path)
            # print("longest_path_use_time", longest_path_use_time)
                    
            f = dir + "networkx_life_of_path_" + str(src) + "_to_" + str(dst) + ".txt"
            with open(f) as csvfile:
                spamreader = csv.reader(csvfile, delimiter=',',quotechar='"',quoting=csv.QUOTE_ALL, skipinitialspace=True)
                for row in spamreader:
                    if row[0] == longest_path:
                        lengths = row[3].split("_")
                        lengths = np.array([float(x) for x in lengths])
                        longest_path_life_time = (lengths > 0).sum()

                        ratio.append(longest_path_life_time/longest_path_use_time)
                        # print(ratio[-1])
                        break
                
            

    # print(ratio)
    return np.array(ratio)

if __name__ == '__main__':

    bins = np.linspace(0.9,1500,15000)
    # for constellation in constellations:
    #     ratio = load_data(constellation)
    #     # print(ratio.shape, ratio)
        
    #     # print("Mean, 25th Percentile, Median, 75th Percentile, 90th Percentile, Max, Min, Std")
    #     # print(np.mean(ratio), np.percentile(ratio, 25), np.median(ratio), np.percentile(ratio, 75), np.percentile(ratio, 90),  np.max(ratio), np.min(ratio), np.std(ratio), sep=',')
    #     count, bins_count = np.histogram(ratio, bins=bins)
    #     pdf_ratio = count / sum(count)
    #     cdf_ratio = np.cumsum(pdf_ratio)
    #     print(list(cdf_ratio))
    #     idxs = np.nonzero(cdf_ratio < 0.99999)
    #     plt.plot(bins[idxs], cdf_ratio[idxs], patterns[constellation], label=nice_name[constellation])

    data = np.genfromtxt("longest_path_lifetimes.txt", delimiter=",")
    plt.figure(figsize=(6.4,3.2))
    for constellation in constellations:
        cdf_ratio = data[constellation_line_numbers[constellation]]
        
        idxs = np.nonzero(cdf_ratio < 0.99999)
        plt.plot(bins[idxs], cdf_ratio[idxs], patterns[constellation], label=nice_name[constellation])


    plt.xlabel("Ratio of Path Lifetime to Usability Time", fontsize=18)
    plt.ylabel("CDF", fontsize=18)
    plt.legend(fontsize=14, loc="lower right", frameon=False)
    plt.yticks([0,0.1, 0.2, 0.3,0.4,0.5,0.6,0.7,0.8,0.9,1], fontsize=14)
    plt.xscale("log")
    plt.xticks([1,2,4,8,16,32,64,128,256,512,1500],labels=[1,2,4,8,16,32,64,128,256,512,1500],fontsize=14)
    plt.grid(linewidth=0.5, linestyle=':')
    plt.tight_layout()

    base_file = "paper_plots/longestPathLifeRatio"
    png_file = base_file + ".png"
    pdf_file = base_file + ".pdf"
    plt.savefig(png_file)
    plt.savefig(pdf_file)