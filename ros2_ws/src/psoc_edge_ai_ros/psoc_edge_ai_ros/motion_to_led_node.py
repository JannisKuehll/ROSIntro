"""Turn acceleration messages into a simple moving/not-moving state."""

from __future__ import annotations

import math

import rclpy
from geometry_msgs.msg import Vector3Stamped
from rclpy.node import Node
from std_msgs.msg import Bool


GRAVITY_MPS2 = 9.81
MOVEMENT_THRESHOLD_MPS2 = 0.5


class MotionToLed(Node):
    """Publish True while the acceleration indicates movement."""

    def __init__(self) -> None:
        super().__init__("motion_to_led")
        self._previous_vector: tuple[float, float, float] | None = None
        self._last_moving: bool | None = None

        self._moving_publisher = self.create_publisher(
            Bool, "/psoc/moving", 10
        )
        self._acceleration_subscription = self.create_subscription(
            Vector3Stamped,
            "/psoc/acceleration",
            self._on_acceleration,
            10,
        )

    def _on_acceleration(self, message: Vector3Stamped) -> None:
        """Publish the current movement state for every sensor sample."""
        vector = (
            message.vector.x,
            message.vector.y,
            message.vector.z,
        )
        if not all(math.isfinite(value) for value in vector):
            self.get_logger().warning("Ignoring invalid acceleration")
            return

        # Detect both a change in total acceleration and rotation at 1 g.
        magnitude = math.sqrt(sum(value * value for value in vector))
        gravity_difference = abs(magnitude - GRAVITY_MPS2)
        vector_change = 0.0
        if self._previous_vector is not None:
            vector_change = math.sqrt(
                sum(
                    (current - previous) ** 2
                    for current, previous in zip(
                        vector, self._previous_vector
                    )
                )
            )
        self._previous_vector = vector

        moving = max(gravity_difference, vector_change) >= (
            MOVEMENT_THRESHOLD_MPS2
        )
        output = Bool()
        output.data = moving
        # Repeating the state lets a later-started LED node catch up.
        self._moving_publisher.publish(output)

        if moving != self._last_moving:
            state = "moving" if moving else "still"
            self.get_logger().info(
                f"Acceleration {magnitude:.2f} m/s^2 -> {state}"
            )
            self._last_moving = moving


def main(args: list[str] | None = None) -> int:
    """Start the movement classifier."""
    rclpy.init(args=args)
    node: MotionToLed | None = None

    try:
        node = MotionToLed()
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        if node is not None:
            node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
