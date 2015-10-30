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

from collections import OrderedDict
from random import choice
from time import sleep, time

from PIL import Image, ImageGrab

import win_terface

class MinesweeperInterface(OrderedDict):

    cipher = {
        (192, 192, 192): 0,
        (0, 0, 255): 1,
        (0, 128, 0): 2,
        (255, 0, 0): 3,
        (0, 0, 128): 4,
        (128, 0, 0): 5,
        (0, 128, 128): 6,
        (0, 0, 0): 7,
        (128, 128, 128): 8,
        # (192, 192, 192, 0): 0,  # Empty
        (0, 0, 0, 0): 'M', # Mine
        (128, 128, 128, 0): 'C',  # Covered
        }

    def __init__(self):
        OrderedDict.__init__(self)
        self.position, self.tile_size = self.locate_minefield(), 16
        self.left, self.top, Right, Bot = self.position
        self.width = (Right - self.left)//self.tile_size
        self.height = (Bot - self.top)//self.tile_size
        self.reset_button = (self.width/2.25, -2.5)
        self.reset()
        exit()
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
        # boardImage.save(
            # r'E:\Pictures\Minesweeper/M{:.0f}.bmp'.format(time()), 'BMP')
        for X, Y in Keys.copy():
            self[(X, Y)] = self.identify_cell_value(X, Y, boardImage)

    def identify_cell_value(self, X, Y, fieldImage=None):
        if fieldImage is None:
            fieldImage = ImageGrab.grab(self.position)
        tileX, tileY = self.tile_size * X, self.tile_size * Y
        macroColor = fieldImage.getpixel((tileX + 14, tileY + 8)) 
        try:
            Value = self.cipher[macroColor + (0,)]
        except KeyError:
            valueColor = fieldImage.getpixel((tileX + 7, tileY + 4))
            Value = self.cipher[valueColor]
        return Value

    def reset(self):
        self.open_cells(self.reset_button)

    def open_cells(self, *indexCollection):
        for Index in indexCollection:
            X, Y = self.convert_cell_to_screen(*Index)
            print(X, Y)
            win_terface.execute_mouse(X, Y)
            win_terface.execute_mouse(('Left', 'Click'))

    def flag_cells(self, *indexCollection):
        for Index in indexCollection:
            win_terface.execute_mouse(self.convert_cell_to_screen(*Index))
            win_terface.execute_mouse(('Right', 'Click'))
            self[Index] = 'F'
            self.unsolved.discard(Index)


    def convert_cell_to_screen(self, X, Y):
        """Converts the cell index to the expected screen X and Y."""
        screenX = self.left + (self.tile_size * X) + 8  # target center.
        screenY = self.top + (self.tile_size * Y) + 8
        return screenX, screenY

    def collect_adjacent(self, Index):
        X, Y = Index
        rangeX = [V for V in range(X - 1, X + 2) if -1 < V < self.width]
        rangeY = [V for V in range(Y - 1, Y + 2) if -1 < V < self.height]
        return [((X, Y), self[(X, Y)]) for Y in rangeY for X in rangeX]

    def identify_discovered_cell(self):
        targetIndex = choice(list(self.unsolved))
        self.open_cells(targetIndex)
        return self.identify_cell_value(*targetIndex)

    def __str__(self):
        args = [(str(V) for V in self.values())] * self.width
        return '\n'.join(' '.join(Row) for Row in zip(*args))


def main():
    Start = time()
    Minefield = MinesweeperInterface()
    if 0 not in Minefield.values():
        Start = attain_suitable_start(Minefield)
        Minefield.read_field()
    while Minefield.unsolved:
        Changed = apply_logic(Minefield)
        if not Changed and Minefield.identify_discovered_cell() == 'M':
            print("Forced to explore and hit a mine. Unlucky I guess.")
            print(Minefield)
            for Index in sorted(Minefield.unsolved):
                print(Index, Minefield[Index])
            exit()
        else:
            Minefield.read_field()
    print('It took {:.2f}seconds to solve.'.format(time()-Start))


def attain_suitable_start(Minefield):
    cellValue, Reset, Start = 1, 0, time()
    while cellValue:
        cellValue = Minefield.identify_discovered_cell()
        if cellValue == 'M':
            Reset += 1
            Minefield.reset()
            Start = time()
    print('Reset {} time{}.'.format(Reset, '' if Reset == 1 else 's'))
    return Start


def apply_logic(Minefield):
    Previous = Minefield.unsolved.copy()
    apply_isolated_logic(Minefield)
    Changed = Previous != Minefield.unsolved
    if not Changed:
        apply_overlapping_logic(Minefield)
        Minefield.read_field()
        Changed = Previous != Minefield.unsolved
    return Changed

def apply_isolated_logic(Minefield):
    Unsolved = Minefield.unsolved.copy()
    for targetSynopsis in comprehend_indexes(Unsolved, Minefield):
        targetIndex, lackingMines, coveredLst = targetSynopsis
        Covered = len(coveredLst)

        if not Covered:
            Minefield.unsolved.discard(targetIndex)
        elif not lackingMines:
            Minefield.open_cells(*coveredLst)
        elif lackingMines == Covered:
            Minefield.flag_cells(*coveredLst)

def comprehend_indexes(indexCollection, Minefield):
    for targetIndex in indexCollection:
        requiredMines = Minefield[targetIndex]
        Adjacent = Minefield.collect_adjacent(targetIndex)
        flaggedMines = len([Val for _,  Val in Adjacent if Val == 'F'])
        try:
            lackingMines = requiredMines - flaggedMines
        except TypeError:
            pass
        else:
            coveredLst = [Index for Index, Val in Adjacent if Val == 'C']
            yield targetIndex, lackingMines, coveredLst


def apply_overlapping_logic(Minefield):
    """Deduce the non-overlapping cells of two targetCells."""
    # Logic explained https://www.youtube.com/watch?v=R6C_TZHDXCw#t=224
    for overlapSynopsis in comprehend_overlaps(Minefield):
        primaryOnlyMines, primaryOnlyCoveredLst, secondaryTotallyShared = (
            overlapSynopsis)
        if not primaryOnlyMines and secondaryTotallyShared:
            Minefield.open_cells(*primaryOnlyCoveredLst)
        elif primaryOnlyMines == len(primaryOnlyCoveredLst):
            Minefield.flag_cells(*primaryOnlyCoveredLst)


def comprehend_overlaps(Minefield):
    Unsolved = Minefield.unsolved.copy()
    for primarySynopsis in comprehend_indexes(Unsolved, Minefield):
        primaryIndex, primaryMines, primaryCoveredLst = primarySynopsis
        indexAdjacent, _ = zip(*Minefield.collect_adjacent(primaryIndex))

        for secondarySynopsis in comprehend_indexes(indexAdjacent, Minefield):
            _, secondaryMines, secondaryCoveredLst = secondarySynopsis

            sharedMines = min(primaryMines, secondaryMines)
            primaryOnlyMines = primaryMines - sharedMines
            primaryOnlyCovered = [Index for Index in primaryCoveredLst
                                  if Index not in secondaryCoveredLst]
            secondaryTotallyShared = all(Index in primaryCoveredLst
                                         for Index in secondaryCoveredLst)
            yield primaryOnlyMines, primaryOnlyCovered, secondaryTotallyShared


main()
