"""Send ROS movement states to the separate LED board."""

import rclpy
import serial
from rclpy.node import Node
from std_msgs.msg import Bool


class LedSerialNode(Node):
    def __init__(self) -> None:
        super().__init__("led_serial_node")
        self.declare_parameter("port", "/dev/ttyACM1")
        port = self.get_parameter("port").value
        if not isinstance(port, str) or not port:
            raise ValueError("led_port must be a nonempty serial device path")

        self._serial = serial.Serial(port, baudrate=115200, timeout=0)
        self.get_logger().info(f"Writing LED Board on {port}")
        self._last_moving: bool | None = None
        self._subscription = self.create_subscription(
            Bool, "/psoc/moving", self._on_moving, 10
        )

    def _on_moving(self, message: Bool) -> None:
        # A command is only necessary when the state changes.
        if message.data == self._last_moving:
            return
        command = b"LED,BLINK\n" if message.data else b"LED,ON\n"
        try:
            self._serial.write(command)
        except serial.SerialException as exc:
            raise RuntimeError("LED Board serial write failed") from exc
        self._last_moving = message.data
        self.get_logger().info(command.decode("ascii").strip())

    def destroy_node(self) -> bool:
        self._serial.close()
        return super().destroy_node()


def main(args: list[str] | None = None) -> None:
    rclpy.init(args=args)
    node = None
    try:
        node = LedSerialNode()
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
