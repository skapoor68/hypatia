import os, sys
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.ticker as tk
import numpy as np
from collections import OrderedDict
from matplotlib.ticker import FormatStrFormatter
from matplotlib.collections import LineCollection
from datetime import datetime
import csv
import scipy
import networkx as nx
sys.path.append("../../satgenpy")
from satgen import *

total_time = int(sys.argv[1])



if __name__ == '__main__':
    all_paths = []
    start_time = 0
    end_time = total_time*1000*1000*1000
    for i in range(start_time, end_time, 1000*1000*1000):
        # idx = start_time + i*1000*1000*1000
        paths = "path_length_variation/paths_" + str(i) + ".txt"
        all_paths.append(np.genfromtxt(paths))

    all_paths = np.array(all_paths)
    path_colors = ["b-", "r--", "g-.", "m:"]
    labels = ["Top-2 Variation", "Top-5 Variation", "Top-10 Variation", "Top-15 Variation"]
    ratios = [2,5,10,15]
    all_paths = all_paths.reshape((-1, 4))
    
    print("Mean, 25th Percentile, Median, 75th Percentile, 90th Percentile, Max, Min, Std")
    
    for i in range(4):
        data = all_paths[:,i]
        print(np.mean(data), np.percentile(data, 25), np.median(data), np.percentile(data, 75), np.percentile(data, 90),  np.max(data), np.min(data), np.std(data), sep=',')
        count, bins_count = np.histogram(data, bins=50)
        pdf_data = count / sum(count)
        cdf_data = np.cumsum(pdf_data)
        plt.plot(bins_count[1:], cdf_data, path_colors[i], label=labels[i])

    
    # plt.title("Utilization for the New York-London Route", fontsize=18)
    plt.xlabel("Variation in length in top-k paths", fontsize=18)
    plt.ylabel("CDF", fontsize=18)
    plt.yticks(fontsize=14)
    plt.xticks(fontsize=14)
    plt.yticks([0, 0.2,0.4,0.6,0.8,1], fontsize=14)
    plt.grid(linewidth=0.5, linestyle=':')
    plt.tight_layout()
    plt.legend(fontsize=14, loc="lower right", frameon=False)
            
    base_file = "paper_plots/path_variation_ratios"
    png_file = base_file + ".png"
    pdf_file = base_file + ".pdf"
    plt.savefig(png_file)
    plt.savefig(pdf_file)