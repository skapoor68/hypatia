import os, sys
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.ticker as tk
import matplotlib.gridspec as gridspec
import numpy as np
from collections import OrderedDict
from matplotlib.ticker import FormatStrFormatter
from datetime import datetime
import csv
import scipy

configuration_line_numbers = {
    "starlink_8shells_isls_plus_grid_ground_stations_top_100_algorithm_free_one_only_over_isls":0,
    "starlink_4shells_isls_plus_grid_ground_stations_top_100_algorithm_free_one_only_over_isls":1,
    "starlink_2shells_isls_plus_grid_ground_stations_top_100_algorithm_free_one_only_over_isls":2,
    "starlink_different_8shells_isls_plus_grid_ground_stations_top_100_algorithm_free_one_only_over_isls":3,
    "starlink_different_4shells_isls_plus_grid_ground_stations_top_100_algorithm_free_one_only_over_isls":4,
    "starlink_different_2shells_isls_plus_grid_ground_stations_top_100_algorithm_free_one_only_over_isls":5,
    "starlink_current_5shells_isls_plus_grid_ground_stations_top_100_algorithm_free_one_only_over_isls":6,
    "starlink_older_5shells_isls_plus_grid_ground_stations_top_100_algorithm_free_one_only_over_isls":7,
    "starlink_550_72_66_isls_plus_grid_ground_stations_top_100_algorithm_free_one_only_over_isls":8,
    "starlink_550_isls_plus_grid_ground_stations_top_100_algorithm_free_one_only_over_isls":9
}

configurations = [ 
    [
    "starlink_8shells_isls_plus_grid_ground_stations_top_100_algorithm_free_one_only_over_isls",
    "starlink_4shells_isls_plus_grid_ground_stations_top_100_algorithm_free_one_only_over_isls",
    "starlink_2shells_isls_plus_grid_ground_stations_top_100_algorithm_free_one_only_over_isls",
    "starlink_550_isls_plus_grid_ground_stations_top_100_algorithm_free_one_only_over_isls"
    ],
    [
    "starlink_different_8shells_isls_plus_grid_ground_stations_top_100_algorithm_free_one_only_over_isls",
    "starlink_different_4shells_isls_plus_grid_ground_stations_top_100_algorithm_free_one_only_over_isls",
    "starlink_different_2shells_isls_plus_grid_ground_stations_top_100_algorithm_free_one_only_over_isls",
    "starlink_550_isls_plus_grid_ground_stations_top_100_algorithm_free_one_only_over_isls"
    ],
    [
    "starlink_current_5shells_isls_plus_grid_ground_stations_top_100_algorithm_free_one_only_over_isls",
    "starlink_older_5shells_isls_plus_grid_ground_stations_top_100_algorithm_free_one_only_over_isls",
    # "starlink_550_72_66_isls_plus_grid_ground_stations_top_100_algorithm_free_one_only_over_isls",
    "starlink_550_isls_plus_grid_ground_stations_top_100_algorithm_free_one_only_over_isls"
    ]    
]

names = {
    "starlink_current_5shells_isls_plus_grid_ground_stations_top_100_algorithm_free_one_only_over_isls":"Current Starlink",
    "starlink_older_5shells_isls_plus_grid_ground_stations_top_100_algorithm_free_one_only_over_isls":"Earlier Starlink",
    "starlink_different_8shells_isls_plus_grid_ground_stations_top_100_algorithm_free_one_only_over_isls":"8 Shells",
    "starlink_different_4shells_isls_plus_grid_ground_stations_top_100_algorithm_free_one_only_over_isls":"4 Shells",
    "starlink_different_2shells_isls_plus_grid_ground_stations_top_100_algorithm_free_one_only_over_isls":"2 Shells",
    "starlink_8shells_isls_plus_grid_ground_stations_top_100_algorithm_free_one_only_over_isls":"8 Shells",
    "starlink_4shells_isls_plus_grid_ground_stations_top_100_algorithm_free_one_only_over_isls":"4 Shells",
    "starlink_2shells_isls_plus_grid_ground_stations_top_100_algorithm_free_one_only_over_isls":"2 Shells",
    "starlink_550_72_66_isls_plus_grid_ground_stations_top_100_algorithm_free_one_only_over_isls":"72 orbits, 66 satellites",
    "starlink_550_isls_plus_grid_ground_stations_top_100_algorithm_free_one_only_over_isls":"First Shell"
}

