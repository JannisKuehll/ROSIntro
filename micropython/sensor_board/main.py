"""Read the onboard BMI270 and stream acceleration data to ROS 2."""

import time

from machine import I2C, Pin

try:
    from micropython_bmi270 import bmi270
except ImportError:
    raise ImportError(
        "Missing BMI270 driver. Install it with "
        "mpremote mip install github:jposada202020/MicroPython_BMI270"
    )


# The onboard BMI270 is connected to I2C bus 0 at address 0x68.
I2C_BUS = 0
BMI270_ADDRESS = 0x68

# ROS receives ten sensor samples per second from the Sensor Board.
SAMPLE_INTERVAL_MS = 100


def create_i2c():
    """Create the I2C bus used by the onboard BMI270."""
    return I2C(
        I2C_BUS,
        # These board aliases map to SDA P8_1 and SCL P8_0.
        scl=Pin.board.I2C_SCL_1V8,
        sda=Pin.board.I2C_SDA_1V8,
        freq=400000,
    )


def send_acceleration(sensor):
    """Read one sample and send the simple serial protocol line."""
    ax, ay, az = sensor.acceleration
    # The ROS serial node parses this comma-separated message.
    print("ACCEL,{:.3f},{:.3f},{:.3f}".format(ax, ay, az))


def main():
    """Initialize the BMI270 and continuously stream acceleration data."""
    i2c = create_i2c()
    if BMI270_ADDRESS not in i2c.scan():
        raise RuntimeError(
            "BMI270 was not found at I2C address 0x{:02X}".format(
                BMI270_ADDRESS
            )
        )

    sensor = bmi270.BMI270(i2c, address=BMI270_ADDRESS)
    print("READY,SENSOR")

    # The continuous sensor loop starts immediately after initialization.
    last_sample_ms = time.ticks_ms()
    while True:
        now_ms = time.ticks_ms()
        if (
            time.ticks_diff(now_ms, last_sample_ms)
            >= SAMPLE_INTERVAL_MS
        ):
            send_acceleration(sensor)
            last_sample_ms = now_ms

        time.sleep_ms(5)


if __name__ == "__main__":
    main()
