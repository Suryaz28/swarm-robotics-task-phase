# Task 3: Simulated Drone Telemetry

Three ROS 2 Jazzy Python nodes exchange simulated sensor readings, status, and warnings. No real drone or simulator is used.

## Architecture

```text
/drone_sensor_publisher -- /drone/altitude (Float32) ------\
                        -- /drone/battery (Float32) -------+--> /drone_telemetry_monitor
                        -- /drone/temperature (Float32) ---/               |
                                                                /drone/status (String)
                                                                           |
                                                               /drone_warning_publisher
                                                                           |
                                                               /drone/warnings (String)
```

`drone_monitoring/package.xml`, `setup.py`, and `setup.cfg` define the ROS package and executable entry points. The inner `drone_monitoring/` directory contains the node programs. `test/test_logic.py` tests the status and warning logic.

## Implementation

The sensor node publishes three values every second. By default altitude and temperature vary smoothly and battery drops by 0.1 percentage points per second. Initial values and whether to vary them can be changed with ROS parameters. The monitor remembers the latest readings and publishes a status at 1 Hz. It waits until all three values have arrived, and can report multiple conditions. Battery below 20%, temperature above 60 C, and altitude above 30 m are considered abnormal; values exactly on the thresholds are normal. The warning node subscribes to status and publishes and logs the corresponding warnings. Detecting a publisher that stops after sending data is not implemented; that is optional in the task.

## Build

First create a workspace, copy this package into its `src` directory, then build. These commands assume `Task3` is on the Desktop as prepared:

```bash
source /opt/ros/jazzy/setup.bash
mkdir -p ~/ros2_ws/src
cp -r "$HOME/Desktop/swarm robotics taskphase/Task3/drone_monitoring" ~/ros2_ws/src/
cd ~/ros2_ws
colcon build --packages-select drone_monitoring
source install/setup.bash
```

If a package already exists in `~/ros2_ws/src/drone_monitoring`, inspect it before copying; remove or rename the old copy yourself to avoid nesting or overwriting unintended files. After editing code in Task3, repeat the copy/build step so the workspace uses the latest version.

## Run

Open three terminals. In **each**, run:

```bash
source /opt/ros/jazzy/setup.bash
source ~/ros2_ws/install/setup.bash
```

Run one command in each terminal:

```bash
ros2 run drone_monitoring drone_sensor_publisher
ros2 run drone_monitoring drone_telemetry_monitor
ros2 run drone_monitoring drone_warning_publisher
```

Stop each with Ctrl+C. In another sourced terminal, inspect the running system:

```bash
ros2 node list
ros2 topic list
ros2 topic info /drone/altitude
ros2 topic echo /drone/battery
ros2 topic hz /drone/altitude
ros2 node info /drone_telemetry_monitor
rqt_graph
```

Stop `echo` and `hz` with Ctrl+C. Refresh the graph if necessary, and capture it while all nodes are running.

## Test scenarios

Keep the monitor and warning nodes running. For each row, stop and restart the sensor publisher using the command shown; `vary_readings:=false` keeps readings fixed. Start with base defaults altitude 15 m, battery 100%, temperature 35 C. The following scenarios were run in ROS 2; screenshots are linked below.

| Case | Sensor publisher command after `ros2 run drone_monitoring drone_sensor_publisher` | Expected |
|---|---|---|
| Normal | `--ros-args -p vary_readings:=false` | NORMAL; No active warnings |
| Low battery | `--ros-args -p vary_readings:=false -p initial_battery:=10.0` | LOW BATTERY |
| Overheating | `--ros-args -p vary_readings:=false -p initial_temperature:=65.0` | OVERHEATING |
| High altitude | `--ros-args -p vary_readings:=false -p initial_altitude:=35.0` | ALTITUDE LIMIT EXCEEDED |
| Multiple | `--ros-args -p vary_readings:=false -p initial_battery:=10.0 -p initial_temperature:=65.0 -p initial_altitude:=35.0` | All three warnings |
| Waiting | Stop all nodes; restart monitor and warning only | WAITING FOR SENSOR DATA; Waiting for telemetry |

For example, the low-battery command is:

```bash
ros2 run drone_monitoring drone_sensor_publisher --ros-args -p vary_readings:=false -p initial_battery:=10.0
```

Restart the monitor for the waiting test: it intentionally keeps the latest value after a sensor stops.

### Results and screenshots

All six scenarios produced the expected status or warning during the run:

- [Normal operation](screenshots/normal_operation.png): changing sensor values and NORMAL status.
- [Low battery status](screenshots/Pasted%20image.png) and [battery warning](screenshots/Screenshot%20from%202026-11-08%2020-03-27.png).
- [Overheating](screenshots/Pasted%20image%20%282%29.png).
- [Altitude limit exceeded](screenshots/Pasted%20image%20%283%29.png).
- [Multiple warnings](screenshots/Pasted%20image%20%284%29.png).
- [Waiting for sensor data](screenshots/Pasted%20image%20%285%29.png).
- [ROS 2 communication graph](screenshots/Pasted%20image%20%286%29.png).

The package built successfully. `ros2 node list` showed all three nodes; `ros2 topic list` showed the five drone topics. The altitude topic used `std_msgs/msg/Float32` with one publisher and one subscriber. Battery messages were observed with `ros2 topic echo`, and `ros2 topic hz /drone/altitude` reported 1.000 Hz. Node information showed the monitor's three sensor subscriptions and status publisher. The graph shows sensor topics feeding the monitor, the status feeding the warning node, and its warnings output. The automated logic tests also passed.

## Challenges and learning

A monitor must not interpret missing initial readings as normal. Multiple limit violations need to be preserved rather than handled as mutually exclusive alternatives. ROS topics use separate message types for numerical readings and text status; timers control the publishing interval. The graph initially appeared empty and did not show the warnings topic. Refreshing it, selecting Nodes/Topics (all), and showing leaf topics and dead sinks revealed the complete data flow. The workspace needed to be sourced in each terminal before launching the nodes.
