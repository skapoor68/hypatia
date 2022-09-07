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

def load_data(constellation, frequency, total_time):
    usage_times = []
    life_times = []
    greedy_times = []
    # bad_paths = 
    dir = "paper_data/" + constellation + "/" + frequency + "ms_for_" + total_time + "s/manual/data/"
    greedy_dir = "paper_data/" + constellation + "/greedy_" + frequency + "ms_for_" + total_time + "s/manual/data/"
    for src in range(1584, 1684):
        for dst in range(src+1, 1684):
            f = dir + "networkx_path_" + str(src) + "_to_" + str(dst) + ".txt"
            with open(f) as csvfile:
                spamreader = csv.reader(csvfile, delimiter=',',quotechar='"',quoting=csv.QUOTE_ALL, skipinitialspace=True)

                id = 0
                prev_time = -1
                for row in spamreader:
                    # path = list(row[1].split("-"))
                    # path = [int(i) for i in path]
                    # p = path[1:-1]
                    # if not all(x < 1584 for x in p):
                    #     print(path)
                    # print(row)
                    if prev_time == -1:
                        prev_time = int(row[0]) / 1000000000
                        continue
                    
                    t = int(row[0]) / 1000000000
                    path_time = t - prev_time
                    usage_times.append(path_time)

                    prev_time = t
                    id = id + 1
                    # if usage_times[-1] > 150:
                    #     print(row)

                if prev_time == -1:
                    print(f)
                else:
                    usage_times.append(float(total_time) - prev_time)

                # if usage_times[-1] > 150:
                #     print(row)
        
            f = dir + "networkx_life_of_path_" + str(src) + "_to_" + str(dst) + ".txt"
            with open(f) as csvfile:
                spamreader = csv.reader(csvfile, delimiter=',',quotechar='"',quoting=csv.QUOTE_ALL, skipinitialspace=True)

                id = 0
                prev_time = -1
                for row in spamreader:
                    
                    t = int(row[2])
                    life_times.append(t)

                    id = id + 1

            f = greedy_dir + "networkx_path_0.2_" + str(src) + "_to_" + str(dst) + ".txt"
            with open(f) as csvfile:
                spamreader = csv.reader(csvfile, delimiter=',',quotechar='"',quoting=csv.QUOTE_ALL, skipinitialspace=True)

                id = 0
                prev_time = -1
                for row in spamreader:
                    # path = list(row[1].split("-"))
                    # path = [int(i) for i in path]
                    # p = path[1:-1]
                    # if not all(x < 1584 for x in p):
                    #     print(path)
                    # print(row)
                    if prev_time == -1:
                        prev_time = int(row[0]) / 1000000000
                        continue
                    
                    t = int(row[0]) / 1000000000
                    path_time = t - prev_time
                    greedy_times.append(path_time)
                    # if greedy_times[-1] == 1:
                    #     print(src, dst)

                    prev_time = t
                    id = id + 1
                    # if greedy_times[-1] > 150:
                    #     print(row)

                if prev_time == -1:
                    print(f)
                else:
                    greedy_times.append(float(total_time) - prev_time)


    return np.array(usage_times), np.array(life_times), np.array(greedy_times)

