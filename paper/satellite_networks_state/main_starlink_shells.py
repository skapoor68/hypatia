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

import sys
import math
from main_shells_helper import MainShellsHelper

# WGS72 value; taken from https://geographiclib.sourceforge.io/html/NET/NETGeographicLib_8h_source.html
EARTH_RADIUS = 6378135.0

# GENERATION CONSTANTS

BASE_NAME = "starlink_current"
NICE_NAME = "Starlink-Current"

# STARLINK 550

ECCENTRICITY = 0.0000001  # Circular orbits are zero, but pyephem does not permit 0, so lowest possible value
ARG_OF_PERIGEE_DEGREE = 0.0
PHASE_DIFF = True
NUM_SHELLS = 5

################################################################
# The below constants are taken from Starlink's FCC filing as below:
# [1]: https://fcc.report/IBFS/SAT-MOD-20190830-00087
################################################################
# From https://fcc.report/IBFS/SAT-MOD-20181108-00083/1569860.pdf (minimum angle of elevation: 25 deg)
# ALTITUDES_M = [550000, 560000, 540000, 570000, 530000, 580000, 520000, 590000]  # Altitude ~550 km
# ALTITUDES_M = [550000, 1110000, 1130000, 1275000, 1325000]  # older starlink
ALTITUDES_M = [550000, 540000, 570000, 560000, 560000]  # current starlink
theta = math.radians(25)

def generate_constants():
    revs, gsl_lengths, isl_lengths = [], [], []
    for altitude in ALTITUDES_M:
        revs.append((math.sqrt((398600.5 * 1000) / (EARTH_RADIUS + altitude)) * 1000 * 86400) / (2 * math.pi * (EARTH_RADIUS + altitude)))
        cone_radius = math.sqrt((EARTH_RADIUS * math.sin(theta)) ** 2 + altitude ** 2  + 2 * EARTH_RADIUS * altitude) - EARTH_RADIUS * math.sin(theta)
        gsl_lengths.append(math.sqrt(math.pow(cone_radius, 2) + math.pow(altitude, 2)))
        # ISLs are not allowed to dip below 80 km altitude in order to avoid weather conditions
        isl_lengths.append(2 * math.sqrt(math.pow(EARTH_RADIUS + altitude, 2) - math.pow(EARTH_RADIUS + 80000, 2)))

    return revs, gsl_lengths, isl_lengths

MEAN_MOTION_REV_PER_DAY, MAX_GSL_LENGTH_M, MAX_ISL_LENGTH_M = generate_constants()
print(MEAN_MOTION_REV_PER_DAY, MAX_GSL_LENGTH_M, MAX_ISL_LENGTH_M)

# NUM_ORBS = [72,72,72,72,72,72,72,72]
# NUM_ORBS = [72,32,8,5,6] # older starlink
NUM_ORBS = [72,72,36,6,4] # current starlink

# NUM_SATS_PER_ORB = [22,22,22,22,22,22,22,22]
# NUM_SATS_PER_ORB = [22,50,50,75,75] # older starlink
NUM_SATS_PER_ORB = [22,22,20,58,43] # current starlink

# INCLINATION_DEGREE = [53,53,53,53,53,53,53,53] # same
# INCLINATION_DEGREE = [53,27,72,13,40,62,82,53] # different
# INCLINATION_DEGREE = [53,53.8,74,81,70] # older starlink
INCLINATION_DEGREE = [53,53.2,70,97.6,97.6] # current starlink

################################################################


main_helper = MainShellsHelper(
    BASE_NAME,
    NICE_NAME,
    NUM_SHELLS,
    ECCENTRICITY,
    ARG_OF_PERIGEE_DEGREE,
    PHASE_DIFF,
    MEAN_MOTION_REV_PER_DAY[:NUM_SHELLS],
    ALTITUDES_M[:NUM_SHELLS],
    MAX_GSL_LENGTH_M[:NUM_SHELLS],
    MAX_ISL_LENGTH_M[:NUM_SHELLS],
    NUM_ORBS[:NUM_SHELLS],
    NUM_SATS_PER_ORB[:NUM_SHELLS],
    INCLINATION_DEGREE[:NUM_SHELLS],
)


def main():
    args = sys.argv[1:]
    if len(args) != 4:
        print("Must supply exactly four arguments")
        print("Usage: python main_starlink_shells.py [duration (s)] [time step (ms)] "
              "[isls_plus_grid / isls_none] "
              "[ground_stations_{top_100, paris_moscow_grid}] "
              "[algorithm_{free_one_only_over_isls, free_one_only_gs_relays, paired_many_only_over_isls}] "
              "[user_terminals_{atlanta, global}] "
              "[num_user_terminals]")
        exit(1)
    else:
        main_helper.calculate(
            "gen_data",
            args[0], # isls_plus_grid / isls_none
            args[1], # ground_stations_{top_100, paris_moscow_grid}
            args[2], # user_terminals_{atlanta, global}
            int(args[3]) # num_user_terminals
        )

if __name__ == "__main__":
    main()
