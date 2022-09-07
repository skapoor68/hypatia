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

constellation_line_numbers = {
    "kuiper_630_isls_plus_grid_ground_stations_top_100_algorithm_free_one_only_over_isls" : 0,
    "starlink_550_isls_plus_grid_ground_stations_top_100_algorithm_free_one_only_over_isls" : 1,
    "telesat_1015_isls_plus_grid_ground_stations_top_100_algorithm_free_one_only_over_isls": 2
}

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
            path_lengths = {}
            path_in_use_times = {}
            path_life_times = {}
            f = dir + "networkx_life_of_path_" + str(src) + "_to_" + str(dst) + ".txt"
            with open(f) as csvfile:
                spamreader = csv.reader(csvfile, delimiter=',',quotechar='"',quoting=csv.QUOTE_ALL, skipinitialspace=True)
                for row in spamreader:
                    lengths = row[3].split("_")
                    lengths = np.array([float(x) for x in lengths])
                    path_lengths[row[0]] = lengths
                    path_in_use_times[row[0]] = int(float(row[1]))
                    if path_in_use_times[row[0]] < 0:
                        path_in_use_times[row[0]] = path_in_use_times[row[0]] + 600
                
            f = dir + "networkx_path_" + str(src) + "_to_" + str(dst) + ".txt"
            with open(f) as csvfile:
                spamreader = csv.reader(csvfile, delimiter=',',quotechar='"',quoting=csv.QUOTE_ALL, skipinitialspace=True)
                for row in spamreader:
                    # print(row)
                    t = int(row[0]) // 1000000000
                    if row[1] == "Unreachable":
                        continue
                    path_life = calculate_path_life(constellation, path_lengths[row[1]], t)
                    if row[1] in path_life_times:
                        if path_life_times[row[1]] != path_life:
                            path_life_times[row[1]] += path_life
                    else:
                        path_life_times[row[1]] = path_life

            for path in path_life_times:
                if path_life_times[path] >= path_in_use_times[path]:
                    ratio.append(path_life_times[path] / path_in_use_times[path])
                    # if ratio[-1] > 50:
                    #     print(path, ratio[-1])
                else:
                    print(constellation, src, dst, path, path_life_times[path], path_in_use_times[path])

    # print(ratio)
    return np.array(ratio)

if __name__ == '__main__':

    bins = np.linspace(1,2048,21000)
    # for constellation in constellations:
    #     ratio = load_data(constellation)
        
    #     # print("Mean, 25th Percentile, Median, 75th Percentile, 90th Percentile, Max, Min, Std")
    #     # print(np.mean(ratio), np.percentile(ratio, 25), np.median(ratio), np.percentile(ratio, 75), np.percentile(ratio, 90),  np.max(ratio), np.min(ratio), np.std(ratio), sep=',')
    #     count, bins_count = np.histogram(ratio, bins=bins)
    #     pdf_ratio = count / sum(count)
    #     cdf_ratio = np.cumsum(pdf_ratio)
    #     print(list(cdf_ratio))
    #     idxs = np.nonzero(cdf_ratio < 0.99999)
    #     plt.plot(bins_count[idxs], cdf_ratio[idxs], patterns[constellation], label=nice_name[constellation])

    data = np.genfromtxt("path_life_ratio.txt", delimiter=",")
    for constellation in constellations:
        cdf_ratio = data[constellation_line_numbers[constellation]]
        print(cdf_ratio, cdf_ratio<0.99999)
        idxs = np.nonzero(cdf_ratio < 0.99999)
        print(idxs)
        plt.plot(bins[idxs], cdf_ratio[idxs], patterns[constellation], label=nice_name[constellation])


    plt.xlabel("Ratio of Path Lifetime to Usability Time", fontsize=18)
    plt.ylabel("CDF", fontsize=18)
    plt.legend(fontsize=14, loc="lower right", frameon=False)
    plt.yticks([0, 0.2,0.4,0.6,0.8,1], fontsize=14)
    plt.xscale("log")
    plt.xticks([1,2,4,8,16,32,64,128,256,512,1024,2048], labels=[1,2,4,8,16,32,64,128,256,512,1024,2048], fontsize=13.5)
    plt.grid(linewidth=0.5, linestyle=':')
    plt.tight_layout()

    base_file = "paper_plots/pathLifeRatio"
    png_file = base_file + ".png"
    pdf_file = base_file + ".pdf"
    plt.savefig(png_file)
    plt.savefig(pdf_file)