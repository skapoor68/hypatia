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

def load_data(constellation):
    ratio = []
    dir = "paper_data/" + constellation + "/1000ms_for_6000s/manual/data/"
    for file in os.listdir(dir):
        if file.startswith("networkx_path_"):
            f = dir + file
            with open(f) as csvfile:
                spamreader = csv.reader(csvfile, delimiter=',',quotechar='"',quoting=csv.QUOTE_ALL, skipinitialspace=True)

                id = 0
                prev_path = ""
                prev_links = []
                for row in spamreader:
                    # print(row)
                    if prev_path == "":
                        prev_path = list(row[1].split("-"))
                        prev_path = [int(i) for i in prev_path]
                        prev_links = [str(prev_path[i]) + "_" +  str(prev_path[i + 1]) for i in range(len(prev_path) - 1)]
                        continue
                    
                    path = list(row[1].split("-"))
                    path = [int(i) for i in path]
                    current_links = [str(path[i]) + "_" +  str(path[i + 1]) for i in range(len(path) - 1)]
                    intersection = list(set(current_links).intersection(prev_links))

                    ratio.append((len(prev_links) - len(intersection)) / len(prev_links))

                    prev_links = current_links
                    id = id + 1


    return np.array(ratio)

if __name__ == '__main__':
    constellations  = ["kuiper_630_isls_plus_grid_ground_stations_top_100_algorithm_free_one_only_over_isls",
    "starlink_550_isls_plus_grid_ground_stations_top_100_algorithm_free_one_only_over_isls",
    "telesat_1015_isls_plus_grid_ground_stations_top_100_algorithm_free_one_only_over_isls"
    ]

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
    
    for constellation in constellations:
        ratio = load_data(constellation)
        
        print("Mean, 25th Percentile, Median, 75th Percentile, 90th Percentile, Max, Min, Std")
        print(np.mean(ratio), np.percentile(ratio, 25), np.median(ratio), np.percentile(ratio, 75), np.percentile(ratio, 90),  np.max(ratio), np.min(ratio), np.std(ratio), sep=',')
        count, bins_count = np.histogram(ratio, bins=np.linspace(0,1,51))
        pdf_ratio = count / sum(count)
        cdf_ratio = np.cumsum(pdf_ratio)

        plt.xlabel("Path Variation Ratio", fontsize=18)
        plt.ylabel("Probability", fontsize=18)
        plt.yticks([0.1, 0.2, 0.3,0.4,0.5,0.6,0.7,0.8,0.9,1], fontsize=14)
        plt.xticks(fontsize=14)
        
        plt.plot(bins_count[1:], cdf_ratio, patterns[constellation], label=nice_name[constellation] + "\nVariation in Composition")
    
    base_file = "paper_plots/pathVariations"
    png_file = base_file + ".png"
    pdf_file = base_file + ".pdf"
    plt.legend(fontsize=14, loc="upper left")
    plt.savefig(png_file)
    plt.savefig(pdf_file)