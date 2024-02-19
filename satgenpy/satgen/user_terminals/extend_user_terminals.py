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

from satgen.distance_tools import *
from .read_user_terminals import *


def extend_user_terminals(filename_user_terminals_basic_in, filename_user_terminals_out):
    user_terminals = read_user_terminals_basic(filename_user_terminals_basic_in)
    with open(filename_user_terminals_out, "w+") as f_out:
        for user_terminal in user_terminals:
            cartesian = geodetic2cartesian(
                float(user_terminal["latitude_degrees_str"]),
                float(user_terminal["longitude_degrees_str"]),
                user_terminal["elevation_m_float"]
            )
            f_out.write(
                "%d,%s,%f,%f,%f,%f,%f,%f,%f\n" % (
                    user_terminal["uid"],
                    user_terminal["name"],
                    float(user_terminal["latitude_degrees_str"]),
                    float(user_terminal["longitude_degrees_str"]),
                    user_terminal["elevation_m_float"],
                    cartesian[0],
                    cartesian[1],
                    cartesian[2],
                    user_terminal["demand"],
                )
            )
