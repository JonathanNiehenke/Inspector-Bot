"""
    My personal function wrappers to logically and informatively
interact with Windows.
"""
# Would like to move completely to built-in ctypes.
# Memory severs FindWindows is difficult from ctypes.

# Naming Styles -- Why? For variable and function distinction.
# Variables = mixedCamelCase, Global variable = ALL_CAPS;
# Function/Methods/Modules = lowercase_with_underscores.
# Class = CamelCase

from __future__ import print_function

import win32gui
# import pywintypes
from win32api import mouse_event, GetSystemMetrics

SCREEN_RESOLUTION = GetSystemMetrics(0), GetSystemMetrics(1)
ABSOLUTE_RATIO_X = 65535.0/SCREEN_RESOLUTION[0]
ABSOLUTE_RATIO_Y = 65535.0/SCREEN_RESOLUTION[1]


def locate_window(windowName):
    """Returns and reveals the window's position."""
    windowID = identify_window(windowName)
    win32gui.ShowWindow(windowID, 1)  # Restores if minimized.
    win32gui.SetForegroundWindow(windowID)
    return win32gui.GetWindowRect(windowID)


def identify_window(windowName):
    """Gets the window identifier by a window's title."""
    windowID = win32gui.FindWindow(None, windowName)
    if not windowID:
        print('Window with entire title was not found.')
        print('Now searching for the given title within a window title.')
        windowID = identify_window2(windowName)
    return windowID


def identify_window2(windowName):
    """Gets the window identifier by a piece of a window's title."""
    callerReturn = []

    def enum_caller(hwnd, wName):
        if windowName in win32gui.GetWindowText(hwnd):
            callerReturn.append(hwnd)
            return True

    win32gui.EnumWindows(enum_caller, wName)
    try:
        windowID = callerReturn.pop()
    except IndexError:
        raise ValueError(
            'Found no window title with {} in it.'.format(repr(windowName)))
    return windowID


def execute_mouse(*actionPairs):
    """Moves the cursor to X and Y or execute a Button Action."""
    Cursor = {
        'Left':  {'Press': 0x0002, 'Release': 0x0004,  'Click': 0x0006},
        'Right': {'Press': 0x0008, 'Release': 0x00010, 'Click': 0x00018},
        }
    for xButton, yAction in actionPairs:
        try:
            mouse_event(Cursor[xButton][yAction], 0, 0)
        except KeyError:
            mouse_event(0x8001, *convert_to_absolute(xButton, yAction))


def convert_to_absolute(screenX, screenY):
    """Converts screenX/Y into "absolute" values."""
    return int(screenX*ABSOLUTE_RATIO_X), int(screenY*ABSOLUTE_RATIO_Y)


def shift_window(windowID, newLocation, newSize):
    """Moves and/or resizes the window."""
    win32gui.ShowWindow(windowID, 1)  # Restores if minimized.
    try:
        Width, Height = newSize
    except TypeError:
        Left, Top, Right, Bot = locate_window(windowID)
        Width, Height = Right - Left, Bot - Top
    try:
        Left, Top = newLocation
    except TypeError:
        Left, Top, _, _ = locate_window(windowID)
    win32gui.MoveWindow(windowID, Left, Top, Width, Height, True)
