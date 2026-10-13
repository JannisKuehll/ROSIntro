# Two PSoC Edge boards with ROS 2

This folder has two MicroPython programs and one ROS 2 workspace. Nothing in
the ros2_ws directory is copied to the boards.

micropython/sensor_board/main.py runs on the Sensor Board. It reads the BMI270
and prints ACCEL,x,y,z ten times per second.
micropython/led_board/main.py runs on the LED Board. It receives LED,ON or
LED,BLINK and controls the onboard LED.

ros2_ws/src/psoc_edge_ai_ros contains three Ubuntu/WSL2 ROS nodes:
sensor_serial_node.py reads the Sensor Board on one serial port and publishes
/psoc/acceleration.
motion_to_led_node.py reads that topic and publishes /psoc/moving.
led_serial_node.py reads /psoc/moving and writes commands to the LED Board on
the other serial port. launch/two_psoc_demo.launch.py starts all three nodes.

## Preparation

Install MicroPython on both kits and install the BMI270 MicroPython driver on
the Sensor Board. In a Windows terminal, while the boards still have Windows
COM ports, copy each main.py to its corresponding kit with mpremote:

mpremote connect <sensor-COM-port> mip install github:jposada202020/MicroPython_BMI270
mpremote connect <sensor-COM-port> fs cp micropython/sensor_board/main.py :main.py
mpremote connect <led-COM-port> fs cp micropython/led_board/main.py :main.py

Disconnect any serial terminals and mpremote sessions. Attach both USB
devices to WSL2 with usbipd. Identify the actual Sensor and LED device paths
in Ubuntu; the /dev/ttyACM numbers may change between boots.

In Ubuntu, install the ROS 2 distribution you use, colcon and pyserial.
For the ROS 2 Lyrical setup used here, open Ubuntu in the ROSIntro folder
(for example, cd to it under /mnt/c) and run:

sudo apt update
sudo apt install -y python3-colcon-common-extensions python3-serial
source /opt/ros/lyrical/setup.bash
cd ros2_ws
colcon build --symlink-install
source install/setup.bash
ros2 launch psoc_edge_ai_ros two_psoc_demo.launch.py sensor_port:=/dev/ttyACM0 led_port:=/dev/ttyACM1

Pass the real Linux port of the Sensor Board as sensor_port and the LED Board
as led_port. In a second sourced Ubuntu terminal, use ros2 topic echo
/psoc/acceleration and
ros2 topic echo /psoc/moving to watch the data flow.

No button press is needed: both MicroPython programs start on boot. The LED
starts continuously on and blinks at approximately 2 Hz when ROS detects
movement. Once the Sensor Board lies still, the LED stays on again.

This example uses direct WSL2 USB forwarding only. A hardware test with two
working kits is still required before publishing it as a verified demo.
