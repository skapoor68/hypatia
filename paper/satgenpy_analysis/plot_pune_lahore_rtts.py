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

total_time = 60

latencies = np.array([6.267170462,6.262904803,6.72239539,6.710727526,6.699247084,6.687953854,6.676847838,6.665929451,6.655198277,6.644654108,6.634297568,6.624128241,6.614147378,6.604353519,6.594747916,6.585330359,12.1893739,12.19767593,12.20629805,12.21524077,12.22450374,12.23408444,12.24398789,12.25421354,12.26475414,12.27561472,12.28679748,12.29829903,12.31011917,12.32225593,12.33471475,12.34748485,12.36057659,12.37398498,12.38770929,12.40174685,12.41610139,12.43076701,12.44575066,12.46104016,12.47664604,12.49255986,12.50878365,12.525317,12.54215649,12.55930422,12.86328968,15.5421949,15.54308636,15.5443871,15.5461031,15.54822912,15.55077025,15.55372862,15.55709863,15.56088349,15.56509194,15.56971766,6.114295327,6.109750933]) * 2

if __name__ == '__main__':
    plt.figure(figsize=(6.4,3.2))
    x = np.arange(0, total_time)
    plt.plot(x, latencies, "m-", label="Pune-Lahore RTTs")

    
    plt.ylabel("RTT (ms)", fontsize=18)
    plt.xlabel("Time (seconds)", fontsize=18)
    
    
    plt.yticks(fontsize=14)
    plt.legend(fontsize=14, frameon=False)
    plt.xticks([0,10,20,30,40,50,60], fontsize=14)
    plt.grid(linewidth=0.5, linestyle=':')
    plt.tight_layout()

            
    base_file = "paper_plots/puneLahore"
    png_file = base_file + ".png"
    pdf_file = base_file + ".pdf"
    plt.savefig(png_file)
    plt.savefig(pdf_file)