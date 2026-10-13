"""Start all three ROS nodes with one serial port per board."""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description() -> LaunchDescription:
    return LaunchDescription(
        [
            DeclareLaunchArgument("sensor_port", default_value="/dev/ttyACM0"),
            DeclareLaunchArgument("led_port", default_value="/dev/ttyACM1"),
            Node(
                package="psoc_edge_ai_ros",
                executable="sensor_serial",
                parameters=[{"port": LaunchConfiguration("sensor_port")}],
                output="screen",
            ),
            Node(
                package="psoc_edge_ai_ros",
                executable="motion_to_led",
                output="screen",
            ),
            Node(
                package="psoc_edge_ai_ros",
                executable="led_serial",
                parameters=[{"port": LaunchConfiguration("led_port")}],
                output="screen",
            ),
        ]
    )
