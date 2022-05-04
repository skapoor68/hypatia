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
    route_life = []
    middle_route_life = []
    updated_times = []
    updated_middle_times = []
    times_20 = []
    middle_times_20 = []
    times_25 = []
    middle_times_25 = []
    max_changes = 0
    max_file = None
    dir = "paper_data/" + algo + "/" + frequency + "ms_for_" + total_time + "s/manual/data/"
    for file in os.listdir(dir):
        if file.startswith("networkx_path_"):
            # print(file)
            if file.startswith("networkx_path_dumb_"):
                continue
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
                        updated_times.append(path_time)
                        if id > 0:
                            updated_middle_times.append(path_time)

                        prev_time = t
                        id = id + 1

                    updated_times.append(200 - prev_time)
            elif file.startswith("networkx_path_20_"):
                continue
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
                        times_20.append(path_time)
                        if id > 0:
                            middle_times_20.append(path_time)

                        prev_time = t
                        id = id + 1

                    times_20.append(200 - prev_time)
            elif file.startswith("networkx_path_25.0_"):
                continue
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
                        times_25.append(path_time)
                        if id > 0:
                            middle_times_25.append(path_time)

                        prev_time = t
                        id = id + 1

                    times_25.append(200 - prev_time)
            else:
                f = dir + file
                with open(f) as csvfile:
                    spamreader = csv.reader(csvfile, delimiter=',',quotechar='"',quoting=csv.QUOTE_ALL, skipinitialspace=True)

                    id = 0
                    prev_time = -1
                    changes = 0
                    for row in spamreader:
                        # print(row)
                        if prev_time == -1:
                            prev_time = int(row[0]) / 1000000000
                            # life = int(row[1]) / 1000000000
                            # route_life.append(life)
                            continue
                        
                        t = int(row[0]) / 1000000000
                        # life = int(row[1]) / 1000000000
                        path_time = t - prev_time
                        times.append(path_time)
                        changes += 1
                        # route_life.append(life)
                        # middle_route_life.append(life)
                        if id > 0:
                            middle_times.append(path_time)

                        prev_time = t
                        id = id + 1
                        if t > 200:
                            break

                    # times.append(200 - prev_time)
                    if changes > max_changes:
                        max_changes = changes
                        max_file = file

    print(max_changes, max_file)
    exit(0)
    return np.array(times), np.array(middle_times), np.array(route_life) + 1, np.array(middle_route_life) + 1, np.array(updated_times), np.array(updated_middle_times), np.array(times_20), np.array(times_25)

def load_fwd_state_data(algo, frequency, total_time):
    times_1_2 = []
    dir = "data/" + algo + "/" + total_time + "ms_for_" + frequency + "s/manual/data/"
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
                    times_1_2.append(path_time)

                    prev_time = t
                    id = id + 1

                times_1_2.append(200 - prev_time)

    return times_1_2


