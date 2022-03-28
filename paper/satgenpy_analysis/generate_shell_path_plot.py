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
    times = []
    dir = "data/" + config + "/" + str(frequency) + "ms_for_" + str(total_time) + "s/manual/data/"
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

                times.append(200 - prev_time)

    return np.array(times)


if __name__ == '__main__':
    print("Name, Mean, 25th Percentile, Median, 75th Percentile, 90th Percentile, Max, Min, Std")
    plt_colors = ["b-", "r-", "g-", "c-", "m-", "y-", "k-", "b--", "r--", "g--", "c--", "m--", "y--", "k--", "b:", "r:", "g:", "c:", "m:", "y:", "k:", "b-.", "r-.", "g-.", "c-.", "m-.", "y-.", "k-."]
    for i in range(len(configurations)):
        times = load_data(configurations[i], 1000, 200)
        print(names[i], np.mean(times), np.percentile(times, 25), np.median(times), np.percentile(times, 75), np.percentile(times, 90),  np.max(times), np.min(times), np.std(times), sep=',')
        count, bins_count = np.histogram(times, bins=50)
        pdf_times = count / sum(count)
        cdf_times = np.cumsum(pdf_times)
        plt.plot(bins_count[1:], cdf_times, plt_colors[i], label=names[i])


    # plt.plot(bins_count[1:], pdf, color="red", label="PDF")
    plt.xlabel("Time(seconds)")
    plt.ylabel("Probability")
    
    plt.legend()
    base_file = "shells"
    png_file = base_file + ".png"
    pdf_file = base_file + ".pdf"
    plt.savefig(png_file)
    plt.savefig(pdf_file)