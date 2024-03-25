# Hypatia

## Steps to run this fork (for Starlink's first shell)
1. Run 
```
bash run_max_flow.sh
```
with parameters specified in the script.

2. Modify `global_variables.py`to configure ISLs, GSLs, user terminal settings.

3. The resulting network flow is generated in the paper/satellite_networks_state/gen_data


## Getting started

1. System setup:
   - Python version 3.7+
   - Recent Linux operating system (e.g., Ubuntu 18+)
   - It is strongly recommended to use a python environment(like conda or virtualenv) to manage the dependencies.
     ```
     conda create --name ai_env python=3.7 -y
     ```

2. Install dependencies:
   ```
   bash hypatia_install_dependencies.sh
   ```
   Some of the dependencies may not get installed through the script directly. In such cases, download them separately.
   
3. Build all four modules (as far as possible):
   ```
   bash hypatia_build.sh
   ```
   
4. Run tests:
   ```
   bash hypatia_run_tests.sh
   ```

5. The reproduction of the paper is essentially the tutorial for Hypatia.
   Please navigate to `paper/README.md`.

### Visualizations
Most of the visualizations in the paper are available [here](https://leosatsim.github.io/).
All of the visualizations can be regenerated using scripts available in `satviz` as discussed above.

Below are some examples of visualizations:

- SpaceX Starlink 5-shell side-view (left) and top-view (right). To know the configuration of the shells, click [here](https://leosatsim.github.io/).

  <a href="#"><img alt="Starlink side-view" src="https://raw.githubusercontent.com/leosatsim/leosatsim.github.io/master/images/Starlink_side_view.png" width="45%" /></a>
  <a href="#"><img alt="Starlink top-view" src="https://raw.githubusercontent.com/leosatsim/leosatsim.github.io/master/images/Starlink_top_view.png" width="45%" /></a>

- Amazon Kuiper 3-shell side-view (left) and top-view (right). To know the configuration of the shells, click [here](https://leosatsim.github.io/kuiper.html).

  <a href="#"><img alt="Kuiper side-view" src="https://raw.githubusercontent.com/leosatsim/leosatsim.github.io/master/images/Kuiper_side_view.png" width="45%" /></a>
  <a href="#"><img alt="Kuiper top-view" src="https://raw.githubusercontent.com/leosatsim/leosatsim.github.io/master/images/Kuiper_top_view.png" width="45%" /></a>

- RTT changes over time between Paris and Luanda over Starlink 1st shell. Left: 117 ms, Right: 85 ms. Click on the images for 3D interactive visualizations.

  <a href="https://leosatsim.github.io/starlink_550_path_Paris_1608_Luanda_1650_46800.html"><img alt="starlink_paris_luanda_long" src="https://raw.githubusercontent.com/leosatsim/leosatsim.github.io/master/images/starlink_paris_luanda_long.png" width="35%" /></a>
  <a href="https://leosatsim.github.io/starlink_550_path_Paris_1608_Luanda_1650_139900.html"><img alt="starlink_paris_luanda_short" src="https://raw.githubusercontent.com/leosatsim/leosatsim.github.io/master/images/starlink_paris_luanda_short.png" width="35%" /></a>

- Link utilizations change over time, even with the input traffic being static. For Kuiper 1st shell, path between Chicago and Zhengzhou at 10s (top) and 150s (bottom). Click on the images for 3D interactive visualizations.

  <a href="https://leosatsim.github.io/kuiper_630_path_wise_util_Chicago_1193_Zhengzhou_1243_10000.html"><img alt="kuiper_Chicago_Zhengzhou_10s" src="https://raw.githubusercontent.com/leosatsim/leosatsim.github.io/master/images/kuiper_Chicago_Zhengzhou_10s.png" width="90%" /></a>
  <a href="https://leosatsim.github.io/kuiper_630_path_wise_util_Chicago_1193_Zhengzhou_1243_150000.html"><img alt="kuiper_Chicago_Zhengzhou_150s" src="https://raw.githubusercontent.com/leosatsim/leosatsim.github.io/master/images/kuiper_Chicago_Zhengzhou_150s.png" width="90%" /></a>
