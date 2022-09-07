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
    "starlink_550_isls_plus_grid_ground_stations_top_100_algorithm_free_one_only_over_isls":"Starlink S1"
}

def load_data(config, frequency, total_time):
    ratio = []
    dir = "paper_data/" + config + "/" + str(frequency) + "ms_for_" + str(total_time) + "s/manual/data/"
    for file in os.listdir(dir):
        if file.startswith("networkx_rtt_"):
            f = dir + file
            with open(f) as csvfile:
                spamreader = csv.reader(csvfile, delimiter=',',quotechar='"',quoting=csv.QUOTE_ALL, skipinitialspace=True)
                rtts = []
                for row in spamreader:
                    # print(row)
                    rtt = float(row[1])
                    if np.isnan(rtt) or rtt == 0:
                        print(f, row)
                        continue
                    rtts.append(rtt)
            
                rtts = np.array(rtts)
                # print(np.min(rtts), np.max(rtts))
                ratio.append(np.min(rtts) / np.max(rtts))
                # print(ratio[-1])

    return np.array(ratio)

if __name__ == '__main__':

    titles = ["Increasing Shells", "Different Inclination Angles", "Starlink Configurations"]
    # print("Name, Mean, 25th Percentile, Median, 75th Percentile, 90th Percentile, Max, Min, Std")
    plt_colors = ["b-", "r--", "g-.", "k:"]
    config_num = int(sys.argv[1])
    data = np.genfromtxt("shells_rtt_ratio.txt", delimiter=",")
    bins = np.linspace(0,1,10000)
    plt.figure(figsize=(6.4,3.2))
    plt.ylabel("CDF", fontsize=18)
    # for i in range(len(configurations)):
    #     ax[i].set_xlabel("Min RTT / Max RTT", fontsize=18)
    #     for j in range(len(configurations[i])):
    #         ratio = load_data(configurations[i][j], 1000, 600)
    #         # print(names[configurations[i][j]], np.mean(ratio), np.percentile(ratio, 25), np.median(ratio), np.percentile(ratio, 75), np.percentile(ratio, 90),  np.max(ratio), np.min(ratio), np.std(ratio), sep=',')
    #         count, bins_count = np.histogram(ratio, bins=bins)
    #         # print(bins, bins_count)
    #         pdf_ratio = count / sum(count)
    #         cdf_ratio = np.cumsum(pdf_ratio)
    #         # print(list(cdf_ratio))
    #         idxs = np.nonzero(cdf_ratio > 0)
    #         print(bins[idxs])
    #         ax[i].plot(bins[idxs], cdf_ratio[idxs], plt_colors[j], label=names[configurations[i][j]])

    #     ax[i].legend()
    #     ax[i].grid(linewidth=0.5, linestyle=':')
    #     ax[i].set_title(titles[i], fontsize=18)
    #     ax[i].set_xticks(np.linspace(0.3,1, 8))
    #     ax[i].set_xticklabels(np.round(np.linspace(0.3,1, 8), decimals=2), fontsize=14)
    #     ax[i].set_yticks(np.linspace(0,1,6))
    #     ax[i].set_yticklabels(np.round(np.linspace(0,1,6), decimals=1), fontsize=14)

    
    plt.xlabel("Min RTT / Max RTT", fontsize=18)
    for j in range(len(configurations[config_num])):
        configuration_ratio = data[configuration_line_numbers[configurations[config_num][j]]]
        idxs = np.nonzero(configuration_ratio > 0)
        # print(bins[idxs])
        plt.plot(bins[idxs], configuration_ratio[idxs], plt_colors[j], label=names[configurations[config_num][j]])

    plt.legend(fontsize=14, loc="upper left", frameon=False)
    plt.grid(linewidth=0.5, linestyle=':')
    # plt.set_title(titles[i], fontsize=18)
    plt.xticks(np.linspace(0.3,1,8), fontsize=16)
    # plt.set_xticklabels(np.round(np.linspace(0.3,1,8), decimals=2), fontsize=14)
    plt.yticks(np.linspace(0,1,6), fontsize=16)
    # plt.set_yticklabels(np.round(np.linspace(0,1,6), decimals=1), fontsize=14)
    if config_num == 0:
        plt.arrow(0.6, 0.5, 0.15,0, width=0.3, head_width=0.5, head_length=0.05, fill=False, alpha=0.5)
        plt.annotate("Better", (0.63,0.45), alpha=0.5, fontsize=20)


    # plt.plot(bins_count[1:], pdf, color="red", label="PDF")
    # plt.xlabel("Time(seconds)")
    
    plt.tight_layout()
    base_file = "paper_plots/shells_rtt_ratio_" + sys.argv[1]
    png_file = base_file + ".png"
    pdf_file = base_file + ".pdf"
    plt.savefig(png_file)
    plt.savefig(pdf_file)