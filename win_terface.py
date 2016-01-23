"""
    My personal wrappers to quickly, logically and informatively manage
the windows, screen captures and mouse actions of Microsoft Windows.
"""
# Began: When I decided autopy and PIL.ImageGrab were not acceptable.
# By Jonathan Niehenke

# Would like to handle garbage collection of device_context, context
#   and bitmap myself, because it is missed by the garbage collector;
#   but I don't have a clue.

# Would like to move completely to built-in ctypes rather than depend
#   on third party pywin32. Also ctypes supports SendInput.
# If memory serves FindWindows is difficult from ctypes because python
#   object need to be converted to acceptable ctype objects.

from collections import namedtuple
from functools import partial
from time import sleep
import ctypes

from win32api import mouse_event, GetSystemMetrics
import win32gui
import win32ui


WIN32 = ctypes.windll.kernel32

PIXEL = namedtuple('Pixel', ('red', 'green', 'blue'))
DIMENSIONS = namedtuple('Dimensions', ['width', 'height'])

ABSOLUTE_RATIO_X = 65535.0/GetSystemMetrics(0)
ABSOLUTE_RATIO_Y = 65535.0/GetSystemMetrics(1)

CONSOLE_COLOR = {
    'Black': 0, 'Blue': 1, 'Green': 2, 'Aqua': 3, 'Red': 4, 'Purple': 5,
    'Yellow': 6, 'White': 7, 'Gray': 8, 'Light blue': 9, 'Light green': 10,
    'Light aqua': 11, 'Light red': 12, 'Light purple': 13,
    'Light yellow': 14, 'Bright white': 15,
    }

PRINT_COLORS = [
    {'fgColor': 'Bright white', 'bgColor': 'Light blue'},
    {'fgColor': 'Bright white', 'bgColor': 'Red'},
    {'fgColor': 'Light yellow', 'bgColor': 'Purple'},
    {'fgColor': 'Light yellow', 'bgColor': 'Aqua'},
    {'fgColor': 'Black', 'bgColor': 'Aqua'},
    {'fgColor': 'Light green', 'bgColor': 'Black'},
    ]



