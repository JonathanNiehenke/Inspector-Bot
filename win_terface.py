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
import win32ui
# import pywintypes
from win32api import mouse_event, GetSystemMetrics

ABSOLUTE_RATIO_X = 65535.0/GetSystemMetrics(0)
ABSOLUTE_RATIO_Y = 65535.0/GetSystemMetrics(1)

class WindowElement(object):
    
    def __init__(self, windowName):
        self.handle = identify_window(windowName)
        self.bring_to_top()
        windowDcHandle = win32gui.GetWindowDC(self.handle)
        self.device_context = win32ui.CreateDCFromHandle(windowDcHandle)
        self.position = win32gui.GetWindowRect(self.handle)
        self.width, self.height = dimension_window(*self.position)

    def bring_to_top(self):
        win32gui.ShowWindow(self.handle, 1)  # Restores if minimized.
        win32gui.SetForegroundWindow(self.handle)

    def identify_pixel(self, X, Y, Capture=None):
        """Returns the RGB tuple of Capture or window at X and Y."""
        try:
            intRGB = Capture.GetPixel(X, Y)
        except AttributeError:
            intRGB = self.device_context.GetPixel(X, Y)
        return tuple((intRGB >> Val) & 255 for Val in (0, 8, 16))

    def capture(self, fileName=None):
        """Returns the window image and saves as fileName if given."""
        compatibleDC = self.device_context.CreateCompatibleDC()
        dataBitMap = win32ui.CreateBitmap()
        dataBitMap.CreateCompatibleBitmap(
            self.device_context, self.width, self.height)
        compatibleDC.SelectObject(dataBitMap)
        compatibleDC.BitBlt(
            (0,0),
            (self.width, self.height),
            self.device_context,
            (0,0),
            13369376,  # win32con.SRCCOPY
            )
        try:
            dataBitMap.SaveBitmapFile(compatibleDC, fileName)
        except TypeError:
            pass
        return compatibleDC

    def move_to(self, Left, Top):
        """Moves the window to absolute Left and Top position."""
        win32gui.MoveWindow(
            self.handle, Left, Top, self.width, self.height, True)

    def resize(self, Width, Height):
        """Resizes window in-place to specified Width and Height."""
        Top, Left, _, _ = self.position
        win32gui.MoveWindow(self.handle, Left, Top, Width, Height, True)


def identify_window(windowName):
    """Gets the window identifier by a window's title."""
    windowID = win32gui.FindWindow(None, windowName)
    if not windowID:
        windowID = identify_window2(windowName)
    return windowID

def identify_window2(windowName):
    """Gets the window identifier by a piece of a window's title."""
    callerReturn = []

    def enum_caller(windowID, wName):
        if wName in win32gui.GetWindowText(windowID):
            callerReturn.append(windowID)
            return True

    win32gui.EnumWindows(enum_caller, windowName)
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


# def capture_window(windowID=None):
    # """Takes a screenshot of the screen or application."""
    # if windowID is None:
        # windowID = win32gui.GetDesktopWindow()
    # Width, Height = dimension_window(*win32gui.GetWindowRect(windowID))
    # windowDC = win32gui.GetWindowDC(windowID)
    # dcObj = win32ui.CreateDCFromHandle(windowDC)
    # compatibleDC = dcObj.CreateCompatibleDC()
    # dataBitMap = win32ui.CreateBitmap()
    # dataBitMap.CreateCompatibleBitmap(dcObj, Width, Height)
    # compatibleDC.SelectObject(dataBitMap)
    # compatibleDC.BitBlt((0,0),(Width, Height) , dcObj, (0,0), win32con.SRCCOPY)
    # return dataBitMap
    # dataBitMap.SaveBitmapFile(compatibleDC, r'E:\Pictures\test.bmp')

    # # Free Resources
    # dcObj.DeleteDC()
    # compatibleDC.DeleteDC()
    # win32gui.ReleaseDC(windowID, windowDC)
    # win32gui.DeleteObject(dataBitMap.GetHandle())





def identify_window(windowName):
    """Gets the window identifier by a window's title."""
    windowID = win32gui.FindWindow(None, windowName)
    if not windowID:
        windowID = identify_window2(windowName)
    return windowID

def dimension_window(Left, Top, Right, Bottom):
    return Right - Left, Bottom - Top
