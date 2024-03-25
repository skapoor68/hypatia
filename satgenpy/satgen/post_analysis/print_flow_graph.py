# The MIT License (MIT)
#
# Copyright (c) 2020 ETH Zurich
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from .graph_tools import *
from satgen.isls import *
from satgen.ground_stations import *
from satgen.user_terminals import *
from satgen.tles import *
import exputil
import tempfile
import matplotlib.pyplot as plt
import pandas as pd

def print_flow_graph(base_output_dir, satellite_network_dir, dynamic_state_update_interval_ms, simulation_end_time_s):
    
    local_shell = exputil.LocalShell()

    data_dir = base_output_dir + "/data"
    pdf_dir = base_output_dir + "/pdf"
    user_terminals = read_user_terminals_extended(satellite_network_dir + "/user_terminals.txt")
    local_shell.make_full_dir(pdf_dir)
    local_shell.make_full_dir(data_dir)

    data_filename = data_dir + "/networkx_all_flow_" + str(dynamic_state_update_interval_ms) +"ms_for_" + str(simulation_end_time_s) + "s" + ".txt"

    pdf_dir = base_output_dir + "/pdf"
    pdf_filename = pdf_dir + "/time_vs_networkx_flow_" + "ut_capacity_" + str(user_terminal_gsl_capacity)+ "_mbps_" + "gs_capacity_" + str(ground_station_gsl_capacity) + "_mbps_" + str(dynamic_state_update_interval_ms) + "ms_for_" + str(simulation_end_time_s) + "s" + ".pdf"
    tf = tempfile.NamedTemporaryFile(delete=False)
    tf.close()
    local_shell.copy_file("plot/plot_time_vs_networkx_flow.plt", tf.name)
    local_shell.sed_replace_in_file_plain(tf.name, "[OUTPUT-FILE]", pdf_filename)
    local_shell.sed_replace_in_file_plain(tf.name, "[DATA-FILE]", data_filename)

    ut_demand_total = 0
    for ut in user_terminals:
        ut_demand_total += ut_default_demand
    local_shell.sed_replace_in_file_plain(tf.name, "UT_DEMAND_TOTAL", str(ut_demand_total))

    local_shell.perfect_exec("gnuplot " + tf.name)
    print("Total UT demand:", ut_demand_total)
    print("Produced plot: " + pdf_filename)
    local_shell.remove(tf.name)