if __name__ == '__main__':
    nice_name = {"kuiper_630_isls_plus_grid_ground_stations_top_100_algorithm_free_one_only_over_isls" : "Kuiper 630",
    "starlink_550_isls_plus_grid_ground_stations_top_100_algorithm_free_one_only_over_isls" : "Starlink 550",
    "telesat_1015_isls_plus_grid_ground_stations_top_100_algorithm_free_one_only_over_isls": "Telesat 1015"
    }

    file_name = {"kuiper_630_isls_plus_grid_ground_stations_top_100_algorithm_free_one_only_over_isls" : "kuiper",
    "starlink_550_isls_plus_grid_ground_stations_top_100_algorithm_free_one_only_over_isls" : "starlink",
    "telesat_1015_isls_plus_grid_ground_stations_top_100_algorithm_free_one_only_over_isls": "telesat"
    }

    constellation = "starlink_550_isls_plus_grid_ground_stations_top_100_algorithm_free_one_only_over_isls"
    frequency = "1000"
    total_time = "6000"
    usage_times, life_times, greedy_times = load_data(constellation, frequency, total_time)
    
    max_time = max(np.max(usage_times), np.max(life_times))
    max_time = 100 * ((max_time // 100) + 1)
    bins = np.linspace(0, max_time, 10000)
    # print("Mean, 25th Percentile, Median, 75th Percentile, 90th Percentile, Max, Min, Std")
    # print(np.mean(usage_times), np.percentile(usage_times, 25), np.median(usage_times), np.percentile(usage_times, 75), np.percentile(usage_times, 90),  np.max(usage_times), np.min(usage_times), np.std(usage_times), sep=',')
    count, bins_count = np.histogram(usage_times, bins=bins)
    pdf_usage_times = count / sum(count)
    cdf_usage_times = np.cumsum(pdf_usage_times)
    print(list(cdf_usage_times))


    # print("Mean, 25th Percentile, Median, 75th Percentile, 90th Percentile, Max, Min, Std")
    # print(np.mean(greedy_times), np.percentile(greedy_times, 25), np.median(greedy_times), np.percentile(greedy_times, 75), np.percentile(greedy_times, 90),  np.max(greedy_times), np.min(greedy_times), np.std(greedy_times), sep=',')
    count, bins_count = np.histogram(greedy_times, bins=bins)
    pdf_greedy_times = count / sum(count)
    cdf_greedy_times = np.cumsum(pdf_greedy_times)
    print(list(cdf_greedy_times))

    # print("Mean, 25th Percentile, Median, 75th Percentile, 90th Percentile, Max, Min, Std")
    # print(np.mean(life_times), np.percentile(life_times, 25), np.median(life_times), np.percentile(life_times, 75), np.percentile(life_times, 90),  np.max(life_times), np.min(life_times), np.std(life_times), sep=',')
    count, bins_count = np.histogram(life_times, bins=bins)
    pdf_life_times = count / sum(count)
    cdf_life_times = np.cumsum(pdf_life_times)
    print(list(cdf_life_times))

    # data = np.genfromtxt("greedy_path_lifetimes.txt", delimiter=",")
    # print(data.shape)
    bins = np.linspace(0, 300, 10000)
    plt.figure(figsize=(6.4,3.2))
    plt.xlabel("Path Life (seconds)", fontsize=18)
    plt.ylabel("CDF", fontsize=18)
    plt.yticks([0, 0.2,0.4,0.6,0.8,1], fontsize=14)
    plt.xticks(fontsize=14)
    # plt.xscale("log")
    # plt.xticks([1,2,5,10,20,40,80,160,320], labels=[1,2,5,10,20,40,80,160,320], fontsize=16)
    
    # plt.title(nice_name[constellation], fontsize=18)
    # cdf_usage_times = data[0]
    idxs = np.where((cdf_usage_times < 0.99999) & (cdf_usage_times > 0))
    plt.plot(bins[idxs], cdf_usage_times[idxs], "r-", label="Usage time of Paths")

    # cdf_life_times = data[2]
    idxs = np.where((cdf_life_times < 0.99999) & (cdf_life_times > 0))
    plt.plot(bins[idxs], cdf_life_times[idxs], "g-.", label="Life time of Paths")

    # cdf_greedy_times = data[1]
    idxs = np.where((cdf_greedy_times < 0.99999) & (cdf_greedy_times > 0))
    plt.plot(bins[idxs], cdf_greedy_times[idxs], "b--", label="Thrifty usage times of Paths")
    plt.arrow(0, 0.8, 40,0, width=0.3, head_width=0.5, head_length=20, fill=False, alpha=0.5)
    plt.annotate("Better", (0,0.75), alpha=0.5, fontsize=20)
    base_file = "paper_plots/" +  file_name[constellation] + "GreedyPathLife"
    png_file = base_file + ".png"
    pdf_file = base_file + ".pdf"
    plt.legend(fontsize=14, loc="lower right", frameon=False)
    plt.grid(linewidth=0.5, linestyle=':')
    plt.tight_layout()
    plt.savefig(png_file)
    plt.savefig(pdf_file)