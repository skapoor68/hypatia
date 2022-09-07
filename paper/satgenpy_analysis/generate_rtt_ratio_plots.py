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

def load_data(constellation, total_time):
    ratio = []
    dir = "paper_data/" + constellation + "/1000ms_for_" + str(total_time) + "s/manual/data/"
    max_ratio = 0
    max_file = None
    for file in os.listdir(dir):
        if file.startswith("networkx_rtt_"):
            # print(file)
            f = dir + file
            with open(f) as csvfile:
                spamreader = csv.reader(csvfile, delimiter=',',quotechar='"',quoting=csv.QUOTE_ALL, skipinitialspace=True)
                rtts = []
                i = 0
                for row in spamreader:
                    # print(row)
                    i = i + 1
                    rtts.append(float(row[1]))
                    # if i == 200:
                    #     break

                rtts = np.array(rtts)
                rtts = rtts[np.nonzero(rtts)]
                ratio.append(np.amin(rtts) / np.amax(rtts))
                if ratio[-1] > max_ratio:
                    max_ratio = ratio[-1]
                    max_file = file

    # print(ratio)
    # print(max_ratio, max_file)
    # exit(0)
    return np.array(ratio)

if __name__ == '__main__':
    constellations  = [
        "kuiper_630_isls_plus_grid_ground_stations_top_100_algorithm_free_one_only_over_isls",
        "starlink_550_isls_plus_grid_ground_stations_top_100_algorithm_free_one_only_over_isls",
        "telesat_1015_isls_plus_grid_ground_stations_top_100_algorithm_free_one_only_over_isls"
    ]

    constellation_line_numbers = {"kuiper_630_isls_plus_grid_ground_stations_top_100_algorithm_free_one_only_over_isls" : 0,
    "starlink_550_isls_plus_grid_ground_stations_top_100_algorithm_free_one_only_over_isls" : 1,
    "telesat_1015_isls_plus_grid_ground_stations_top_100_algorithm_free_one_only_over_isls": 2
    }

    nice_name = {"kuiper_630_isls_plus_grid_ground_stations_top_100_algorithm_free_one_only_over_isls" : "Kuiper 630",
    "starlink_550_isls_plus_grid_ground_stations_top_100_algorithm_free_one_only_over_isls" : "Starlink 550",
    "telesat_1015_isls_plus_grid_ground_stations_top_100_algorithm_free_one_only_over_isls": "Telesat 1015"
    }

    file_name = {"kuiper_630_isls_plus_grid_ground_stations_top_100_algorithm_free_one_only_over_isls" : "kuiper",
    "starlink_550_isls_plus_grid_ground_stations_top_100_algorithm_free_one_only_over_isls" : "starlink",
    "telesat_1015_isls_plus_grid_ground_stations_top_100_algorithm_free_one_only_over_isls": "telesat"
    }

    patterns = {"kuiper_630_isls_plus_grid_ground_stations_top_100_algorithm_free_one_only_over_isls" : "r--",
    "starlink_550_isls_plus_grid_ground_stations_top_100_algorithm_free_one_only_over_isls" : "b-",
    "telesat_1015_isls_plus_grid_ground_stations_top_100_algorithm_free_one_only_over_isls": "g-."
    }

    total_time = {"kuiper_630_isls_plus_grid_ground_stations_top_100_algorithm_free_one_only_over_isls" : 6000,
    "starlink_550_isls_plus_grid_ground_stations_top_100_algorithm_free_one_only_over_isls" : 6000,
    "telesat_1015_isls_plus_grid_ground_stations_top_100_algorithm_free_one_only_over_isls": 6600
    }

    # for constellation in constellations:
    #     ratio = load_data(constellation, total_time[constellation])
        
    #     # print("Mean, 25th Percentile, Median, 75th Percentile, 90th Percentile, Max, Min, Std")
    #     # print(np.mean(ratio), np.percentile(ratio, 25), np.median(ratio), np.percentile(ratio, 75), np.percentile(ratio, 90),  np.max(ratio), np.min(ratio), np.std(ratio), sep=',')
    #     count, bins_count = np.histogram(ratio, bins=np.linspace(0,1,1000))
    #     pdf_ratio = count / sum(count)
    #     cdf_ratio = np.cumsum(pdf_ratio)
    #     print(list(cdf_ratio))
    #     idxs = np.nonzero(cdf_ratio > 0.00001)
    #     plt.plot(bins_count[idxs], cdf_ratio[idxs], patterns[constellation], label=nice_name[constellation])

    data = np.genfromtxt("rtt_variations.txt", delimiter=",")
    bins=np.linspace(0,1,1000)
    plt.figure(figsize=(6.4,3.2))
    for constellation in constellations:
        cdf_ratio = data[constellation_line_numbers[constellation]]
        # print(list(cdf_ratio))
        idxs = np.nonzero(cdf_ratio > 0.00001)
        plt.plot(bins[idxs], cdf_ratio[idxs], patterns[constellation], label=nice_name[constellation])
        
    
    plt.xlabel("Min RTT / Max RTT", fontsize=18)
    plt.ylabel("CDF", fontsize=18)
    plt.legend(fontsize=14, loc="upper left", frameon=False)
    plt.yticks([0, 0.2,0.4,0.6,0.8,1], fontsize=14)
    plt.xticks(fontsize=14)
    plt.grid(linewidth=0.5, linestyle=':')
    # plt.title("Variation in RTT", fontsize=18)
    plt.tight_layout()
    

    base_file = "paper_plots/rttVariation"
    png_file = base_file + ".png"
    pdf_file = base_file + ".pdf"
    plt.savefig(png_file)
    plt.savefig(pdf_file)