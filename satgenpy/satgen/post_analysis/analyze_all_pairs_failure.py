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

from satgen.post_analysis.analyze_pair import analyze_pair
import threading

def analyze_all_pairs_failure(base_output_dir, satellite_network_dir, dynamic_state_update_interval_ms,
                      simulation_end_time_s, satgenpy_dir_with_ending_slash):
    routing_map = {}  # maps a (src, dst) pair to a list of lists of hops
    route_pairs = [(src, dst) for src in range(100) for dst in range(src + 1, 100)]
    num_threads = 128
    threads = []
    lock = threading.Lock()

    def analyze_route_chunk(route_chunk):
        local_routing_map = {}
        for src, dst in route_chunk:
            print(f"Analyzing route from {src + 1584} to {dst + 1584}")
            local_routing_map[(src, dst)] = analyze_pair(
                base_output_dir,
                satellite_network_dir,
                dynamic_state_update_interval_ms,
                simulation_end_time_s,
                src + 1584,
                dst + 1584,
                satgenpy_dir_with_ending_slash
            )
        with lock:
            routing_map.update(local_routing_map)

    # Divide the route pairs among the threads
    chunk_size = len(route_pairs) // num_threads + 1
    for i in range(0, len(route_pairs), chunk_size):
        route_chunk = route_pairs[i:i + chunk_size]
        thread = threading.Thread(target=analyze_route_chunk, args=(route_chunk,))
        threads.append(thread)
        thread.start()

    # Wait for all threads to complete
    for thread in threads:
        thread.join()
    
    total_paths = 0
    failed_paths = 0
    total_routes = 0
    failed_satellite = 842
    failed_isls = {tuple(sorted(pair)) for pair in [(842, 841), (842, 820), (842, 864), (842, 843), (843, 821), (843, 865), (843, 844)]}
    for route, paths in routing_map.items():
        total_routes += 1
        for path in paths:
            total_paths += 1
            for i in range(len(path) - 1):
                if tuple(sorted([path[i], path[i + 1]])) in failed_isls:
                    failed_paths += 1
                    break
            
    
    print("Paths going through failed satellite: " + str(failed_paths))
    print("Total paths: " + str(total_paths))
    print("Total routes: " + str(total_routes))
            
    