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

import exputil
import time
import os

local_shell = exputil.LocalShell()
max_num_processes = 40

# Create graphs directory if not present already
if not os.path.isdir("graphs"):
    os.makedirs("graphs", exist_ok=True)

if not os.path.isdir("graphs/command_logs"):
    os.makedirs("graphs/command_logs", exist_ok=True)

# Where to store all commands
commands_to_run = []

# this value should correspond to the number of cores
num_shells = 4 # Ensure this value is thread friendly
idx = 0
# Manual
print("printing all different graphs")
for satgenpy_generated_constellation in [
    "starlink_current_5shells_isls_plus_grid_ground_stations_starlink",
]:
    oracle_type = 'multiple_gsls' # 'single_gsl' or 'multiple_gsls'
    update_interval_ms = 1000
    duration_s = 60
    failure_type = 'None' # "None" or 'Betweenness' or 'Random'
    num_failures = 0
    print(satgenpy_generated_constellation)

    interval = duration_s // num_shells
    # interval = 2
    for start_time in range(0, 0 + duration_s, interval):
        commands_to_run.append(
            "cd ../../satgenpy; "
            "python -m satgen.post_analysis.oracle_%s "
            "../paper/satgenpy_analysis/graphs ../paper/satellite_networks_state/gen_data/%s %d %d %d %s %d"
            " > ../paper/satgenpy_analysis/graphs/command_logs/oracle_%s_%s_%dms_for_%ds_%d.log "
            "2>&1" % (
                oracle_type,
                satgenpy_generated_constellation, update_interval_ms, start_time, start_time + interval, failure_type, num_failures,
                oracle_type, satgenpy_generated_constellation, update_interval_ms, duration_s, start_time
            )
        )

    idx += 1

# Run the commands
print("Running commands (at most %d in parallel)..." % max_num_processes)
for i in range(len(commands_to_run)):
    print("Starting command %d out of %d: %s" % (i + 1, len(commands_to_run), commands_to_run[i]))
    local_shell.detached_exec(commands_to_run[i])
    while local_shell.count_screens() >= max_num_processes:
        time.sleep(2)

# Awaiting final completion before exiting
print("Waiting completion of the last %d..." % max_num_processes)
while local_shell.count_screens() > 0:
    time.sleep(2)
print("Finished.")