if __name__ == '__main__':
    
    times, middle_times, route_life, middle_route_life, updated_times, updated_middle_times, times_20, times_25 = load_data(sys.argv[1], sys.argv[2], sys.argv[3])
    times_1_2 = load_fwd_state_data(sys.argv[1], sys.argv[2], sys.argv[3])

    # print(times, middle_times)
    # print(times)
    print("Mean, 25th Percentile, Median, 75th Percentile, 90th Percentile, Max, Min, Std")
    print(np.mean(times), np.percentile(times, 25), np.median(times), np.percentile(times, 75), np.percentile(times, 90),  np.max(times), np.min(times), np.std(times), sep=',')
    count, bins_count = np.histogram(times, bins=50)
    pdf_times = count / sum(count)
    cdf_times = np.cumsum(pdf_times)

    # print(middle_times)
    # print(np.mean(middle_times), np.percentile(middle_times, 25), np.median(middle_times), np.percentile(middle_times, 75), np.percentile(middle_times, 90),  np.max(middle_times), np.min(middle_times), np.std(middle_times), sep=',')
    # count, bins_count = np.histogram(middle_times, bins=50)
    # pdf_middle_times = count / sum(count)
    # cdf_middle_times = np.cumsum(pdf_middle_times)

    print(np.mean(route_life), np.percentile(route_life, 25), np.median(route_life), np.percentile(route_life, 75), np.percentile(route_life, 90),  np.max(route_life), np.min(route_life), np.std(route_life), sep=',')
    count, bins_count = np.histogram(route_life, bins=50)
    pdf_route_life = count / sum(count)
    cdf_route_life = np.cumsum(pdf_route_life)

    # print(np.mean(middle_route_life), np.percentile(middle_route_life, 25), np.median(middle_route_life), np.percentile(middle_route_life, 75), np.percentile(middle_route_life, 90),  np.max(middle_route_life), np.min(middle_route_life), np.std(middle_route_life), sep=',')
    # count, bins_count = np.histogram(middle_route_life, bins=50)
    # pdf_middle_route_life = count / sum(count)
    # cdf_middle_route_life = np.cumsum(pdf_middle_route_life)

    print(np.mean(updated_times), np.percentile(updated_times, 25), np.median(updated_times), np.percentile(updated_times, 75), np.percentile(updated_times, 90),  np.max(updated_times), np.min(updated_times), np.std(updated_times), sep=',')
    count, bins_count = np.histogram(updated_times, bins=50)
    pdf_updated_times = count / sum(count)
    cdf_updated_times = np.cumsum(pdf_updated_times)


    print(np.mean(times_1_2), np.percentile(times_1_2, 25), np.median(times_1_2), np.percentile(times_1_2, 75), np.percentile(times_1_2, 90),  np.max(times_1_2), np.min(times_1_2), np.std(times_1_2), sep=',')
    print(np.mean(times_20), np.percentile(times_20, 25), np.median(times_20), np.percentile(times_20, 75), np.percentile(times_20, 90),  np.max(times_20), np.min(times_20), np.std(times_20), sep=',')
    count, bins_count = np.histogram(times_20, bins=50)
    pdf_times_20 = count / sum(count)
    cdf_times_20 = np.cumsum(pdf_times_20)
    
    print(np.mean(times_25), np.percentile(times_25, 25), np.median(times_25), np.percentile(times_25, 75), np.percentile(times_25, 90),  np.max(times_25), np.min(times_25), np.std(times_25), sep=',')
    count, bins_count = np.histogram(times_25, bins=50)
    pdf_times_25 = count / sum(count)
    cdf_times_25 = np.cumsum(pdf_times_25)

    # print(pdf, cdf)

    # plt.plot(bins_count[1:], pdf, color="red", label="PDF")
    plt.xlabel("Time(seconds)")
    plt.ylabel("Probability")
    
    plt.plot(bins_count[1:], cdf_times, "b-", label="Life of a Path", color="blue")
    base_file = sys.argv[1] + "_path_life_" + sys.argv[2] + "ms_" + sys.argv[3] + "s"
    png_file = base_file + ".png"
    pdf_file = base_file + ".pdf"
    plt.legend()
    plt.savefig(png_file)
    plt.savefig(pdf_file)


    # plt.plot(bins_count[1:], cdf_middle_times, label="middle times", color="red")
    plt.plot(bins_count[1:], cdf_updated_times, "r--", label="Active till valid", color="red")
    # plt.plot(bins_count[1:], cdf_route_life, label="All Route Life", color="green")
    plt.plot(bins_count[1:], cdf_times_20, "m:", label="Active till within 20%")
    plt.plot(bins_count[1:], cdf_times_25, "k-.", label="Active till within 25%", color="black")
    
    plt.legend()
    base_file = sys.argv[1] + "_lasting_path_" + sys.argv[2] + "ms_" + sys.argv[3] + "s"
    png_file = base_file + ".png"
    pdf_file = base_file + ".pdf"
    plt.savefig(png_file)
    plt.savefig(pdf_file)