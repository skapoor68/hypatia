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


configurations = [ 
    # "starlink_550_different_8shells_isls_plus_grid_ground_stations_top_100_algorithm_free_one_only_over_isls"
    # "starlink_550_different_4shells_isls_plus_grid_ground_stations_top_100_algorithm_free_one_only_over_isls",
    # "starlink_550_different_2shells_isls_plus_grid_ground_stations_top_100_algorithm_free_one_only_over_isls",
    # "starlink_550_8shells_isls_plus_grid_ground_stations_top_100_algorithm_free_one_only_over_isls",
    "starlink_550_4shells_isls_plus_grid_ground_stations_top_100_algorithm_free_one_only_over_isls",
    "starlink_550_2shells_isls_plus_grid_ground_stations_top_100_algorithm_free_one_only_over_isls",
    # "starlink_550_72_66_isls_plus_grid_ground_stations_top_100_algorithm_free_one_only_over_isls",
    "starlink_550_isls_plus_grid_ground_stations_top_100_algorithm_free_one_only_over_isls"
    ]

names = [
    # "different_8",
    # "different_4",
    # "different_2",
    # "same_8",
    "same_4",
    "same_2",
    # "72_66",
    "72_22"
]

def load_data(config, frequency, total_time):
    ratio = []
    dir = "data/" + config + "/" + str(frequency) + "ms_for_" + str(total_time) + "s/manual/data/"
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
                ratio.append(np.max(rtts) / np.min(rtts))

    return np.array(ratio)

if __name__ == '__main__':
    
    print("Name, Mean, 25th Percentile, Median, 75th Percentile, 90th Percentile, Max, Min, Std")
    plt_colors = ["b-", "r-", "g-", "c-", "m-", "y-", "k-", "b--", "r--", "g--", "c--", "m--", "y--", "k--", "b:", "r:", "g:", "c:", "m:", "y:", "k:", "b-.", "r-.", "g-.", "c-.", "m-.", "y-.", "k-."]
    for i in range(len(configurations)):
        ratio = load_data(configurations[i], 1000, 200)
        print(names[i], np.mean(ratio), np.percentile(ratio, 25), np.median(ratio), np.percentile(ratio, 75), np.percentile(ratio, 90),  np.max(ratio), np.min(ratio), np.std(ratio), sep=',')
        count, bins_count = np.histogram(ratio, bins=50)
        pdf_ratio = count / sum(count)
        cdf_ratio = np.cumsum(pdf_ratio)
        plt.plot(bins_count[1:], cdf_ratio, plt_colors[i], label=names[i])


    # plt.plot(bins_count[1:], pdf, color="red", label="PDF")
    plt.xlabel("Time(seconds)")
    plt.ylabel("Probability")
    
    plt.legend()
    base_file = "shells_rtt_ratio"
    png_file = base_file + ".png"
    pdf_file = base_file + ".pdf"
    plt.savefig(png_file)
    plt.savefig(pdf_file)