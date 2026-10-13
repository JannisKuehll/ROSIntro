"""Control the onboard LED from ROS 2."""

import sys
import time

from machine import Pin

try:
    import uselect
except ImportError:
    import select as uselect


# The user LED is on P10_7 and uses active-high logic.
LED_PIN = "P10_7"
LED_ON_LEVEL = 1
LED_OFF_LEVEL = 0

# Toggle every 250 ms. One complete on/off cycle therefore takes 500 ms.
BLINK_HALF_PERIOD_MS = 250


def handle_command(command, led, mode, led_is_on, last_toggle_ms):
    """Apply one complete LED command and return the updated state."""
    if command == "LED,ON":
        led.value(LED_ON_LEVEL)
        print("LED_ACK,ON")
        return "on", True, last_toggle_ms

    if command == "LED,BLINK":
        # Always restart blinking with the LED on.
        led.value(LED_ON_LEVEL)
        print("LED_ACK,BLINK")
        return "blink", True, time.ticks_ms()

    print("ERROR,expected LED,ON or LED,BLINK")
    return mode, led_is_on, last_toggle_ms


def main():
    """Start with the LED on and wait for commands from ROS 2."""
    led = Pin(LED_PIN, Pin.OUT)
    led.value(LED_ON_LEVEL)

    mode = "on"
    led_is_on = True
    last_toggle_ms = time.ticks_ms()
    input_buffer = ""

    poller = uselect.poll()
    poller.register(sys.stdin, uselect.POLLIN)
    print("READY,LED")

    while True:
        # Poll without blocking so the LED can keep blinking on schedule.
        while poller.poll(0):
            character = sys.stdin.read(1)
            if not character:
                break

            if character in ("\r", "\n"):
                if input_buffer:
                    (
                        mode,
                        led_is_on,
                        last_toggle_ms,
                    ) = handle_command(
                        input_buffer.strip(),
                        led,
                        mode,
                        led_is_on,
                        last_toggle_ms,
                    )
                input_buffer = ""
            else:
                input_buffer += character

        now_ms = time.ticks_ms()
        if (
            mode == "blink"
            and time.ticks_diff(now_ms, last_toggle_ms)
            >= BLINK_HALF_PERIOD_MS
        ):
            led_is_on = not led_is_on
            led.value(LED_ON_LEVEL if led_is_on else LED_OFF_LEVEL)
            last_toggle_ms = now_ms

        time.sleep_ms(5)


if __name__ == "__main__":
    main()
