"""
Bot that plays a game of Minesweeper by reading the screen, making
    decisions and moving the mouse.
"""
# Began 9/22/2015
# By Jonathan Niehenke

# Naming Styles -- Why? For variable and function distinction.
#   Variables = mixedCamelCase, Global variable = ALL_CAPS,
#   Function/Methods/Modules = lowercase_with_underscores,
#   Class = CamelCase

# Definition Order -- Why? Improve reading navigation.
#   In order of use (hierarchical top to bottom). Unless shared by a
#   continuous defined group of functions or defined elsewhere which
#   would note a def@ comment.

# Personal challenge: -- Why? For improvement.
#   Clean clear code > performance benefits > type saving.
#   Frequently, succinctly, and completely inform future code readers.
#   The code should explain itself while comments explain application.
#   Properly named functions and variables describe their purpose.
#   Descriptive verb function names express action and imply output.
#   Assertions disclose both your assumptions and variable conditions.
#   Handling errors is easier, cheaper and clearer than error dodging.
#   Make as simple as possible without losing functionality.
#   Simple implementation is easier to build, fix and modify.

import sys
from collections import OrderedDict
from random import choice
from time import sleep, time

from PIL import Image, ImageGrab

import win_terface

class MinesweeperInterface(OrderedDict):

    cipher = {
        (0, 0, 255): 1,
        (0, 128, 0): 2,
        (255, 0, 0): 3,
        (0, 0, 128): 4,
        (128, 0, 0): 5,
        (0, 128, 128): 6,
        (0, 0, 0): 7,
        (128, 128, 128): 8,
        (192, 192, 192, 0): 0,  # Empty
        (128, 128, 128, 0): 'C',  # Covered
        }

    def __init__(self):
        OrderedDict.__init__(self)
        self.position, self.tile_size = self.locate_minefield(), 16
        self.left, self.top, Right, Bot = self.position
        self.width = (Right - self.left)//self.tile_size
        self.height = (Bot - self.top)//self.tile_size
        self.reset_button = (self.width/2.25, -2.5)
        Keys = [(X, Y) for Y in range(self.height) for X in range(self.width)]
        self.unsolved = set(Keys)
        self.read_field(Keys)

    def locate_minefield(self):
        """Returns and reveals the location of the minefield."""
        gridOffset = (15, 101, -11, -11)
        windowPos = win_terface.locate_window('Minesweeper')
        gridPos = tuple(W + G for W, G in zip(windowPos, gridOffset))
        return gridPos

    def read_field(self, Keys=None):
        if Keys is None:
            Keys = self.unsolved.copy()
        boardImage = ImageGrab.grab(self.position)
        boardImage.save(
            r'E:\Pictures\Minesweeper/M{:.0f}.bmp'.format(time()), 'BMP')
        for X, Y in Keys.copy():
            self[(X, Y)] = self.identify_cell_value(X, Y, boardImage)

    def identify_cell_value(self, X, Y, fieldImage=None):
        if fieldImage is None:
            fieldImage = ImageGrab.grab(self.position)
        tileX, tileY = self.tile_size * X, self.tile_size * Y
        Color = fieldImage.getpixel((tileX + 7, tileY + 4))
        try:
            Value = self.cipher[Color]
        except KeyError:
            Color = fieldImage.getpixel((tileX + 14, tileY + 8))
            Value = self.cipher[Color + (0,)]
        return Value

    # def identify_cell_value(self, X, Y, fieldImage):
        # tileX, tileY = self.tile_size * X, self.tile_size * Y
        # macroColor = fieldImage.getpixel((tileX + 14, tileY + 8)) 
        # try:
            # Value = self.cipher[macroColor + (0,)]
        # except KeyError:
            # valueColor = fieldImage.getpixel((tileX + 7, tileY + 4))
            # Value = self.cipher[valueColor]
        # return Value

    def reset(self):
        self.preform_to_cell(self.reset_button, 'Open')

    def preform_to_cell(self, targetIndex, Action):
        actionDict = {'Open': ('Left', 'Click'), 'Flag': ('Right', 'Click')}
        win_terface.execute_mouse(self.convert_cell_to_screen(*targetIndex))
        win_terface.execute_mouse(actionDict[Action])

    def convert_cell_to_screen(self, X, Y):
        """Converts the cell index to the expected screen X and Y."""
        screenX = self.left + (self.tile_size * X) + 8  # target center.
        screenY = self.top + (self.tile_size * Y) + 8
        return screenX, screenY

    def collect_adjacent(self, X, Y):
        rangeX = [V for V in range(X - 1, X + 2) if -1 < V < self.width]
        rangeY = [V for V in range(Y - 1, Y + 2) if -1 < V < self.height]
        return [((X, Y), self[(X, Y)]) for Y in rangeY for X in rangeX]

    def __str__(self):
        args = [(str(V) for V in self.values())] * self.width
        return '\n'.join(' '.join(Row) for Row in zip(*args))


def main():
    Minefield = MinesweeperInterface()
    if 0 not in Minefield.values():
        attain_suitable_start(Minefield)
        Minefield.read_field()
    while Minefield.unsolved:
        apply_isolated_logic(Minefield)
        Minefield.read_field()
    print(Minefield)


def attain_suitable_start(Minefield):
    cellValue, Reset = 1, 0
    while cellValue:
        targetIndex = choice(list(Minefield.keys()))
        Minefield.preform_to_cell(targetIndex, 'Open')
        cellValue = Minefield.identify_cell_value(*targetIndex)
        if cellValue == 7:
            Reset += 1
            Minefield.reset()
    else:
        print('Reset {} time{}.'.format(Reset, '' if Reset == 1 else 's'))


def apply_isolated_logic(Minefield):
    for targetIndex in Minefield.unsolved.copy():
        try:
            lackingMines, Covered, coveredLst = comprehend_adjacent(
                Minefield, targetIndex)
        except TypeError:
            continue

        if not Covered:
            Minefield.unsolved.discard(targetIndex)
        elif not lackingMines:
            for Index in coveredLst:
                Minefield.preform_to_cell(Index, 'Open')
        elif lackingMines == Covered:
            for Index in coveredLst:
                Minefield.preform_to_cell(Index, 'Flag')
                Minefield[Index] = 'F'
                Minefield.unsolved.discard(Index)


def comprehend_adjacent(Minefield, targetIndex):
    Mines = Minefield[targetIndex]
    Adjacent = Minefield.collect_adjacent(*targetIndex)
    flaggedMines = len([Val for _,  Val in Adjacent if Val == 'F'])
    lackingMines = Mines - flaggedMines
    coveredLst = [Index for Index, Val in Adjacent if Val == 'C']
    Covered = len(coveredLst)
    return lackingMines, Covered, coveredLst


main()
