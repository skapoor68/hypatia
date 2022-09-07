# MIT License
#
# Copyright (c) 2020 Debopam Bhattacherjee
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

import math
import ephem
import numpy as np
import pandas as pd
import datetime
import csv
import sys

import folium
from folium import plugins
from folium.plugins import HeatMap
    
def main():

    f = "../../paper/satellite_networks_state/input_data/ground_stations_newyork_london_circular_bigger.basic.txt"
    points = []
    with open(f) as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',',quotechar='"',quoting=csv.QUOTE_ALL, skipinitialspace=True)
        for row in spamreader:
            point = {}
            point['pid'] = int(row[0])
            point['name'] = row[1]
            point['latitude_degrees_str'] = float(row[2])
            point['longitude_degrees_str'] = float(row[3])
            point['elevation_m_float'] = float(row[4])
            points.append(point)
    
    data = []
    
    for i in range(len(points)):
        point = points[i]
        lat = float(point["latitude_degrees_str"])
        lon = float(point["longitude_degrees_str"])
        
        data.append([lat, lon])

    # print(data)
    m = folium.Map([points[0]["latitude_degrees_str"], points[0]["longitude_degrees_str"]],  zoom_start=5)
    for datum in data:
        folium.CircleMarker(location=[datum[0], datum[1]],
                        radius=0.5,
                        weight=5).add_to(m)
    
    folium.LayerControl().add_to(m)
    f_name = "newyork_london.html"
    m.save(f_name)


if __name__ == "__main__":
    main()