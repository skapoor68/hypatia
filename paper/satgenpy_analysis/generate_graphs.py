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
    times = []
    middle_times = []
    dir = "data/" + algo + "/" + frequency + "ms_for_" + total_time + "s/path/data/"
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
    
    times, middle_times = load_data(sys.argv[1], sys.argv[2], sys.argv[3])

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

    base_file = sys.argv[1] + "_" + sys.argv[2] + "ms_" + sys.argv[3] + "s"
    png_file = base_file + ".png"
    pdf_file = base_file + ".pdf"
    plt.savefig(png_file)
    plt.savefig(pdf_file)