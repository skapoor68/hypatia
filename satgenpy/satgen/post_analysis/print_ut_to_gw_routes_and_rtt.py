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
from satgen.tles import *
import exputil
import tempfile


def print_ut_to_gw_routes_and_rtt(base_output_dir, satellite_network_dir,
                        src, dst):

    # Local shell
    local_shell = exputil.LocalShell()

    # Default output dir assumes it is done manual
    pdf_dir = base_output_dir + "/pdf"
    data_dir = base_output_dir + "/data"
    local_shell.make_full_dir(pdf_dir)
    local_shell.make_full_dir(data_dir)

    # Variables (load in for each thread such that they don't interfere)
    ground_stations = read_ground_stations_extended(satellite_network_dir + "/ground_stations.txt")
    tles = read_tles(satellite_network_dir + "/tles.txt")
    satellites = tles["satellites"]
    # list_isls = read_isls(satellite_network_dir + "/isls.txt", len(satellites))
    # epoch = tles["epoch"]
    # description = exputil.PropertiesConfig(satellite_network_dir + "/description.txt")


    # Make plot
    src = src + len(satellites) + len(ground_stations)
    dst = dst + len(satellites)
    data_filename = data_dir + "/networkx_rtt_" + str(src) + "_to_" + str(dst) + ".txt"
    
    pdf_filename = pdf_dir + "/time_vs_networkx_rtt_" + str(src) + "_to_" + str(dst) + ".pdf"
    tf = tempfile.NamedTemporaryFile(delete=False)
    tf.close()
    local_shell.copy_file("plot/plot_time_vs_networkx_rtt.plt", tf.name)
    local_shell.sed_replace_in_file_plain(tf.name, "[OUTPUT-FILE]", pdf_filename)
    local_shell.sed_replace_in_file_plain(tf.name, "[DATA-FILE]", data_filename)
    local_shell.perfect_exec("gnuplot " + tf.name)
    print("Produced plot: " + pdf_filename)
    local_shell.remove(tf.name)


