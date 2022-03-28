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

def load_data(algo, frequency, total_time):
    usable_times = []
    life_times = []
    dir = "paper_data/" + algo + "/" + frequency + "ms_for_" + total_time + "s/manual/data/"
    for file in os.listdir(dir):
        if file.startswith("networkx_path_"):            
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
                    usable_times.append(path_time)

                    prev_time = t
                    id = id + 1

                if prev_time == -1:
                    print(f)
                else:
                    usable_times.append(6000 - prev_time)
        elif file.startswith("networkx_life_of_path"):
            f = dir + file
            with open(f) as csvfile:
                spamreader = csv.reader(csvfile, delimiter=',',quotechar='"',quoting=csv.QUOTE_ALL, skipinitialspace=True)

                id = 0
                prev_time = -1
                for row in spamreader:
                    
                    t = int(row[2])
                    life_times.append(t)

                    id = id + 1


    return np.array(usable_times), np.array(life_times)

if __name__ == '__main__':
    args = sys.argv[1:]
    nice_name = {"kuiper_630_isls_plus_grid_ground_stations_top_100_algorithm_free_one_only_over_isls" : "Kuiper 630",
    "starlink_550_isls_plus_grid_ground_stations_top_100_algorithm_free_one_only_over_isls" : "Starlink 550",
    "telesat_1015_isls_plus_grid_ground_stations_top_100_algorithm_free_one_only_over_isls": "Telesat 1015"
    }

    file_name = {"kuiper_630_isls_plus_grid_ground_stations_top_100_algorithm_free_one_only_over_isls" : "kuiper",
    "starlink_550_isls_plus_grid_ground_stations_top_100_algorithm_free_one_only_over_isls" : "starlink",
    "telesat_1015_isls_plus_grid_ground_stations_top_100_algorithm_free_one_only_over_isls": "telesat"
    }

    # patterns = {"kuiper_630_isls_plus_grid_ground_stations_top_100_algorithm_free_one_only_over_isls" : "r--",
    # "starlink_550_isls_plus_grid_ground_stations_top_100_algorithm_free_one_only_over_isls" : "b-",
    # "telesat_1015_isls_plus_grid_ground_stations_top_100_algorithm_free_one_only_over_isls": "g-."
    # }

    # times, middle_times, route_life, middle_route_life, updated_times, updated_middle_times, times_20, times_25 = load_data(sys.argv[1], sys.argv[2], sys.argv[3])
    # times_1_2 = load_fwd_state_data(sys.argv[1], sys.argv[2], sys.argv[3])
    usable_times, life_times = load_data(args[0], args[1], args[2])

    print("Mean, 25th Percentile, Median, 75th Percentile, 90th Percentile, Max, Min, Std")
    print(np.mean(usable_times), np.percentile(usable_times, 25), np.median(usable_times), np.percentile(usable_times, 75), np.percentile(usable_times, 90),  np.max(usable_times), np.min(usable_times), np.std(usable_times), sep=',')
    count, bins_count = np.histogram(usable_times, bins=50)
    pdf_usable_times = count / sum(count)
    cdf_usable_times = np.cumsum(pdf_usable_times)

    print("Mean, 25th Percentile, Median, 75th Percentile, 90th Percentile, Max, Min, Std")
    print(np.mean(life_times), np.percentile(life_times, 25), np.median(life_times), np.percentile(life_times, 75), np.percentile(life_times, 90),  np.max(life_times), np.min(life_times), np.std(life_times), sep=',')
    count, bins_count = np.histogram(life_times, bins=50)
    pdf_life_times = count / sum(count)
    cdf_life_times = np.cumsum(pdf_life_times)

    plt.xlabel("Path Life (seconds)", fontsize=18)
    plt.ylabel("Probability", fontsize=18)
    plt.yticks([0.1, 0.2, 0.3,0.4,0.5,0.6,0.7,0.8,0.9,1], fontsize=14)
    plt.xticks(fontsize=14)
    
    plt.title(nice_name[args[0]])
    plt.plot(bins_count[1:], cdf_usable_times, "r--", label="Usability time of a Path")
    plt.plot(bins_count[1:], cdf_life_times, "g-.", label="Life times of a Path")
    base_file = "paper_plots/" + file_name[args[0]] + "PathLife"
    png_file = base_file + ".png"
    pdf_file = base_file + ".pdf"
    plt.legend(fontsize=14, loc="lower right")
    plt.savefig(png_file)
    plt.savefig(pdf_file)