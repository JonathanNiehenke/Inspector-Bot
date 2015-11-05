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

from collections import OrderedDict
from fractions import Fraction
from functools import partial
from random import choice
from time import sleep, time
import argparse

import win_terface

class MinesweeperInterface(OrderedDict):
    """
    An object to automate playing the Windows XP version of minesweeper.
   """

    left_minefield_margin, top_minefield_margin, cell_size = 15, 101, 16
    color_decoder = {
        (192, 192, 192): 0,
        (0, 0, 255): 1,
        (0, 128, 0): 2,
        (255, 0, 0): 3,
        (0, 0, 128): 4,
        (128, 0, 0): 5,
        (0, 128, 128): 6,
        (0, 0, 0): 7,
        (128, 128, 128): 8,
        (0, 0, 0, 0): 'M', # Mine
        (128, 128, 128, 0): 'C',  # Covered
        }

    def __init__(self, **Options):
        OrderedDict.__init__(self)
        self.game_window = win_terface.WindowElement(
            'Minesweeper', bringTop=True)
        self.window_left, self.window_top, _, _ = self.game_window.position
        minefieldWidth = (self.game_window.width - 26)
        minefieldHeight = (self.game_window.height - 112)
        self.width_by_cells = minefieldWidth // self.cell_size
        self.height_by_cells = minefieldHeight // self.cell_size
        self.reset_button_index = (self.width_by_cells/2, -2)
        indexCollection = [(X, Y) for Y in range(self.height_by_cells)
                           for X in range(self.width_by_cells)]
        self.unsolved_cell_collection = set(indexCollection)
        self.open_cells, self.flag_cells, self.save_dir = (
            self.manage_options(Options))
        self.read_minefield()

    def manage_options(self, Options):
        openCells = partial(
            self.preform_to_cells, self.click_open, Options.get('pause', 0))
        flaggingFunc = self.click_flag if Options['flag'] else self.mark_flag
        flagCells = partial(
            self.preform_to_cells, flaggingFunc, Options.get('pause', 0))
        saveDir = Options.get('record', None)
        return openCells, flagCells, saveDir

    def read_minefield(self, indexCollection=None):
        assert 'M' not in self.values()
        if indexCollection is None:
            indexCollection = self.unsolved_cell_collection.copy()
        captureImage = self.game_window.screen_capture()
        try:
            filePathname = ''.join([self.save_dir, '\\', str(time()), '.bmp'])
        except TypeError:
            pass
        else:
            captureImage.save(filePathname)
        for cellIndex in indexCollection.copy():
            self[cellIndex] = self.decipher_mineweeper_cell(
                captureImage, cellIndex)

    def decipher_mineweeper_cell(self, Object, cellIndex):
        """Return the minesweeper value of cell at Index."""
        windowX, windowY = self.convert_cell_index_to_window(*cellIndex)
        macroColor = Object[windowX + 14, windowY + 8] + (0,)
        try:
            cellValue = self.color_decoder[macroColor]
        except KeyError:
            cellValue = self.color_decoder[Object[windowX + 7, windowY + 4]]
        return cellValue

    def reset(self):
        """Preforms the mouse action to reset the minefield."""
        self.open_cells(self.reset_button_index)

    def preform_to_cells(self, Function, Pause, *cellCollection):
        for Index in cellCollection:
            Function(Index, Pause)

    def click_open(self, Index, Pause):
        """Preforms the mouse action to open the cell at index."""
        win_terface.execute_mouse(self.convert_cell_index_to_screen(*Index))
        sleep(Pause)
        win_terface.execute_mouse(('Left', 'Click'))

    def click_flag(self, Index, Pause):
        """Preforms the mouse action to flag the cell at index."""
        win_terface.execute_mouse(self.convert_cell_index_to_screen(*Index))
        sleep(Pause)
        win_terface.execute_mouse(('Right', 'Click'))
        self.mark_flag(Index)

    def mark_flag(self, Index, *_):
        self[Index] = 'F'
        self.unsolved_cell_collection.discard(Index)

    def collect_adjacent_cells(self, Index):
        """Return a list of surrounding cell indexes and values."""
        X, Y = Index
        rangeX = [V for V in range(X - 1, X + 2)
                  if -1 < V < self.width_by_cells]
        rangeY = [V for V in range(Y - 1, Y + 2)
                  if -1 < V < self.height_by_cells]
        return [((X, Y), self[(X, Y)]) for Y in rangeY for X in rangeX]

    def identify_discovered_cell(self):
        """Return the value of a randomly opened cell."""
        targetIndex = choice(list(self.unsolved_cell_collection))
        self.open_cells(targetIndex)
        sleep(3/1024)  # Otherwise the cell is read too fast.
        cellValue = self.decipher_mineweeper_cell(self.game_window, targetIndex)
        return cellValue

    def convert_cell_index_to_screen(self, X, Y):
        """Converts cell index to the expected screen X and Y."""
        Center = self.cell_size // 2
        windowX, windowY = self.convert_cell_index_to_window(X, Y)
        screenX = self.window_left + windowX + Center
        screenY = self.window_top + windowY + Center
        return screenX, screenY

    def convert_cell_index_to_window(self, X, Y):
        """Converts the X, Y of a cell to its X, Y in the window."""
        windowX = self.left_minefield_margin + (self.cell_size * X)
        windowY = self.top_minefield_margin + (self.cell_size * Y)
        return windowX, windowY

    def __str__(self):
        args = [(str(V) for V in self.values())] * self.width_by_cells
        return '\n'.join(' '.join(Row) for Row in zip(*args))


