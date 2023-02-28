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

mapping = {}

def load_data(src=1584):
    # ratio = []
    variation_rtts = []
    basic_rtts = []
    counter = 0
    dir_variation = "paper_data/starlink_550_isls_plus_grid_ground_stations_top_100_algorithm_free_one_only_over_isls/1000ms_for_6000s/manual/data/"
    dir_basic = "paper_data/starlink_550_half_phase_isls_plus_grid_ground_stations_top_100_algorithm_free_one_only_over_isls/1000ms_for_6000s/manual/data/"
    for i in range(1584, 1684):
        for j in range(i + 1, 1684):
            # if i == 1605 or j == 1605 or i == 1657 or j == 1657:
            #     continue
            variation_file = dir_variation + "networkx_rtt_" + str(i) + "_to_" + str(j) + ".txt"
            basic_file = dir_basic + "networkx_rtt_" + str(i) + "_to_" + str(j) + ".txt"

            variation_times = np.genfromtxt(variation_file, delimiter=",") [:, 1]
            basic_times = np.genfromtxt(basic_file, delimiter=",")[:, 1]
            variation_rtts.append(np.max(variation_times) / np.min(variation_times))
            basic_rtts.append(np.max(basic_times) / np.min(basic_times))
            # ratio.append(variation_times / basic_times)
            # mapping[counter] = (i, j)
            # counter += 1
    return np.array(variation_rtts), np.array(basic_rtts)

# if __name__ == '__main__':

#     ratios = load_data()
#     ratio = np.min(ratios, axis=1)
        
#     print("Mean, 25th Percentile, Median, 75th Percentile, 90th Percentile, Max, Min, Std")
#     print(np.mean(ratio), np.percentile(ratio, 25), np.median(ratio), np.percentile(ratio, 75), np.percentile(ratio, 90),  np.max(ratio), np.min(ratio), np.std(ratio), sep=',')
#     count, bins_count = np.histogram(ratio, bins=1000000)
#     pdf_ratio = count / sum(count)
#     cdf_ratio = np.cumsum(pdf_ratio)

#     plt.figure(figsize=(6.4,3.2))
#     idxs = np.nonzero(cdf_ratio < 0.99999)
#     plt.plot(bins_count[idxs], cdf_ratio[idxs], "b-")
        
#     plt.xlabel("Ratio of RTTs", fontsize=18)
#     plt.ylabel("CDF", fontsize=18)
#     # plt.legend(fontsize=14, loc="lower right")
#     plt.yticks([0, 0.2,0.4,0.6,0.8,1], fontsize=14)
#     plt.xticks(fontsize=14)
#     plt.xticks(fontsize=14)
#     plt.grid(linewidth=0.5, linestyle=':')
#     plt.tight_layout()

#     base_file = "paper_plots/rtt_ratio_mins"
#     png_file = base_file + ".png"
#     pdf_file = base_file + ".pdf"
#     plt.savefig(png_file)
#     plt.savefig(pdf_file)

#     min_ratios = np.min(ratios, axis=1)
#     max_ratios = np.max(ratios, axis=1)

#     # print(np.argmin(min_ratios), np.argmax(max_ratios))
#     # print(mapping[np.argmin(min_ratios)], mapping[np.argmax(max_ratios)])


if __name__ == '__main__':

    variation, basic = load_data()
    
        
    print("Mean, 25th Percentile, Median, 75th Percentile, 90th Percentile, Max, Min, Std")
    print(np.mean(variation), np.percentile(variation, 25), np.median(variation), np.percentile(variation, 75), np.percentile(variation, 90),  np.max(variation), np.min(variation), np.std(variation), sep=',')
    count, bins_count = np.histogram(variation, bins=1000000)
    pdf_variation = count / sum(count)
    cdf_variation = np.cumsum(pdf_variation)

    plt.figure(figsize=(6.4,3.2))
    idxs = np.nonzero(cdf_variation < 0.99999)
    plt.plot(bins_count[idxs], cdf_variation[idxs], "b-", label = "+Grid Variation")

    print(np.mean(basic), np.percentile(basic, 25), np.median(basic), np.percentile(basic, 75), np.percentile(basic, 90),  np.max(basic), np.min(basic), np.std(basic), sep=',')
    count, bins_count = np.histogram(basic, bins=1000000)
    pdf_basic = count / sum(count)
    cdf_basic = np.cumsum(pdf_basic)

    idxs = np.nonzero(cdf_basic < 0.99999)
    plt.plot(bins_count[idxs], cdf_basic[idxs], "r--", label = "NN +Grid")
        
    plt.xlabel("Ratio of RTTs", fontsize=18)
    plt.ylabel("CDF", fontsize=18)
    plt.legend(fontsize=14, loc="lower right", frameon=False)
    plt.yticks([0, 0.2,0.4,0.6,0.8,1], fontsize=14)
    plt.xticks(fontsize=14)
    plt.xticks(fontsize=14)
    plt.grid(linewidth=0.5, linestyle=':')
    plt.tight_layout()

    base_file = "paper_plots/isl_config_rtt_variation"
    png_file = base_file + ".png"
    pdf_file = base_file + ".pdf"
    plt.savefig(png_file)
    plt.savefig(pdf_file)

    # min_ratios = np.min(ratios, axis=1)
    # max_ratios = np.max(ratios, axis=1)

    # print(np.argmin(min_ratios), np.argmax(max_ratios))
    # print(mapping[np.argmin(min_ratios)], mapping[np.argmax(max_ratios)])
