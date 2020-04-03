#!/usr/bin/env python3
"""This script lets you easily give commands to an orange pi by pressing the
board button. The commands you can give are easily configured in the 
commands.txt file. The first line is the first command, the second line is the 
second command and so on.
You select the command by pressing the button for a certain amount of seconds.
The red led serves as an indicator of the time the button has been pressed and
thus, the command selected so far.
If you press the button for less than one second, no command is executed. The 
led turns on while you press it to let you know the program is running.
If you press the button for more than a second the led will flicker each second
to let you know which command are you giving:
    one flicker, command one
    two flickers, command two
    ... and so on
After a command is given the red led will flash n times to confirm it's 
executing command n.
"""
import time, os, sys, subprocess

import opibtn, opiled

if not os.geteuid() == 0:
    sys.exit("Only root can run this script")

_start = None


def _down():
    global _start
    _start = time.time()
    opiled.blink("red", [0.95, 0.05])


def _up():
    if not _start:
        return  # No previous Down event
    pressed = time.time() - _start
    opiled.set_state("red", 0)
    command = int(pressed // 1)
    print(f"pressed for: {pressed:.2f}s command: {command}")
    time.sleep(1)
    if command:
        # Confirm the command to execute
        opiled.blink("red", [0.5, 0.5], command)
        time.sleep(command)
        with open("commands.txt", "r") as coms:
            for num, line in enumerate(coms):
                if num == command - 1:
                    print(f'executing command {command}: "{line.strip()}"')
                    subprocess.run([line], shell=True)

if __name__ == "__main__":
    try:
        opibtn.read_button(_down, _up)
    except KeyboardInterrupt:
        pass