def main():
    Parser = argparse.ArgumentParser()
    Parser.add_argument('-p', '--pause', default=0.0, type=pause_time,
                        help="The pause time in seconds between actions.")
    Parser.add_argument('-f', '--flag', action='store_true',
                        help="Enables flagging mines otherwise leaves blank.")
    Parser.add_argument('-r', '--record', '--record_into_directory',
                        help="Directory to save the images the bot sees.")
    Parser.add_argument('-d', '--display', '--display_end', action='store_true',
                        help="Display the minefield before exiting.")
    Options = vars(Parser.parse_args())
    play_minesweeper(Options)


def pause_time(Str):
    Pause = float(Fraction(Str))
    if not 0.0 <= Pause <= 5.0:
        raise argparse.ArgumentTypeError(
            'Value has to include or be within 0 and 5.')
    return Pause 


def play_minesweeper(Options):
    Minefield = MinesweeperInterface(**Options)
    if 0 not in Minefield.values():
        attain_suitable_start(Minefield)
        Minefield.read_minefield()
    while Minefield.unsolved_cell_collection:
        Changed = apply_logic(Minefield)
        if not Changed and Minefield.identify_discovered_cell() == 'M':
            print("Forced to explore and hit a mine. Unlucky I guess.")
            if Options.get('display-end'):
                print(Minefield)
            exit()
        else:
            Minefield.read_minefield()
    if Options.get('display'):
        print(Minefield)


def attain_suitable_start(Minefield):
    """Explores and resets till a blank cell is uncovered."""
    cellValue, Reset = 1, 0
    while cellValue:
        cellValue = Minefield.identify_discovered_cell()
        if cellValue == 'M':
            Reset += 1
            Minefield.reset()
            sleep(1/64)
    Msg = 'Reset {} time{} before a suitable start was found.'
    print(Msg.format(Reset, '' if Reset == 1 else 's'))


def apply_logic(Minefield):
    """Deduce, flag, and open cells in Minefield."""
    Previous = Minefield.unsolved_cell_collection.copy()
    apply_isolated_logic(Minefield)
    Changed = Previous != Minefield.unsolved_cell_collection
    if not Changed:
        apply_overlapping_logic(Minefield)
        Minefield.read_minefield()
        Changed = Previous != Minefield.unsolved_cell_collection
    return Changed


def apply_isolated_logic(Minefield):
    """Deduce, flag and open around individual cells."""
    Unsolved = Minefield.unsolved_cell_collection.copy()
    for targetInfo in condense_about_indexes(Minefield, Unsolved):
        targetIndex, lackingMines, coveredLst = targetInfo
        Covered = len(coveredLst)
        if not Covered:
            Minefield.unsolved_cell_collection.discard(targetIndex)
        elif not lackingMines:
            Minefield.open_cells(*coveredLst)
        elif lackingMines == Covered:
            Minefield.flag_cells(*coveredLst)


def condense_about_indexes(Minefield, indexCollection):
    """Return the meaningful info about Indexes in indexCollection."""
    for targetIndex in indexCollection:
        requiredMines = Minefield[targetIndex]
        adjacentCells = Minefield.collect_adjacent_cells(targetIndex)
        flaggedMines = len([Val for _,  Val in adjacentCells if Val == 'F'])
        try:
            lackingMines = requiredMines - flaggedMines
        except TypeError:  # requiredMines = 'F' or 'C'
            pass
        else:
            coveredLst = [Index for Index, Val in adjacentCells if Val == 'C']
            yield targetIndex, lackingMines, coveredLst


def apply_overlapping_logic(Minefield):
    """Deduce, flag and open the non-overlapping cells of two cells."""
    # https://www.youtube.com/watch?v=R6C_TZHDXCw#t=224 explains logic.
    Unsolved = Minefield.unsolved_cell_collection.copy()
    for overlappingOutline in condense_overlaps(Minefield, Unsolved):
        primaryOnlyMines, primaryOnlyCovered, secondaryTotallyShared = (
            overlappingOutline)
        if not primaryOnlyMines and secondaryTotallyShared:
            Minefield.open_cells(*primaryOnlyCovered)
        elif primaryOnlyMines == len(primaryOnlyCovered):
            Minefield.flag_cells(*primaryOnlyCovered)


def condense_overlaps(Minefield, Unsolved):
    """Return the meaningful info about two overlapping cells."""
    for primaryInfo in condense_about_indexes(Minefield, Unsolved):
        primaryIndex, *primaryOutline = primaryInfo
        adjacentCells = Minefield.collect_adjacent_cells(primaryIndex)
        adjacentIndexes, _ = zip(*adjacentCells)
        for secondaryInfo in condense_about_indexes(Minefield, adjacentIndexes):
            _, *secondaryOutline = secondaryInfo
            yield condense_overlapping_outines(primaryOutline, secondaryOutline)


def condense_overlapping_outines(primaryOutline, secondaryOutline):
    """Return the meaningful info from overlapping Outlines."""
    primaryMines, primaryCoveredLst = primaryOutline
    secondaryMines, secondaryCoveredLst = secondaryOutline
    sharedMines = min(primaryMines, secondaryMines)
    primaryOnlyMines = primaryMines - sharedMines
    primarySet, secondarySet = set(primaryCoveredLst) , set(secondaryCoveredLst)
    primaryOnlyCovered = primarySet.difference(secondarySet)
    secondaryTotallyShared = secondarySet.issubset(primarySet)
    return primaryOnlyMines, primaryOnlyCovered, secondaryTotallyShared


if __name__ == '__main__':
    main()
