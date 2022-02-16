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
import json
import math

def load_data():
    ratios = np.empty(shape = (0,))
    means = np.empty(shape = (0,))
    std_devs = np.empty(shape = (0,))
    maxs = np.empty(shape = (0,))
    dir = "good_paths_1/outs/"
    for file in os.listdir(dir):
        f = dir + file
        print(f)
        with open(f) as csvfile:
            spamreader = csv.reader(csvfile, delimiter=']',quotechar='"',quoting=csv.QUOTE_ALL, skipinitialspace=True)
            id = 0
            paths = []
            distances = []
            for row in spamreader:
                if id < 201:
                    id = id + 1
                    continue
                if len(row) == 0:
                    continue
                # print(row)
                paths.append(np.array(json.loads(row[0] + "]")))
                distances.append(np.array(json.loads(row[1] + "]")))
                
            paths = np.array(paths)
            distances = np.array(distances)
            updated_distances = np.where(distances == 0, math.inf, distances)
            
            if len(np.nonzero(distances / np.amin(updated_distances) > 1.75)[0]) > 0:
                cmd = "python good_paths_1.py " +  str(paths[0][0]) + " " + str(paths[0][-1]) + " > good_paths_2/outs/" + str(paths[0][0]) + "_" + str(paths[0][-1]) + ".txt"
                print(cmd)

            shortest_lengths = np.amin(updated_distances, axis=0) / np.amin(updated_distances)
            ratios = np.append(ratios, shortest_lengths)
            means = np.append(means, np.mean(shortest_lengths))
            std_devs = np.append(std_devs, np.std(shortest_lengths))
            print("max ratio", paths[0][0], paths[0][-1],np.max(shortest_lengths),sep=",")
            maxs = np.append(maxs, np.max(shortest_lengths))

    return ratios, means, std_devs,maxs

if __name__ == '__main__':
    np.set_printoptions(threshold=sys.maxsize)
    ratios, means, std_devs, maxs = load_data()
    
    print("Mean, 25th Percentile, Median, 75th Percentile, 90th Percentile, Max, Min, Std")
    print(np.mean(ratios), np.percentile(ratios, 25), np.median(ratios), np.percentile(ratios, 75), np.percentile(ratios, 90),  np.max(ratios), np.min(ratios), np.std(ratios), sep=',')
    count, bins_count = np.histogram(ratios, bins=50)
    pdf_ratios = count / sum(count)
    cdf_ratios = np.cumsum(pdf_ratios)

    print(np.mean(means), np.percentile(means, 25), np.median(means), np.percentile(means, 75), np.percentile(means, 90),  np.max(means), np.min(means), np.std(means), sep=',')
    print(np.mean(maxs), np.percentile(maxs, 25), np.median(maxs), np.percentile(maxs, 75), np.percentile(maxs, 90),  np.max(maxs), np.min(maxs), np.std(maxs), sep=',')
    count, bins_count_max = np.histogram(maxs, bins=50)
    pdf_maxs = count / sum(count)
    cdf_maxs = np.cumsum(pdf_maxs)
    print(np.mean(std_devs), np.percentile(std_devs, 25), np.median(std_devs), np.percentile(std_devs, 75), np.percentile(std_devs, 90),  np.max(std_devs), np.min(std_devs), np.std(std_devs), sep=',')

    plt.plot(bins_count[1:], cdf_ratios, label="All ratios")
    plt.plot(bins_count_max[1:], cdf_maxs, label="Max ratio")
    plt.xlabel("Ratio")
    plt.ylabel("Probability")
    plt.legend()

    base_file = "shortest_paths"
    png_file = base_file + ".png"
    pdf_file = base_file + ".pdf"
    plt.savefig(png_file)
    plt.savefig(pdf_file)