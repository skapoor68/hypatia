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

def load_data():
    file_name = 'system_eval/cpu_memory.csv'

    times = []
    middle_times = []
    dir = "data/kuiper_630_isls_plus_grid_ground_stations_top_100_algorithm_free_one_only_over_isls/1000ms_for_200s/path/data/"
    for file in os.listdir(dir):
        if file.startswith("networkx_path_"):
            print(file)
            f = dir + file
            with open(f) as csvfile:
                spamreader = csv.reader(csvfile, delimiter=',',quotechar='"',quoting=csv.QUOTE_ALL, skipinitialspace=True)

                id = 0
                prev_time = -1
                for row in spamreader:
                    if prev_time == -1:
                        prev_time = int(row[0]) / 1000000000
                        continue
                    
                    t = int(row[0]) / 1000000000
                    path_time = t - prev_time
                    times.append(path_time)
                    if id > 0:
                        middle_times.append(path_time)

                    prev_time = t
                    id = id + 1

                times.append(200 - prev_time)

    return np.array(times), np.array(middle_times)

if __name__ == '__main__':
    # data_file = 'data-7UELV.csv'
    # matplotlib.rcParams['text.usetex'] = True
    # matplotlib.rcParams['pdf.fonttype'] = 42
    
    times, middle_times = load_data()

    # print(times, middle_times)
       
    print(np.mean(times), np.median(times), np.max(times), np.min(times), np.std(times)) 
    count, bins_count = np.histogram(times, bins=50)
    pdf_times = count / sum(count)
    cdf_times = np.cumsum(pdf_times)

    print(np.mean(middle_times), np.median(middle_times), np.max(middle_times), np.min(middle_times), np.std(middle_times)) 
    count, bins_count = np.histogram(middle_times, bins=50)
    pdf_middle_times = count / sum(count)
    cdf_middle_times = np.cumsum(pdf_middle_times)

    # print(pdf, cdf)

    # plt.plot(bins_count[1:], pdf, color="red", label="PDF")
    plt.plot(bins_count[1:], cdf_times, label="all times")
    plt.plot(bins_count[1:], cdf_middle_times, label="middle times", color="red")
    # plt.legend()

    plt.savefig("compare.png")
    plt.savefig("compare.pdf")

    # if flag:
    #     plt.savefig("times.png")
    #     plt.savefig("times.pdf")
    # else:
    #     plt.savefig("middle_times.png")
    #     plt.savefig("middle_times.pdf")

    # for pods in cpu:
    #     if pods < 2 or pods == 5:
    #         continue
    #     cpuValues = np.array(cpu[pods])
    #     cpu_means.append(np.mean(cpuValues))
    #     cpu_std.append(np.std(cpuValues))
    #     x_axis.append(pods)

    # cpu_means = np.array(cpu_means)
    # cpu_std = np.array(cpu_std)
    # x_axis = np.array(x_axis)
    # cpu_axis = np.array([1000, 1200, 1400, 1600, 1800, 2000, 2200])

    # for pods in memory:
    #     if pods < 2 or pods == 5:
    #         continue
    #     memoryValues = np.array(memory[pods])
    #     memory_means.append(np.mean(memoryValues))
    #     memory_std.append(np.std(memoryValues))

    # memory_means = np.array(memory_means)
    # memory_std = np.array(memory_std)
    # memory_axis = np.array([4800, 5000, 5200, 5400, 5600, 5800, 6000, 6200, 6400, 6600, 6800])
    # print(x_axis.shape, cpu_means.shape, cpu_std.shape, memory_means.shape, memory_std.shape)
    # print(x_axis, cpu_means, cpu_std, memory_means, memory_std)

    # fig, ax1 = plt.subplots()

    # color = 'tab:red'
    # ax1.set_xlabel('Number of pods')
    # ax1.set_xticks(x_axis)
    # ax1.set_xticklabels(x_axis, fontsize=16)
    # ax1.set_yticks(cpu_axis)
    # ax1.set_yticklabels(cpu_axis, fontsize=16)
    # ax1.set_ylabel('Millicores consumed', color=color)
    # # ax1.plot(t, data1, color=color)
    # ax1.errorbar(x_axis, cpu_means, yerr=cpu_std, fmt='ro-')
    # ax1.tick_params(axis='y', labelcolor=color)

    # ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis

    # color = 'tab:blue'
    # ax2.set_ylabel('Memory in Megabits', color=color)  # we already handled the x-label with ax1
    # ax2.set_yticks(memory_axis)
    # ax2.set_yticklabels(memory_axis, fontsize=16)
    # ax2.errorbar(x_axis, memory_means, yerr=memory_std, fmt='bo:')
    # ax2.tick_params(axis='y', labelcolor=color)

    # fig.tight_layout()  # otherwise the right y-label is slightly clipped
    # plt.show()