VIRTUAL_KEY = {
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
    """
    Returns an object to manage and screen capture a window.
    """
 
    def __init__(self, windowClass=None, windowName=None, bringTop=False):
        self.handle = identify_window(windowClass, windowName)
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

    def screen_capture(self):
        """Refresh and returns the window capture."""
        self.capture_image.update_from_dc(
            self.device_context, self.width, self.height)
        return self.capture_image

    def move_to(self, Left, Top):
        """Moves the window to absolute Left and Top position."""
        win32gui.MoveWindow(
            self.handle, Left, Top, self.width, self.height, True)

    def resize(self, Width, Height):
        """Resizes window in-place to specified Width and Height."""
        Top, Left, _, _ = self.position
        win32gui.MoveWindow(self.handle, Left, Top, Width, Height, True)

    def __getitem__(self, indexPair):
        """Returns the RGB tuple of the window's pixel at indexPair."""
        try:
            intRGB = self.device_context.GetPixel(*indexPair)
        except win32ui.error:
            raise IndexError
        return convert_integer_rgb(intRGB)

    def __repr__(self):
        windowName = win32gui.GetWindowText(self.handle)
        return '{}({})'.format(self.__class__.__name__, repr(windowName))


class CaptureImage(object):
    """
    Returns object to retain, manage and preform screen captures.
    """

    def __init__(self, Type, *args):
        self.bitmap = win32ui.CreateBitmap()
        {'Window': self.extract_window, 'DC': self.build_from_dc}[Type](*args)

    def extract_window(self, windowName):
        """Initiate from a windowName."""
        Handle = identify_window(windowName)
        Width, Height= dimension_window(*win32gui.GetWindowRect(Handle))
        dcHandle = win32gui.GetWindowDC(Handle)
        DC = win32ui.CreateDCFromHandle(dcHandle)
        self.build_from_dc(DC, Width, Height)

    def build_from_dc(self, DC, Width, Height):
        """Initiate from a device context of a window."""
        self.dimensions = DIMENSIONS(Width, Height)
        self.connect_dc(DC, Width, Height)
        self.update_from_dc(DC, Width, Height)

    def connect_dc(self, DC, Width, Height):
        """Creates and joins a context to a bitmap."""
        self.context = DC.CreateCompatibleDC()
        self.bitmap.CreateCompatibleBitmap(DC, Width, Height)
        self.context.SelectObject(self.bitmap)

    def update_from_dc(self, DC, Width, Height):
        """Copy device context to bitmap context."""
        self.context.BitBlt((0,0), (Width, Height), DC, (0,0), 13369376)

    @property
    def raw_data(self):
        """Return tuple of chained cycling of BGRX values."""
        return self.bitmap.GetBitmapBits()

    def save(self, filePathname):
        try:
            self.bitmap.SaveBitmapFile(self.context, filePathname)
        except win32ui.error:
            errorMsg = 'No such file or directory: {}'.format(filePathname)
            raise FileNotFoundError(errorMsg)
        
    def __getitem__(self, indexPair):
        """Returns the RGB of the bitmap's pixel at indexPair."""
        try:
            intRGB = self.context.GetPixel(*indexPair)
        except win32ui.error:
            raise IndexError
        return convert_integer_rgb(intRGB)

    def __iter__(self):
        bgrxColors = [iter(self.bitmap.GetBitmapBits())] * 4
        rgbColors = (PIXEL(R, G, B) for B, G, R, _ in zip(*bgrxColors))
        Rows = [rgbColors] * self.dimensions.width
        return zip(*Rows)

    def __repr__(self):
        return '{}'.format(self.__class__.__name__)


def identify_window(windowClass=None, windowName=None):
    """Returns the window identifier by a window's title."""
    if windowName is None:
        windowID = win32gui.GetDesktopWindow()
    else:
        windowID = win32gui.FindWindow(windowClass, windowName)
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
    """Return width and height from window rect."""
    return Right - Left, Bottom - Top


def convert_integer_rgb(intRGB):
    """Return RGB tuple from integer RGB."""
    # return PIXEL(*((intRGB >> Val) & 255 for Val in (0, 8, 16)))
    return tuple((intRGB >> Val) & 255 for Val in (0, 8, 16))


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


def color_printer(consoleHandle, *printArgs, **kwArgs):
    fgId = CONSOLE_COLOR.get(kwArgs.pop('fgColor'), 7)
    bgId = CONSOLE_COLOR.get(kwArgs.pop('bgColor'), 0)
    WIN32.SetConsoleTextAttribute(consoleHandle, fgId + bgId * 16)
    print(*printArgs, **kwArgs, flush=True)


print_color = partial(color_printer, WIN32.GetStdHandle(-11))


def print_colorized_board(Board, *Args, **kwArgs):
    for Row in assemble_colorized_board(Board, *Args, **kwArgs):
        for boardValue, Color, End in Row:
            print_color(boardValue, **Color, end=End)


def assemble_colorized_board(Board, *Args, **kwArgs):
    Colors = kwArgs.pop('Colors', PRINT_COLORS.copy())
    assert len(Args) + 2 <= len(Colors)
    otherColors = Colors.pop(), Colors.pop()
    argumentColors = list(zip(Args, Colors))
    coloredBoard = []
    for Y,  Row in enumerate(Board):
        coloredBoard.append(colorize_row(Row, argumentColors, otherColors, Y))
    return coloredBoard


def colorize_row(Row, argumentColors, otherColors, Y):
    originalColor, defaultColor = otherColors
    for boardIndex, boardValue in Row:
        for argValue, Color in argumentColors:
            if boardIndex in argValue:
                yield boardValue, Color, ' '
                break
        else:
            yield boardValue, defaultColor, ' '
    yield Y, originalColor, '\n'


# Future Reference: Resource Handling
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

def print_window_info(Name, bringTop=False):
    print('WindowInfo')
    Msg = 'Class: {}, Title: {}'
    def enum_caller(windowID, Name):
        Title = win32gui.GetWindowText(windowID)
        if bringTop and Name in Title:
            print(Msg.format(win32gui.GetClassName(windowID), Title))
            win32gui.ShowWindow(windowID, 1)  # Restores if minimized.
            win32gui.SetForegroundWindow(windowID)
            sleep(2)
        elif Name in Title:
            print(Msg.format(win32gui.GetClassName(windowID), Title))
    win32gui.EnumWindows(enum_caller, Name)
