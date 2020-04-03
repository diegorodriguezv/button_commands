#!/usr/bin/env python3
""" This module provides helper functions to manage the two leds present in an 
orange pi.
"""
import queue, threading, time, random, os, sys

if not os.geteuid() == 0:
    sys.exit("Only root can run this script")

_RED_LED = open("/sys/class/leds/orangepi:red:status/brightness", "w")
_GREEN_LED = open("/sys/class/leds/orangepi:green:pwr/brightness", "w")

_led_queue = queue.Queue()


def _led_manager():
    while True:
        job = _led_queue.get()
        for (led, state) in job:
            if led == "red":
                led_file = _RED_LED
            elif led == "green":
                led_file = _GREEN_LED
            else:
                raise ValueError(f"led must be 'red' or 'green', not {led}")
            led_file.write(str(int(state)))
            led_file.flush()
        _led_queue.task_done()


t = threading.Thread(target=_led_manager)
t.daemon = True
t.start()
del t


class _Blinker:
    def __init__(self, led):
        self.led = led
        self.is_running = False
        self.start_time = 0

    def start(self, pattern, ntimes=-1, duration=-1):
        if duration > 0:
            t = threading.Timer(duration, self.stop)
            t.daemon = True
            t.start()
            del t
        self.is_running = True
        t = threading.Thread(target=self._blinker, args=(pattern, ntimes))
        t.daemon = True
        t.start()
        del t

    def stop(self):
        self.is_running = False

    def _blinker(self, pattern, ntimes):
        cycles = 0
        total = sum(pattern)
        self.start_time = time.time()
        while True:
            state = True
            so_far = 0
            for state_duration in pattern:
                if not self.is_running:
                    return
                _led_queue.put([(self.led, state)])
                so_far += state_duration
                elapsed = time.time() - self.start_time
                remaining = so_far - elapsed % total
                state = not state
                time.sleep(remaining)
            cycles += 1
            if cycles == ntimes:
                break


_red_blinker = _Blinker("red")
_green_blinker = _Blinker("green")


def blink(led, pattern, ntimes=-1, duration=-1):
    """Blink one of the board LEDs in a given pattern.
    
    :param led: The led to blink, "red" or "green" 
    :param pattern: An iterable with the duration of each state in seconds 
    starting with on
    :param ntimes: Repeat the pattern this number of times and then stop, -1 to
    blink indefinitely
    :param duration: Stop blinking after this many seconds, -1 to blink 
    indefinitely

    :Example:
      
            blink("red", [.5, .5, 1, 1]) will turn on for half a second, then 
            off for half a second, 
            then on one second and off one second

    .. note:: The process will start immediately and any previous blinking will
    be stopped
    .. note:: The led will be left on the state it is at the moment of stopping
    .. note:: if both duration and ntimes are specified, the first one to occur
    will stop the blinking
    """
    global _red_blinker, _green_blinker
    if led == "red":
        _red_blinker.stop()
        _red_blinker = _Blinker(led)
        _red_blinker.start(pattern, ntimes, duration)
    else:
        _green_blinker.stop()
        _green_blinker = _Blinker(led)
        _green_blinker.start(pattern, ntimes, duration)


def set_state(led, state):
    """Set the state of one of the board LEDs.
    
    :param led: The led to blink, "red" or "green" 
    :param state: 1 for on, 0 for off

    .. note:: Setting the state of a led will stop it from blinking
    """
    if led == "red":
        bl = _red_blinker
    else:
        bl = _green_blinker
    bl.stop()
    _led_queue.put([(led, state)])


def _test():
    for i in (
        [0.6]
        + [0.5] * 2
        + [0.4] * 2
        + [0.3] * 3
        + [0.2] * 5
        + [0.1] * 10
        + [0.05] * 20
        + [0.03] * 30
    ):
        set_state("red", 0)
        set_state("green", 1)
        time.sleep(i)
        set_state("red", "1")
        set_state("green", "0")
        time.sleep(i)
    set_state("red", False)
    set_state("green", True)
    _led_queue.join()


def _test2():
    br = _Blinker("red")
    bg = _Blinker("green")
    br.start([0.1, 0.9, 0.2, 0.8], 3)
    bg.start([0.2, 0.8, 0.1, 0.9])


if __name__ == "__main__":
    _test()
    input()
    _test2()
    input()
    set_state("red", False)
    set_state("green", True)
    _led_queue.join()
