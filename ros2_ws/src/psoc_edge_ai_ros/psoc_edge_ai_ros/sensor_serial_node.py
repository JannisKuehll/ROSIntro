"""Publish acceleration lines from the sensor board as ROS messages."""

import math

import rclpy
import serial
from geometry_msgs.msg import Vector3Stamped
from rclpy.node import Node


def parse_acceleration(line: str) -> tuple[float, float, float] | None:
    """Return three finite values for a valid ACCEL line."""
    fields = line.strip().split(",")
    if len(fields) != 4 or fields[0] != "ACCEL":
        return None
    try:
        values = tuple(float(value) for value in fields[1:])
    except ValueError:
        return None
    if not all(math.isfinite(value) for value in values):
        return None
    return values


class SensorSerialNode(Node):
    def __init__(self) -> None:
        super().__init__("sensor_serial_node")
        self.declare_parameter("port", "/dev/ttyACM0")
        port = self.get_parameter("port").value
        if not isinstance(port, str) or not port:
            raise ValueError("sensor_port must be a nonempty serial device path")

        # Nonblocking serial reads keep ROS callbacks responsive.
        self._serial = serial.Serial(port, baudrate=115200, timeout=0)
        self.get_logger().info(f"Reading Sensor Board on {port}")
        self._buffer = bytearray()
        self._publisher = self.create_publisher(
            Vector3Stamped, "/psoc/acceleration", 10
        )
        self._timer = self.create_timer(0.02, self._read_sensor)

    def _read_sensor(self) -> None:
        try:
            self._buffer.extend(self._serial.read(self._serial.in_waiting or 1))
        except serial.SerialException as exc:
            raise RuntimeError("Sensor Board serial read failed") from exc

        while b"\n" in self._buffer:
            raw_line, _, remainder = self._buffer.partition(b"\n")
            self._buffer = bytearray(remainder)
            line = raw_line.decode("ascii", errors="replace").strip()
            if line == "READY,SENSOR":
                self.get_logger().info("Sensor Board is ready")
                continue
            if not line:
                continue
            acceleration = parse_acceleration(line)
            if acceleration is None:
                self.get_logger().warning(f"Ignoring invalid sensor line: {line}")
                continue

            message = Vector3Stamped()
            message.header.stamp = self.get_clock().now().to_msg()
            message.vector.x, message.vector.y, message.vector.z = acceleration
            self._publisher.publish(message)

        if len(self._buffer) > 256:
            self.get_logger().warning("Discarding oversized sensor line")
            self._buffer.clear()

    def destroy_node(self) -> bool:
        self._serial.close()
        return super().destroy_node()


def main(args: list[str] | None = None) -> None:
    rclpy.init(args=args)
    node = None
    try:
        node = SensorSerialNode()
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        if node is not None:
            node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
