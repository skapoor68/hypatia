import sys
sys.path.append("../../satgenpy")
import satgen
import os
import numpy as np
from sgp4.api import Satrec, jday

NICE_NAME = "Starlink"
NUM_ORBS = 72
NUM_SATS_PER_ORB = 22
INCLINATION_DEGREE = 53
ECCENTRICITY = 0.0000001  # Circular orbits are zero, but pyephem does not permit 0, so lowest possible value
ARG_OF_PERIGEE_DEGREE = 0.0
MEAN_MOTION_REV_PER_DAY = 15.19  # Altitude ~550 km

lat_values = [i for i in range(60)]
def generate_groundstations(lon = -80):
    ground_stations = []
    i = 0

    for lat in lat_values:
        ground_station = {}
        ground_station['gid'] = i
        ground_station['latitude_degrees_str'] = str(lat)
        ground_station['longitude_degrees_str'] = str(lon)
        ground_station['name'] = "gid" + str(i)
        ground_station['elevation_m_float'] = 0
        ground_station['cartesian_x'], ground_station['cartesian_y'], ground_station['cartesian_z'] = satgen.geodetic2cartesian(lat, lon, 0)
        ground_stations.append(ground_station)
        i = i + 1

    return ground_stations

def read_tles_sgp4(filename_tles):
    satellites = []
    with open(filename_tles, 'r') as f:
        n_orbits, n_sats_per_orbit = [int(n) for n in f.readline().split()]
        universal_epoch = None
        i = 0
        for tles_line_1 in f:
            tles_line_2 = f.readline()
            tles_line_3 = f.readline()

            # Retrieve name and identifier
            name = tles_line_1
            sid = int(name.split()[1])
            if sid != i:
                raise ValueError("Satellite identifier is not increasing by one each line")
            i += 1

            satellite = {}
            satellite['line1'] = tles_line_2
            satellite['line2'] = tles_line_3

            satellites.append(satellite)

    return satellites

if __name__ == '__main__':
    np.set_printoptions(threshold=sys.maxsize)
    output_generated_data_dir = "phase_expts"

    ground_stations = generate_groundstations()
    # ground_stations = satgen.read_ground_stations_extended("../satellite_networks_state/gen_data/starlink_550_isls_plus_grid_ground_stations_top_100_algorithm_free_one_only_over_isls/ground_stations.txt")
    gss = []
    for ground_station in ground_stations:
        gss.append(np.array([ground_station["cartesian_x"], ground_station["cartesian_y"], ground_station["cartesian_z"]]))

    gss = np.array(gss) / 1000
    
    for phase in range(int(sys.argv[1]), int(sys.argv[2])):
        tle_fname = output_generated_data_dir + "/" + str(phase) + "_tles.txt"
        # satgen.generate_tles_from_scratch_manual(
        #     tle_fname,
        #     NICE_NAME,
        #     NUM_ORBS,
        #     NUM_SATS_PER_ORB,
        #     phase / NUM_ORBS,
        #     INCLINATION_DEGREE,
        #     ECCENTRICITY,
        #     ARG_OF_PERIGEE_DEGREE,
        #     MEAN_MOTION_REV_PER_DAY
        # )

        tles = satgen.read_tles(tle_fname)
        satellites = read_tles_sgp4(tle_fname)
        epoch = tles["epoch"]
        min_distances = np.zeros((len(ground_stations),6000))
        for tt in range(6000):
            # if tt % 100 == 0:
            #     print(tt)
            t = epoch + tt / 86400
            current_time = t.tt.datetime
            jd, fr = jday(current_time.year, current_time.month, current_time.day, current_time.hour, current_time.minute, current_time.second)
            # print(t)
            

            sat_locations = np.empty((len(satellites), 3))
            for i, sat in enumerate(satellites):
                satellite = Satrec.twoline2rv(sat['line1'], sat['line2'])
                e, location, velocity = satellite.sgp4(jd, fr)
                sat_locations[i] = np.array(location)
            
            distances = np.sum((gss[:, None] - sat_locations[None, :]) ** 2, -1) ** 0.5
            
            min_distances[:, tt] = np.min(distances, axis=1)
            
        print(phase, repr(min_distances.flatten()), sep=',')