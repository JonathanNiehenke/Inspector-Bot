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

from collections import namedtuple

import win32gui
import win32ui
# import pywintypes
from win32api import mouse_event, GetSystemMetrics

ABSOLUTE_RATIO_X = 65535.0/GetSystemMetrics(0)
ABSOLUTE_RATIO_Y = 65535.0/GetSystemMetrics(1)
Pixel = namedtuple('Pixel', ('Red', 'Green', 'Blue'))
Dimensions = namedtuple('Dimensions', ['width', 'height'])
VirtualKey = {
    8: 'Backspace', 9: 'Tab', 27: 'Esc', 32: 'Spacebar',
    33: 'Page Up', 34: 'Page Down', 35: 'End', 36: 'Home',
    37: 'LArrow', 38: 'UArrow', 39: 'RArrow', 40: 'DArrow',
    44: 'Print Screen', 45: 'Ins', 46: 'Del',
    48: 0, 49: 1, 50: 2, 51: 3, 52: 4, 53: 5, 54: 6, 55: 7, 56: 8, 57: 9,
    65: 'A', 66: 'B', 67: 'C', 68: 'D', 69: 'E', 70: 'F', 71: 'G',
    72: 'H', 73: 'I', 74: 'J', 75: 'K', 76: 'L', 77: 'M', 78: 'N',
    79: 'O', 80: 'P', 81: 'Q', 82: 'R', 83: 'S', 84: 'T', 85: 'U', 
    86: 'V', 87: 'W', 88: 'X', 89: 'Y', 90: 'Z',
    160: 'LShift', 161: 'RShift', 162: 'LControl', 163: 'RControl',
    }

class WindowElement(object):
 
    def __init__(self, windowName=None, bringTop=False):
        self.handle = identify_window(windowName)
        if bringTop:
            self.bring_to_top()
        windowDcHandle = win32gui.GetWindowDC(self.handle)
        self.device_context = win32ui.CreateDCFromHandle(windowDcHandle)
        self.position = win32gui.GetWindowRect(self.handle)
        self.width, self.height = dimension_window(*self.position)
        self.capture_image = CaptureImage(
            'DC', self.device_context, self.width, self.height)

    def bring_to_top(self):
        win32gui.ShowWindow(self.handle, 1)  # Restores if minimized.
        win32gui.SetForegroundWindow(self.handle)

    def update_capture(self, fileName=None):
        """Returns the window capture and saves as fileName if given."""
        self.capture_image.update_from_dc(self.device_context, self.width, self.height)
        try:
            self.capture_image.save(fileName)
        except TypeError:
            pass
        return self.capture_image

    def identify_current_pixel(self, X, Y):
        """Returns the window's pixel value at Index as a RGB tuple."""
        try:
            intRGB = self.device_context.GetPixel(X, Y)
        except win32ui.error:
            raise IndexError
        return convert_integer_rgb(intRGB)

    def identify_capture_pixel(self, X, Y):
        """Returns the capture pixel value at Index as a RGB tuple."""
        return self.capture_image[(X, Y)]

    def move_to(self, Left, Top):
        """Moves the window to absolute Left and Top position."""
        win32gui.MoveWindow(
            self.handle, Left, Top, self.width, self.height, True)

    def resize(self, Width, Height):
        """Resizes window in-place to specified Width and Height."""
        Top, Left, _, _ = self.position
        win32gui.MoveWindow(self.handle, Left, Top, Width, Height, True)

    def __repr__(self):
        windowName = win32gui.GetWindowText(self.handle)
        return '{}({})'.format(self.__class__.__name__, repr(windowName))


class CaptureImage(object):

    def __init__(self, Type, *args):
        self.bitmap = win32ui.CreateBitmap()
        {'Window': self.extract_window, 'DC': self.build_from_dc}[Type](*args)

    def extract_window(self, windowName):
        Handle = identify_window(windowName)
        Width, Height= dimension_window(*win32gui.GetWindowRect(Handle))
        dcHandle = win32gui.GetWindowDC(Handle)
        DC = win32ui.CreateDCFromHandle(dcHandle)
        self.build_from_dc(DC, Width, Height)

    def build_from_dc(self, DC, Width, Height):
        self.connect_dc(DC, Width, Height)
        self.update_from_dc(DC, Width, Height)
        self.dimensions = Width, Height

    def connect_dc(self, DC, Width, Height):
        self.context = DC.CreateCompatibleDC()
        self.bitmap.CreateCompatibleBitmap(DC, Width, Height)
        self.context.SelectObject(self.bitmap)

    def update_from_dc(self, DC, Width, Height):
        self.context.BitBlt((0,0), (Width, Height), DC, (0,0), 13369376)

    @property
    def raw_data(self):
        return self.bitmap.GetBitmapBits()

    def save(self, fileName):
        self.bitmap.SaveBitmapFile(self.context, fileName)
        
    def __getitem__(self, tupleIndex):
        """Returns the pixel value at tupleIndex as a RGB tuple."""
        try:
            intRGB = self.context.GetPixel(*tupleIndex)
        except win32ui.error:
            raise IndexError
        return convert_integer_rgb(intRGB)

    def __iter__(self):
        bgrxColors = [iter(self.bitmap.GetBitmapBits())] * 4
        rgbColors = (Pixel(R, G, B) for B, G, R, _ in zip(*bgrxColors))
        Rows = [rgbColors] * self.dimensions.width
        return zip(*Rows)

    def __repr__(self):
        return '{}'.format(self.__class__.__name__)


def identify_window(windowName=None):
    """Returns the window identifier by a window's title."""
    if windowName is None:
        windowID = win32gui.GetDesktopWindow()
    else:
        windowID = win32gui.FindWindow(None, windowName)
        if not windowID:
            windowID = distinguish_window(windowName)
    return windowID


def distinguish_window(windowName):
    """Returns the window identifier by a piece of a window's title."""
    callerReturn = 0
    def enum_caller(windowID, wName):
        nonlocal callerReturn
        if wName in win32gui.GetWindowText(windowID):
            callerReturn = windowID
            return True
    win32gui.EnumWindows(enum_caller, windowName)
    if not callerReturn:
        raise ValueError(
            'Found no window title with {} in it.'.format(repr(windowName)))
    return callerReturn


def dimension_window(Left, Top, Right, Bottom):
    return Right - Left, Bottom - Top


def convert_integer_rgb(intRGB):
    return Pixel(*((intRGB >> Val) & 255 for Val in (0, 8, 16)))


def execute_mouse(*actionPairs):
    """Moves the cursor to X and Y or execute a Button Action."""
    Cursor = {'Left':  {'Press': 2, 'Release': 4,  'Click': 6},
              'Right': {'Press': 8, 'Release': 16, 'Click': 24},}
    for xButton, yAction in actionPairs:
        try:
            buttonAction = Cursor[xButton][yAction]
        except KeyError:
            mouse_event(32769, *convert_to_absolute(xButton, yAction))
        else:
            mouse_event(buttonAction, 0, 0)


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



