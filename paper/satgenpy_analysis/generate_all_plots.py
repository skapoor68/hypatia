import exputil
import time

local_shell = exputil.LocalShell()
max_num_processes = 50

# Check that no screen is running
# if local_shell.count_screens() != 0:
#     print("There is a screen already running. "
#           "Please kill all screens before running this analysis script (killall screen).")
#     exit(1)

# Where to store all commands
commands_to_run = []

total_time = {"kuiper_630_isls_plus_grid_ground_stations_top_100_algorithm_free_one_only_over_isls" : 6000,
    "starlink_550_isls_plus_grid_ground_stations_top_100_algorithm_free_one_only_over_isls" : 6000,
    "telesat_1015_isls_plus_grid_ground_stations_top_100_algorithm_free_one_only_over_isls": 6600
    }

print("Generating commands for constellation comparison...")
for satgenpy_generated_constellation in [
    "kuiper_630_isls_plus_grid_ground_stations_top_100_algorithm_free_one_only_over_isls",
    "starlink_550_isls_plus_grid_ground_stations_top_100_algorithm_free_one_only_over_isls",
    "telesat_1015_isls_plus_grid_ground_stations_top_100_algorithm_free_one_only_over_isls"
]:
    for duration_s in [total_time[satgenpy_generated_constellation]]:
        list_update_interval_ms = [1000]

        # Path
        for update_interval_ms in list_update_interval_ms:

            command = "python generate_path_life_plots.py " + satgenpy_generated_constellation + " " + str(update_interval_ms) + " " + str(duration_s) 
            commands_to_run.append(command)

commands_to_run.append("python generate_path_length_ratio_plots.py")
commands_to_run.append("python generate_rtt_ratio_plots.py")
commands_to_run.append("python generate_path_variation_plots.py")
commands_to_run.append("python plot_instance.py")
commands_to_run.append("python plot_path_utilization.py")

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
