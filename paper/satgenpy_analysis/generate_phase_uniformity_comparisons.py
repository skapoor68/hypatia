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
import networkx as nx
sys.path.append("../../satgenpy")
from satgen import *


if __name__ == '__main__':
    
    plt.xlabel("Distance to closest satellite (km)", fontsize=18)
    plt.ylabel("CDF", fontsize=18)
    
    plt_colors = ["b--", "r--", "g--", "m--", "y--",  "c--"]
    labels = ["0", "1/6", "1/3", "1/2", "2/3", "5/6"]
    # x = np.arange(0, total_time)

    distances = np.genfromtxt("best_phase_all.txt", delimiter=",")[:, 1:]
    phases = np.linspace(0,72, num=6, endpoint=False, dtype=int)
    data = distances[phases] - 500
    print(np.min(data), np.max(data))
    bins = np.linspace(28, 600, 10000)

    idx = 0
    for row in data:
        count, bins_count = np.histogram(row, bins=bins)
        pdf_usage_times = count / sum(count)
        cdf_usage_times = np.cumsum(pdf_usage_times)
        idxs = np.where((cdf_usage_times < 0.99999) & (cdf_usage_times > 0))
        plt.plot(bins[idxs], cdf_usage_times[idxs], plt_colors[idx], label=labels[idx])
        idx += 1



    # print(list(latencies))
    # plt.plot(x[:200], latencies, "k-", linewidth=3, alpha=0.5)

    # data = np.genfromtxt("rtt_instance.txt", delimiter=",")
    # for i in range(data.shape[0] - 1):
    #     rtt = data[i]
    #     idxs = np.argwhere(rtt > 0)
    #     plt.plot(x[idxs], rtt[idxs], path_colors[i], linestyle='--')

    # latencies = data[-1]
    # plt.plot(x[:200], latencies[:200], "k-", linewidth=3, alpha=0.3)

    plt.legend(fontsize=14, loc="lower right")
    plt.yticks(fontsize=14)
    plt.xscale("log")
    # ticks = np.array([0, 25, 50, 100, 200, 400, 600])
    plt.xticks(ticks = [25, 50, 100, 200, 400, 600], labels=[525, 500,600,700,900,1100], fontsize=14)
    # plt.title("Frequent path switching for Jakarta to Bogotá", fontsize=18)
    plt.grid(linewidth=0.5, linestyle=':')
    plt.tight_layout()

            
    base_file = "paper_plots/phase_uniformity_all"
    png_file = base_file + ".png"
    pdf_file = base_file + ".pdf"
    plt.savefig(png_file)
    plt.savefig(pdf_file)