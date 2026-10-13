from glob import glob

from setuptools import find_packages, setup


package_name = "psoc_edge_ai_ros"

setup(
    name=package_name,
    version="0.1.0",
    packages=find_packages(),
    data_files=[
        (
            "share/ament_index/resource_index/packages",
            [f"resource/{package_name}"],
        ),
        (f"share/{package_name}", ["package.xml"]),
        (f"share/{package_name}/launch", glob("launch/*.launch.py")),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    description="Control an LED kit from a separate PSoC Edge sensor kit via ROS 2.",
    license="Apache-2.0",
    entry_points={
        "console_scripts": [
            "sensor_serial = psoc_edge_ai_ros.sensor_serial_node:main",
            "motion_to_led = psoc_edge_ai_ros.motion_to_led_node:main",
            "led_serial = psoc_edge_ai_ros.led_serial_node:main",
        ],
    },
)
