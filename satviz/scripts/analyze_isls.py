import exputil
import sys
sys.path.append("../../satgenpy")
import math
from satgen import *
import networkx as nx
import numpy as np
import json
import time

def main():    
    satellite_network_dir = "./gen_data/starlink_550_isls_plus_grid_ground_stations_top_100_algorithm_free_one_only_over_isls"
    tles = read_tles(satellite_network_dir + "/tles.txt")
    satellites = tles["satellites"]
    list_isls = read_isls(satellite_network_dir + "/isls.txt", len(satellites))
    epoch = tles["epoch"]

    for (a, b) in list_isls:

        # ISLs are not permitted to exceed their maximum distance
        # TODO: Technically, they can (could just be ignored by forwarding state calculation),
        # TODO: but practically, defining a permanent ISL between two satellites which
        # TODO: can go out of distance is generally unwanted

        distances = []
        for i in range(200):
            t = epoch + i / 86400
            sat_distance_m = distance_m_between_satellites(satellites[a], satellites[b], str(epoch), str(t))
            if sat_distance_m > MAX_ISL_LENGTH_M:
                distances.append(-1)
            else:
                distances.append(sat_distance_m)

        print(a,b,distances)


if __name__ == "__main__":
    main()
