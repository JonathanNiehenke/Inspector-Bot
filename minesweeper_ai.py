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
from functools import partial
from random import choice
from time import sleep, time
import argparse
import sys

from PIL import Image, ImageGrab

sys.path.append(r'F:\Source\ai_projects')
import win_terface

class MinesweeperInterface(OrderedDict):

    tile_size = 16
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

    def __init__(self, **Options):
        OrderedDict.__init__(self)
        self.window = win_terface.WindowElement('Minesweeper')
        self.left, self.top, _, _ = self.window.position
        gridXPadding, gridYPadding = 26, 112
        self.width = (self.window.width - gridXPadding)//self.tile_size
        self.height = (self.window.height - gridYPadding)//self.tile_size
        self.reset_button = (self.width/2, -2)
        Keys = [(X, Y) for Y in range(self.height) for X in range(self.width)]
        self.read_field(Keys)
        self.unsolved = set(Keys)
        self.open_cells = partial(self.apply_function, self.click_open)
        flagType = {True: self.click_flag, False: self.remember_flag}
        self.flag_cells = partial(self.apply_function, flagType[Options['flag']])
        self.pause = Options['pause']


    def read_field(self, Keys=None):
        assert 'M' not in self.values()
        if Keys is None:
            Keys = self.unsolved.copy()
        self.window.update_capture()
            # r'E:\Pictures\Minesweeper\Read{:.2f}.bmp'.format(time()))
        for Index in Keys.copy():
            self[Index] = self.identify_cell_value(
                    self.window.identify_capture_pixel, Index)

    def identify_cell_value(self, idPixelFunc, Index):
        windowX, windowY = self.convert_cell_to_window(*Index)
        macroColor = idPixelFunc(windowX + 14, windowY + 8)
        try:
            cellValue = self.cipher[macroColor + (0,)]
        except KeyError:
            valueColor = idPixelFunc(windowX + 7, windowY + 4)
            cellValue = self.cipher[valueColor]
        return cellValue

    def convert_cell_to_window(self, X, Y):
        gridLeft, gridTop = 15, 101
        windowX = gridLeft + (self.tile_size * X)
        windowY = gridTop + (self.tile_size * Y)
        return windowX, windowY

    def reset(self):
        self.open_cells(self.reset_button)

    def apply_function(self, Function, *toCells):
        for Index in toCells:
            sleep(self.pause)
            Function(Index)

    def click_open(self, Index):
        win_terface.execute_mouse(self.convert_cell_to_screen(*Index))
        win_terface.execute_mouse(('Left', 'Click'))

    def click_flag(self, Index):
        win_terface.execute_mouse(self.convert_cell_to_screen(*Index))
        win_terface.execute_mouse(('Right', 'Click'))
        self.remember_flag(Index)

    def remember_flag(self, Index):
        self[Index] = 'F'
        self.unsolved.discard(Index)

    def convert_cell_to_screen(self, X, Y):
        """Converts cell index to the expected screen X and Y."""
        (windowX, windowY), Center = self.convert_cell_to_window(X, Y), 8
        return self.left + windowX + Center, self.top + windowY + Center

    def collect_adjacent(self, Index):
        X, Y = Index
        rangeX = [V for V in range(X - 1, X + 2) if -1 < V < self.width]
        rangeY = [V for V in range(Y - 1, Y + 2) if -1 < V < self.height]
        return [((X, Y), self[(X, Y)]) for Y in rangeY for X in rangeX]

    def identify_discovered_cell(self):
        targetIndex = choice(list(self.unsolved))
        self.open_cells(targetIndex)
        sleep(3/1024)
        cellValue = self.identify_cell_value(
            self.window.identify_current_pixel, targetIndex)
        return cellValue

    def __str__(self):
        args = [(str(V) for V in self.values())] * self.width
        return '\n'.join(' '.join(Row) for Row in zip(*args))


def main():
    Speed = {'Fastest': 0, 'Faster': 1/8, 'Fast': 1/4, 'Normal': 1/2}
    Parser = argparse.ArgumentParser()
    Parser.add_argument('-f', '--flag', action="store_false")
    Group = Parser.add_mutually_exclusive_group()
    Group.add_argument('-s', '--speed', choices=Speed)
    Group.add_argument('-p', '--pause', default=3/4, type=float)
    Options = vars(Parser.parse_args())
    pauseOverride = Speed.get(Options['speed'], None)
    if pauseOverride is not None:
        Options['pause'] = pauseOverride
    elif not 0 <= Options['pause'] <= 2:
        print(
        "Custome pause time is unacceptable. Continuing with 3/4 seconds.")
        Options['pause'] = 3/4
    play_minesweeper(**Options)


def play_minesweeper(**Options):
    Start = time()
    Minefield = MinesweeperInterface(**Options)
    if 0 not in Minefield.values():
        Start = attain_suitable_start(Minefield)
        Minefield.read_field()
    while Minefield.unsolved:
        Changed = apply_logic(Minefield)
        if not Changed and Minefield.identify_discovered_cell() == 'M':
            print("Forced to explore and hit a mine. Unlucky I guess.")
            print(Minefield)
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
            sleep(1/4)
            Start = time()
    print('Reset {} time{}.'.format(Reset, '' if Reset == 1 else 's'))
    return Start


def apply_logic(Minefield):
    Previous = Minefield.unsolved.copy()
    apply_isolated_logic(Minefield)
    # Minefield.read_field()
    Changed = Previous != Minefield.unsolved
    if not Changed:
        apply_overlapping_logic(Minefield)
        Minefield.read_field()
        Changed = Previous != Minefield.unsolved
    return Changed

def apply_isolated_logic(Minefield):
    Unsolved = Minefield.unsolved.copy()
    for targetIndex, targetSynopsis in comprehend_indexes(Unsolved, Minefield):
        lackingMines, coveredLst = targetSynopsis
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
            yield targetIndex, (lackingMines, coveredLst)


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
    for primaryInfo in comprehend_indexes(Unsolved, Minefield):
        primaryIndex, primarySynopsis = primaryInfo
        indexAdjacent, _ = zip(*Minefield.collect_adjacent(primaryIndex))
        for secondaryInfo in comprehend_indexes(indexAdjacent, Minefield):
            _, secondarySynopsis = secondaryInfo
            yield analyze_synopses(primarySynopsis, secondarySynopsis)

def analyze_synopses(primarySynopsis, secondarySynopsis):
    primaryMines, primaryCoveredLst = primarySynopsis
    secondaryMines, secondaryCoveredLst = secondarySynopsis
    sharedMines = min(primaryMines, secondaryMines)
    primaryOnlyMines = primaryMines - sharedMines
    primaryOnlyCovered = [Index for Index in primaryCoveredLst
                          if Index not in secondaryCoveredLst]
    secondaryTotallyShared = all(Index in primaryCoveredLst
                                 for Index in secondaryCoveredLst)
    return primaryOnlyMines, primaryOnlyCovered, secondaryTotallyShared


main()