def load_data(config, frequency, total_time):
    times = []
    dir = "paper_data/" + config + "/" + str(frequency) + "ms_for_" + str(total_time) + "s/manual/data/"
    # print(dir)
    for file in os.listdir(dir):
        if file.startswith("networkx_path_"):
            # print(file)
            f = dir + file
            with open(f) as csvfile:
                spamreader = csv.reader(csvfile, delimiter=',',quotechar='"',quoting=csv.QUOTE_ALL, skipinitialspace=True)

                id = 0
                prev_time = -1
                for row in spamreader:
                    # print(row)
                    if prev_time == -1:
                        prev_time = int(row[0]) / 1000000000
                        continue
                    
                    t = int(row[0]) / 1000000000
                    path_time = t - prev_time
                    times.append(path_time)

                    prev_time = t
                    id = id + 1

                times.append(int(total_time) - prev_time)

    return np.array(times)

def load():
    f = "shells_lifetimes.txt"
    data = np.array((len(names.keys()), 10000))
    with open(f) as csvfile:
        spamreader = list(csv.reader(csvfile, delimiter=',',quotechar='"',quoting=csv.QUOTE_ALL, skipinitialspace=True))
        for i in range(len(spamreader)):
            data[i] = np.array(spamreader[i])

    return data

if __name__ == '__main__':
    titles = ["Different Altitudes", "Different Inclination Angles", "Starlink Configurations"]
    config_num = int(sys.argv[1])
    # print("Name, Mean, 25th Percentile, Median, 75th Percentile, 90th Percentile, Max, Min, Std")
    plt_colors = ["b-", "r--", "g-.", "k:"]
    plt.figure(figsize=(6.4,3.2))
    data = np.genfromtxt("shells_lifetimes.txt", delimiter=",")
    bins = np.linspace(0,300,10000)
    plt.ylabel("CDF", fontsize=18)
    # for i in range(len(configurations)):
    #     ax[i].set_xlabel("Time (seconds)", fontsize=18)
    #     for j in range(len(configurations[i])):
    #         times = load_data(configurations[i][j], 1000, 600)
    #         count, bins_count = np.histogram(times, bins=bins)
    #         pdf_times = count / sum(count)
    #         cdf_times = np.cumsum(pdf_times)
    #         # print(list(cdf_times))
    #         idxs = np.nonzero(cdf_times < 0.99999)
    #         ax[i].plot(bins_count[idxs], cdf_times[idxs], plt_colors[j], label=names[configurations[i][j]])

    #     ax[i].legend()
    #     ax[i].grid(linewidth=0.5, linestyle=':')
    #     ax[i].set_title(titles[i], fontsize=18)
    #     ax[i].set_xticks(np.arange(0,300,50))
    #     ax[i].set_xticklabels(np.arange(0,350,50), fontsize=14)
    #     ax[i].set_yticks(np.linspace(0,1,6))
    #     ax[i].set_yticklabels(np.round(np.linspace(0,1,6), decimals=1), fontsize=14)
    
    plt.xlabel("Time (seconds)", fontsize=18)
    
    for j in range(len(configurations[config_num])):
        configuration_data = data[configuration_line_numbers[configurations[config_num][j]]]
        idxs = np.where((configuration_data < 0.99999) & (configuration_data > 0))
        plt.plot(bins[idxs], configuration_data[idxs], plt_colors[j], label=names[configurations[config_num][j]])

    plt.legend(fontsize=16, loc="lower right", frameon=False)
    plt.grid(linewidth=0.5, linestyle=':')
    # plt.xscale("log")
    # plt.xticks([10,20,40,80,160,320], labels=[10,20,40,80,160,320], fontsize=16)
    plt.xticks(fontsize=16)
    if config_num == 0:
        plt.arrow(50, 0.5, 60,0, width=0.3, head_width=0.5, head_length=20, fill=False, alpha=0.5)
        plt.annotate("Better", (70,0.45), alpha=0.5, fontsize=20)
    # plt.set_xticklabels(np.arange(0,300,50), fontsize=14)
    plt.yticks([0, 0.2,0.4,0.6,0.8,1], fontsize=16)
    # plt.set_yticklabels(np.round(np.linspace(0,1,11), decimals=1), fontsize=14)
    
    base_file = "paper_plots/shells_path_lifetimes_" + sys.argv[1]
    png_file = base_file + ".png"
    pdf_file = base_file + ".pdf"
    plt.tight_layout()
    plt.savefig(png_file)
    plt.savefig(pdf_file)