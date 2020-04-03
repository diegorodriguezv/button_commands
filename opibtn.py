#!/usr/bin/env python3
"""This module lets you execute a function every time the button on an orange
pi is pressed or released.
"""
import asyncio

from evdev import InputDevice, categorize, ecodes


async def _key_reader(dev, down, up):
    async for ev in dev.async_read_loop():
        if ev.type == ecodes.EV_KEY:
            if ev.value == 1:  # Down
                down()
            if ev.value == 0:  # Up
                up()


def read_button(down, up):
    """Executes a function every time the board button is pressed down or 
    released.

    :param down: a function to call every time the button is pressed
    :param up: a function to call every time the button is released
    """
    dev = InputDevice("/dev/input/event0")
    loop = asyncio.get_event_loop()
    loop.run_until_complete(_key_reader(dev, down, up))


if __name__ == "__main__":
    try:
        read_button(lambda: print("down"), lambda: print("up"))
    except KeyboardInterrupt:
        pass
