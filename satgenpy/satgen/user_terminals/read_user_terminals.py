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


def read_user_terminals_basic(filename_user_terminals_basic):
    """
    Reads user terminals from the input file.

    :param filename_user_terminals_basic: Filename of user terminals basic (typically /path/to/user_terminals.txt)

    :return: List of user terminals
    """
    user_terminals_basic = []
    gid = 0
    with open(filename_user_terminals_basic, 'r') as f:
        for line in f:
            split = line.split(',')
            if len(split) != 6:
                raise ValueError("Basic user terminal file has 6 columns")
            if int(split[0]) != gid:
                raise ValueError("user terminal id must increment each line")
            ground_station_basic = {
                "gid": gid,
                "name": split[1],
                "latitude_degrees_str": split[2],
                "longitude_degrees_str": split[3],
                "elevation_m_float": float(split[4]),
                "demand" : float(split[5]),
            }
            user_terminals_basic.append(ground_station_basic)
            gid += 1
    return user_terminals_basic


def read_user_terminals_extended(filename_user_terminals_extended):
    """
    Reads user terminals from the input file.

    :param filename_user_terminals_extended: Filename of user terminals basic (typically /path/to/user_terminals.txt)

    :return: List of user terminals
    """
    user_terminals_extended = []
    gid = 0
    with open(filename_user_terminals_extended, 'r') as f:
        for line in f:
            split = line.split(',')
            if len(split) != 9:
                raise ValueError("Extended user terminal file has 9 columns: " + line)
            if int(split[0]) != gid:
                raise ValueError("user terminal id must increment each line")
            user_terminal_basic = {
                "gid": gid,
                "name": split[1],
                "latitude_degrees_str": split[2],
                "longitude_degrees_str": split[3],
                "elevation_m_float": float(split[4]),
                "cartesian_x": float(split[5]),
                "cartesian_y": float(split[6]),
                "cartesian_z": float(split[7]),
                "demand" : float(split[8]),
            }
            user_terminals_extended.append(user_terminal_basic)
            gid += 1
    return user_terminals_extended
