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

def load_fwd_state_data(algo, frequency, total_time):
    rtt = []
    dir = "data/" + algo + "/" + total_time + "ms_for_" + frequency + "s/manual/data/"
    old_len = len(rtt)
    for file in os.listdir(dir):
        old_len = len(rtt)
        if file.startswith("networkx_rtt_1.2_"):
            f = dir + file
            with open(f) as csvfile:
                spamreader = csv.reader(csvfile, delimiter=',',quotechar='"',quoting=csv.QUOTE_ALL, skipinitialspace=True)

                for row in spamreader:
                    # print(row)
                    old = float(row[1])
                    if np.isnan(old) or old == 0:
                        print(f, row)
                        continue
                    rtt.append(old)
        
        if len(rtt) - old_len != 200:
            print(file, len(rtt) - old_len)


    return rtt

def load_data(algo, frequency, total_time):
    old_rtt = []
    new_rtt = []
    old_rtt_20 = []
    new_rtt_20 = []
    old_rtt_25 = []
    new_rtt_25 = []
    dir = "data/" + algo + "/" + frequency + "ms_for_" + total_time + "s/manual/data/"
    for file in os.listdir(dir):
        if file.startswith("networkx_rtt_comparison"):
            # print(file)
            f = dir + file
            with open(f) as csvfile:
                spamreader = csv.reader(csvfile, delimiter=',',quotechar='"',quoting=csv.QUOTE_ALL, skipinitialspace=True)

                for row in spamreader:
                    # print(row)
                    old = float(row[1])
                    new = float(row[2])
                    if np.isnan(old) or np.isnan(new) or old == 0 or new == 0:
                        print(f, row)
                        continue
                    old_rtt.append(old)
                    new_rtt.append(new)
        elif file.startswith("networkx_rtt_20_"):
            # print(file)
            f = dir + file
            with open(f) as csvfile:
                spamreader = csv.reader(csvfile, delimiter=',',quotechar='"',quoting=csv.QUOTE_ALL, skipinitialspace=True)

                for row in spamreader:
                    # print(row)
                    old = float(row[1])
                    new = float(row[2])
                    if np.isnan(old) or np.isnan(new) or old == 0 or new == 0:
                        print(f, row)
                        continue
                    old_rtt_20.append(old)
                    new_rtt_20.append(new)
        elif file.startswith("networkx_rtt_25.0_"):
            # print(file)
            f = dir + file
            with open(f) as csvfile:
                spamreader = csv.reader(csvfile, delimiter=',',quotechar='"',quoting=csv.QUOTE_ALL, skipinitialspace=True)

                for row in spamreader:
                    # print(row)
                    old = float(row[1])
                    new = float(row[2])
                    if np.isnan(old) or np.isnan(new) or old == 0 or new == 0:
                        print(f, row)
                        continue
                    old_rtt_25.append(old)
                    new_rtt_25.append(new)

    return np.array(old_rtt), np.array(new_rtt), np.array(old_rtt_20), np.array(new_rtt_20), np.array(old_rtt_25), np.array(new_rtt_25)

if __name__ == '__main__':
    
    old_rtt, new_rtt, old_rtt_20, new_rtt_20, old_rtt_25, new_rtt_25 = load_data(sys.argv[1], sys.argv[2], sys.argv[3])
    rtt_1_2 = load_fwd_state_data(sys.argv[1], sys.argv[2], sys.argv[3])
    np.set_printoptions(threshold=sys.maxsize)
    ratio = np.divide(new_rtt, old_rtt)
    ratio_20 = np.divide(new_rtt_20, old_rtt_20)
    ratio_25 = np.divide(new_rtt_25, old_rtt_25)
    
    # print(times, middle_times)
    # print(times)
    print("Mean, 25th Percentile, Median, 75th Percentile, 90th Percentile, Max, Min, Std")
    print(np.mean(ratio), np.percentile(ratio, 25), np.median(ratio), np.percentile(ratio, 75), np.percentile(ratio, 90),  np.max(ratio), np.min(ratio), np.std(ratio), sep=',')
    count, bins_count = np.histogram(ratio, bins=50)
    pdf_ratio = count / sum(count)
    cdf_ratio = np.cumsum(pdf_ratio)

    print(np.mean(ratio_20), np.percentile(ratio_20, 25), np.median(ratio_20), np.percentile(ratio_20, 75), np.percentile(ratio_20, 90),  np.max(ratio_20), np.min(ratio_20), np.std(ratio_20), sep=',')
    count, bins_count = np.histogram(ratio_20, bins=50)
    pdf_ratio_20 = count / sum(count)
    cdf_ratio_20 = np.cumsum(pdf_ratio_20)

    print(np.mean(ratio_25), np.percentile(ratio_25, 25), np.median(ratio_25), np.percentile(ratio_25, 75), np.percentile(ratio_25, 90),  np.max(ratio_25), np.min(ratio_25), np.std(ratio_25), sep=',')
    count, bins_count = np.histogram(ratio_25, bins=50)
    pdf_ratio_25 = count / sum(count)
    cdf_ratio_25 = np.cumsum(pdf_ratio_25)

    print(len(rtt_1_2), np.mean(rtt_1_2), np.percentile(rtt_1_2, 25), np.median(rtt_1_2), np.percentile(rtt_1_2, 75), np.percentile(rtt_1_2, 90),  np.max(rtt_1_2), np.min(rtt_1_2), np.std(rtt_1_2), sep=',')
    print(len(new_rtt_20), np.mean(new_rtt_20), np.percentile(new_rtt_20, 25), np.median(new_rtt_20), np.percentile(new_rtt_20, 75), np.percentile(new_rtt_20, 90),  np.max(new_rtt_20), np.min(new_rtt_20), np.std(new_rtt_20), sep=',')
    print(len(old_rtt_20), np.mean(old_rtt_20), np.percentile(old_rtt_20, 25), np.median(old_rtt_20), np.percentile(old_rtt_20, 75), np.percentile(old_rtt_20, 90),  np.max(old_rtt_20), np.min(old_rtt_20), np.std(old_rtt_20), sep=',')
    print(len(new_rtt_25), np.mean(new_rtt_25), np.percentile(new_rtt_25, 25), np.median(new_rtt_25), np.percentile(new_rtt_25, 75), np.percentile(new_rtt_25, 90),  np.max(new_rtt_25), np.min(new_rtt_25), np.std(new_rtt_25), sep=',')
    print(len(old_rtt_25), np.mean(old_rtt_25), np.percentile(old_rtt_25, 25), np.median(old_rtt_25), np.percentile(old_rtt_25, 75), np.percentile(old_rtt_25, 90),  np.max(old_rtt_25), np.min(old_rtt_25), np.std(old_rtt_25), sep=',')
    

    # print(pdf, cdf)

    # plt.plot(bins_count[1:], pdf, color="red", label="PDF")
    plt.plot(bins_count[1:], cdf_ratio, label="Ratio of RTTs")
    plt.plot(bins_count[1:], cdf_ratio_20, label="Ratio of RTTs capped at 20%", color="red")
    plt.plot(bins_count[1:], cdf_ratio_25, label="Ratio of RTTs capped at 25%", color="green")
    plt.xlabel("Ratio")
    plt.ylabel("Probability")
    plt.legend()

    base_file = sys.argv[1] + "_rtt_" + sys.argv[2] + "ms_" + sys.argv[3] + "s"
    png_file = base_file + ".png"
    pdf_file = base_file + ".pdf"
    plt.savefig(png_file)
    plt.savefig(pdf_file)