file1 = open('/home/robin/hypatia/paper/satellite_networks_state/input_data/user_terminals_atl_5000.txt', 'r')
lines = file1.readlines()



with open('/home/robin/hypatia/paper/satellite_networks_state/input_data/user_terminals_atl_5000_no_demand.txt', 'w') as file2:
    for line in lines:
        split = line.split(',')
        line_without_demand = split[:-1]
        file2.write(','.join(line_without_demand) + '\n')

