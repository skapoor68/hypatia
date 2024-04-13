user_terminal_gsl_capacity = 1000 # 1 Gbps - proxy for 100 households with 100Mbps demand
ut_default_demand = 1000 # 1 Gbps - proxy for 100 households with 100Mbps demand
ut_gsl_max_capacity = 20000 # 20 Gbps, same as GS - Satellite links
ground_station_gsl_capacity = 20000 # Ground station link to Satellite capacity, 20 Gbps
ground_station_max_sat_connections = 40
ground_station_capacity = ground_station_gsl_capacity * ground_station_max_sat_connections # Ground station total capacity, 80 Gbps
isl_capacity = 100000 # 100 Gbps
satellite_handoff_seconds = 15 # 15 seconds
satellite_max_users = 10000
isl_max_connections = 4
satellite_max_capacity = isl_max_connections * isl_capacity # 100 Gbps
oversubscription_ratio = 1 # The ratio between maximum possible user traffic and the capacity that the network can support