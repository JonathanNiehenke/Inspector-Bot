'''
Bejeweled specific tools to better interact with it.
'''

# Naming Styles -- Why? For variable and function distinction.
# Variables = mixedCamelCase, Global variable = ALL_CAPS;
# Function/Methods/Modules = lowercase_with_underscores.
# Class = CamelCase

from __future__ import print_function
import sys
from time import time
from PIL import Image, ImageGrab, ImageFont, ImageDraw
import numpy

sys.path.append(r'..\\')
import win_terface

ROW_INDEX_LST = [X*82 + 38 for X in xrange(8)]
COLUMN_INDEX_LST = [Y*82 + 43 for Y in xrange(8)]
COLOR_CIPHER = {
        (0,      0,   0): ' ',   # Hyper
        (0,      0, 127): ' ',   # Blue
        (0,      0, 255): ' ',
        (0,   127,   0): 'G',   # Green   Secondary
        (0,   127, 127): ' ',   # Green   Star        Blue, Background
        (0,   127, 255): 'B',   # Blue    Primary
        (0,   255,   0): 'G',   # Green   Primary
        (0,   255, 127): ' ',   # Green
        (0,   255, 255): ' ',   # Blue
        (127,   0,   0): ' ',   # Red
        (127,   0, 127): ' ',   # Purple  Secondary
        (127,   0, 255): ' ',
        (127, 127,   0): 'G',   # Green   Flame       Yellow
        (127, 127, 127): ' ',   # Silver  Secondary
        (127, 127, 255): 'B',   # Blue    Flame
        (127, 255,   0): 'G',   # Green   Flame
        (127, 255, 127): 'G',   # Green   Flame
        (127, 255, 255): 'B',   # Blue    Flame
        (255,   0,   0): 'R',   # Red     Primary
        (255,   0, 127): 'R',   # Red     Flame       Adjacent specials.
        (255,   0, 255): 'P',   # Purple  Primary
        (255, 127,   0): 'O',   # Orange  Primary
        (255, 127, 127): 'R',   # Red     Flame       SOrange, Messages.
        (255, 127, 255): 'P',   # Purple  Flame
        (255, 255,   0): 'Y',   # Yellow  Primary
        (255, 255, 127): 'O',   # Orange  Secondary   Menu/Post Game.
        (255, 255, 255): 'S',   # Silver  Primary
    }

COLOR_ARRAY = numpy.array([K for K in COLOR_CIPHER])
FONT = ImageFont.truetype("Consola.ttf", 75)


def init():
    '''
defines variables that may change between game sessions.'''
    global WINDOW_POS, GRID_POS, GRID_LEFT, GRID_TOP
    windowID = win_terface.identify_window("Bejeweled 3")
    firstDisplay = ((0, 0), (1024, 768))
    win_terface.shift_window(windowID, *firstDisplay)
    WIN_POS = win_terface.locate_window(windowID)
    windowLeft, windowTop = WIN_POS[:2]
    # relativeGrid = 334, 48, 990, 704 # Area=656 Res=1024x960
    GRID_POS = (
        windowLeft + 334, windowTop + 48, windowLeft + 990, windowTop + 704)
    GRID_LEFT, GRID_TOP = GRID_POS[:2]


def translate_board(filePathName=''):
    '''Simplifies gems into representative letters.'''
    boardImage = ImageGrab.grab(GRID_POS)
    boardArray = numpy.array(boardImage)
    pixelGrid = reduce_gems(boardArray)
    boardTranslation = numpy.apply_along_axis(rgb_cipher, -1, pixelGrid)

    if filePathName:
        translateBoard = write_translation_overlay(
            boardImage, boardTranslation)
        translateBoard.save(filePathName, 'PNG')
    return boardTranslation, boardArray


def reduce_gems(screenArray):
    '''Reduce each gem to a single RGB value.'''
    return screenArray[ROW_INDEX_LST,:][:,COLUMN_INDEX_LST]


def rgb_cipher(gemPixel):
    '''Decodes the RGB value to a representing letter.'''
    colorDeviations = numpy.absolute(COLOR_ARRAY - gemPixel).sum(1)
    colorRGB = tuple(COLOR_ARRAY[colorDeviations.argmin()])
    return COLOR_CIPHER[colorRGB]


def write_translation_overlay(boardImage, boardTranslation):
    '''Writes onto the boardImage the boardTranslation.'''
    for Idx, Row in enumerate(boardTranslation):
        Location, translationText = (0, Idx*82 + 10), ' '.join(Row)
        write_text_to_image(boardImage, Location, translationText, FONT)
    return boardImage


def save_read(boardTranslation, Extra):
    '''Saves a file of the board image with boardTranslation overlay.'''
    fileName = '.\\{:.0f}{}.png'.format(time(), Extra)
    boardImage = ImageGrab.grab(GRID_POS)
    boardTranslation = write_translation_overlay(boardImage, boardTranslation)
    boardTranslation.save(fileName, 'PNG')


def write_text_to_image(Image, Location, Text, Font):
    drawImg = ImageDraw.Draw(Image)
    drawImg.text(Location, Text, (0, 0, 0), Font)


def save_board(Extra=''):
    fileName = '.\\{:.0f}{}.png'.format(time(), Extra)
    ImageGrab.grab(GRID_POS).save(fileName, 'PNG')


def execute_mouse_drag(fromPoint, toPoint):
    '''Executes a left button press held fromPoint toPoint.'''
    win_terface.execute_mouse_action(*convert_grid_to_screen(*fromPoint))
    win_terface.execute_mouse_action('Left', 'Press')
    win_terface.execute_mouse_action(*convert_grid_to_screen(*toPoint))
    win_terface.execute_mouse_action('Left', 'Release')


def rest_mouse():
    '''Places the mouse off of the board.'''
    win_terface.execute_mouse_action(GRID_LEFT + 158, GRID_TOP + 676)


def convert_grid_to_screen(xGrid, yGrid):
    return GRID_LEFT + xGrid*82 + 41, GRID_TOP + yGrid*82 + 41
