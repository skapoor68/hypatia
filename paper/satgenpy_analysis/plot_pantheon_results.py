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

if __name__ == '__main__':
    nice_names = ["204mbps_variable_rtt", "48mbps_variable_rtt", "Variable bw\n6 ms delay", "variable_bw_16ms", "n6 mVariableay", ""]
    protocols = ["BBR", "Cubic", "PCC", "Vegas", "Vivace"]
    utilization = {}
    utilization["BBR"] = {"204mbps link\nVariable Delay":95.4, "48mbps link\nVariable Delay":97.9, "Variable bw\n6 ms delay":96.5, "Variable bw\n16 ms delay":90.1, "Variable bw\nVariable delay":95.9}
    utilization["Cubic"] = {"204mbps link\nVariable Delay":61.8, "48mbps link\nVariable Delay":99.5, "Variable bw\n6 ms delay":75.7, "Variable bw\n16 ms delay":55.4, "Variable bw\nVariable delay":68.64}
    utilization["PCC"] = {"204mbps link\nVariable Delay":93.5, "48mbps link\nVariable Delay":78, "Variable bw\n6 ms delay":63.76, "Variable bw\n16 ms delay":70.6, "Variable bw\nVariable delay":71.3}
    utilization["Vegas"] = {"204mbps link\nVariable Delay":10.1, "48mbps link\nVariable Delay":31.3, "Variable bw\n6 ms delay":53.4, "Variable bw\n16 ms delay":45, "Variable bw\nVariable delay":37.8}
    utilization["Vivace"] = {"204mbps link\nVariable Delay":86.8, "48mbps link\nVariable Delay":89, "Variable bw\n6 ms delay":72.8, "Variable bw\n16 ms delay":64.4, "Variable bw\nVariable delay":73.8}


    delay = {}
    delay["BBR"] = {"204mbps link\nVariable Delay":18.371, "48mbps link\nVariable Delay":28.193, "Variable bw\n6 ms delay":19.831, "Variable bw\n16 ms delay":29.743, "Variable bw\nVariable delay":26.474}
    delay["Cubic"] = {"204mbps link\nVariable Delay":16.725, "48mbps link\nVariable Delay":26.4, "Variable bw\n6 ms delay":18.434, "Variable bw\n16 ms delay":28.722, "Variable bw\nVariable delay":25.143}
    delay["PCC"] = {"204mbps link\nVariable Delay":16.302, "48mbps link\nVariable Delay":16.076, "Variable bw\n6 ms delay":7.331, "Variable bw\n16 ms delay":26.1, "Variable bw\nVariable delay":16.535}
    delay["Vegas"] = {"204mbps link\nVariable Delay":13.608, "48mbps link\nVariable Delay":13.563, "Variable bw\n6 ms delay":9.45, "Variable bw\n16 ms delay":19.518, "Variable bw\nVariable delay":16.309}
    delay["Vivace"] = {"204mbps link\nVariable Delay":16.208, "48mbps link\nVariable Delay":16.152, "Variable bw\n6 ms delay":7.584, "Variable bw\n16 ms delay":19.668, "Variable bw\nVariable delay":16.096}
    
    fig, (ax1, ax2) = plt.subplots(2,1)

    plt_lines = {"BBR":"b-", "Cubic": "r--", "PCC": "g:", "Vegas": "k-", "Vivace": "m-."}
    for protocol in protocols:
        ax1.plot(list(utilization[protocol].keys()), list(utilization[protocol].values()), plt_lines[protocol], label=protocol)
        ax2.plot(list(delay[protocol].keys()), list(delay[protocol].values()), plt_lines[protocol], label=protocol)

    ax1.set_ylabel("Utilization %", fontsize=17)
    ax2.set_ylabel("Delay", fontsize=18)
    # ax2.set_xlabel("Scenario", fontsize=18)

    ax1.set_xticks([])
    
    
    base_file = "paper_plots/pantheon"
    png_file = base_file + ".png"
    pdf_file = base_file + ".pdf"
    plt.legend(fontsize=14, bbox_to_anchor=(0,-0.7), loc="lower left", ncol=3)
    # plt.grid(linewidth=0.5, linestyle=':')
    plt.tight_layout(rect=[0,0,1,1])
    plt.savefig(png_file)
    plt.savefig(pdf_file)