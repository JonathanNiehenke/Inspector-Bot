'''
Bot that plays a game of Bejeweled by reading the screen, moving the
    mouse and making decisions favoring special gem creation.
'''
# Began 4/3/2015
# Beta Version 3
# By Jonathan Niehenke

# Naming Styles -- Why? For variable and function distinction.
#   Variables = mixedCamelCase, Global variable = ALL_CAPS,
#   Function/Methods/Modules = lowercase_with_underscores,
#   Class = CamelCase

# Definition Order -- Why? Improve reading navigation.
#   In order of use (hierarchical top to bottom). Unless shared by a
#   continuous defined group of functions or defined elsewhere which
#   would note a  #def@ comment.

# Personal challenge: -- Why? For improvement.
#   Clean clear code > performance benefits > type saving.
#   Expressive verbs in function names express action and imply output.
#   Frequently, succinctly, and completely inform future code readers.
#   Well named single task functions express their intent in the code.
#   Handling errors is easier, cheaper and clearer than error dodging.
#   Disclose assumptions through assertions.
#   Simple implementation is easier to build, fix and modify.

from __future__ import print_function
import sys
import time
import threading
import Queue
from operator import itemgetter
from itertools import izip, product
from copy import deepcopy

import numpy

import bejeweled_iface
import Bj_Reader

WIDTH = 8  # Constant preventing move found from across the board.


def main():
    bejeweled_iface.init()  # Sets variables dependent on the running
    # game. Also brings the game window to the front.
    time.sleep(2)
    play_bejewled()


def play_bejewled():
    '''Plays bejeweled by matching sequences of identical colors.'''
    movesPerLook, moveWait = 1, 27.0/32
    Menu = False
    redundantReader, boardQ = spawn_redundant_reader()

    while not Menu:  # Fails on menu open or end game statistics.
        colorBoard, blankCount, boardArray = preceive_board(saveToFile=True)
        boardQ.put((boardArray, colorBoard))
        print(blankCount, end=' ')
        improvedPatternLst, basicPatternLst = collect_board_patterns(
            colorBoard)
        improvedPatternLst.sort(key=favor_long_high)
        foundMoveLst = identify_moves(improvedPatternLst, colorBoard)

        if foundMoveLst:
            moveGen = foundMoveLst.__iter__()
        else:
            basicPatternLst.sort(key=favor_long_high)
            foundMoveLst = identify_moves(basicPatternLst, colorBoard)
            moveGen = foundMoveLst.__iter__()

        for _ in xrange(movesPerLook):
            try:
                From, To, _ = moveGen.next()
            except StopIteration:
                break
            else:
                bejeweled_iface.execute_mouse_drag(From, To)
                time.sleep(moveWait)

        colorBoard, blankCount, _ = preceive_board(saveToFile=False)
        Menu = 26 < blankCount < 38
        while 1 < blankCount and not Menu:
            bejeweled_iface.rest_mouse()
            time.sleep(0.125 + blankCount/10.0/8 + blankCount/40*2)
            colorBoard, blankCount, _ = preceive_board(saveToFile=False)
            Menu = 26 < blankCount < 38
    else:
        boardQ.join()
        boardQ.put(None)
        redundantReader.join()
        time.sleep(5)
        Bj_Reader.query_referee()
        Bj_Reader.save_ciphers()
        extendFilename = '_{}End'.format(blankCount)

'''
    if not allPatterns and not all(linkLst):
        for Pattern in patternLst:
            #def@ dropper() follows simulate_affect.
            Board = dropper(Board, Pattern  # Removes combo patterns.
        patternLst[:], linkLst[:] = find_patterns(Board, allPatterns)
'''


def spawn_redundant_reader():
    '''Creates and starts an apprentice thread.'''
    boardQ = Queue.Queue(25)
    redundantReader = threading.Thread(
        target=Bj_Reader.read_queue, args=(boardQ,))
    redundantReader.setDaemon(True)
    redundantReader.start()
    return redundantReader, boardQ


def preceive_board(saveToFile=False):
    ''''''
    if saveToFile:
        filePathName = '.\\reads\\{:.0f}.png'.format(time.time())
    else:
        filePathName = ''

    colorBoard, boardArray = bejeweled_iface.translate_board(filePathName)
    blankCount = (colorBoard == ' ').sum()
    return colorBoard, blankCount, boardArray


def collect_board_patterns(Board):
    '''Returns collection of improved and basic pattern information.'''
    basicRowPatternLst = collect_basic_row_patterns(Board)
    basicColumnPatternLst = transpose_index_pairs(
        collect_basic_row_patterns(Board.T))

    improvedPatternLst = improve_pattern_collection(
        deepcopy(basicRowPatternLst))
    improvedPatternLst.extend(
        improve_pattern_collection(deepcopy(basicColumnPatternLst)))
    improvedPatternLst.extend(
        collect_star_patterns(basicRowPatternLst, basicColumnPatternLst))

    return improvedPatternLst, basicRowPatternLst + basicColumnPatternLst


def collect_basic_row_patterns(Board):
    '''Returns collection of basic patterns found along each row.'''
    basicPatternLst = []
    for I, Row in enumerate(Board):
        rowEnum = enumerate(Row)
        _, A = rowEnum.next()  # Efficiently obtain three values along
        _, B = rowEnum.next()  # the leading edge of each row search.
        for J, C in rowEnum:
            Pattern = identify_pattern(A, B, C, I, J)
            if Pattern:
                basicPatternLst.append(Pattern)
            A, B = B, C  # Moves values down the row.

    return basicPatternLst


def identify_pattern(A, B, C, I, J):
    '''Returns I, J index of found patterns and links.'''

    Rpair = B == C  # Pair right of the Link.
    Lpair = A == B  # Pair left  of the Link.

    if ' ' in (A, B, C):
        Pattern = None  # Ignore blanks. Nothing to see here! :)
    # elif Lpair and Rpair:
    #   Pattern = ([(I, J - 2), (I, J - 1), (I, J)], None)  # A combo.
    elif Rpair:
        Pattern = ([(I, J - 1), (I, J)], (I, J - 2, B))
    elif Lpair:
        Pattern = ([(I, J - 2), (I, J - 1)], (I, J, A))
    elif A == C:
        Pattern = ([(I, J - 2), (I, J)], (I, J - 1, A))  # Split.
    else:
        Pattern = None  # Nothing was found.

    return Pattern


def transpose_index_pairs(PatternLst):
    '''Swaps the index pairs of patterns to reflect column indexes.'''
    swappedPatternLst = []
    for Formation, Link in PatternLst:
        Formation[:] = [(I, J) for J, I in Formation]
        if Link:
            X, Y, Color = Link
            Link = Y, X, Color
        swappedPatternLst.append((Formation, Link))
    return swappedPatternLst


def improve_pattern_collection(basicPatternLst):
    '''Creates a list of improved patterns with larger formations.'''
    improvedPatternLst = []
    for Formation, Link in basicPatternLst:

        try:
            previousFormation, previousLink = improvedPatternLst[-1]
        except IndexError:  # improvedPatternLst is empty.
            previousFormation = [(-1, -1), (-1, -1)]  # Bogus Values.
            previousLink = (-1, -1, -1)

        Overlaps = Formation[0] in previousFormation
        currentCombo, previousCombo = Link is None, previousLink is None

        if Link == previousLink:
            previousFormation.append(Formation[-1])
        # elif currentCombo and Overlaps  # the previousFormation.
        #   Replace the previous incomplete pattern with the combo.
        #   improvedPatternLst[-1] = (Formation, Link)
        else:  # if not (previousCombo and Overlaps)  # the Formation.
            # Formation is included in the improved list.
            improvedPatternLst.append((Formation, Link))

    return improvedPatternLst


def collect_star_patterns(rowPatternLst, columnPatternLst):
    '''Returns collection of star patterns.'''
    Intersections = collect_intersections(rowPatternLst, columnPatternLst)
    if Intersections:
        crossRowPatterns = collect_crossing_patterns(
            rowPatternLst, Intersections)
        crossColumnPatterns = collect_crossing_patterns(
            columnPatternLst, Intersections)
        starPatterns = join_crossing_patterns(
            crossRowPatterns, crossColumnPatterns)
    else:
        starPatterns = []

    return starPatterns


def collect_intersections(rowPatternLst, columnPatternLst):
    '''Returns a set of shared links of both collections.'''
    _, rowLinkLst = izip(*rowPatternLst)
    _, columnLinkLst = izip(*columnPatternLst)
    return set(rowLinkLst) & set(columnLinkLst)


def collect_crossing_patterns(PatternLst, Intersections):
    '''Creates a list of the links paired with patterns.'''
    crossingPatternLst = []
    for Formation, Link in PatternLst:
        Crossing = Link in Intersections

        try:
            previousFormationLst, previousLink = crossingPatternLst[-1]
        except IndexError:  # improvedPatternLst is empty.
            previousLink = (-1, -1, -1)  # Bogus Values.
            previousFormation = [[(-1, -1), (-1, -1)]]

        if Crossing and Link == previousLink:
            previousFormationLst.append(Formation)
        elif Crossing:
            crossingPatternLst.append(([Formation], Link))

    return sorted(crossingPatternLst, key=itemgetter(1))


def join_crossing_patterns(crossRowPatterns, crossColumnPatterns):
    '''Joins row and column crossing patterns.'''
    rowFormationLst, Intersections = izip(*crossRowPatterns)
    columnFormationLst, _ = izip(*crossColumnPatterns)
    pairedFormations = izip(rowFormationLst, columnFormationLst)
    patternLst = []
    for formationPair, Link in izip(pairedFormations, Intersections):
        crossingFormations = product(*formationPair)
        patternLst.extend([(sorted(rForm + cForm), Link)
                           for rForm, cForm in crossingFormations])
    return patternLst


def favor_long_high(Pattern):
    # Returns the Formation's length from maximum and position.
    Formation, _ = Pattern
    return 6 - len(Formation), Formation[0][0]


def identify_moves(patternLst, Board):
    '''Returns list of moves that join incomplete patterns.'''
    foundMoves = []
    for Formation, Link in patternLst:
        try:
            Y, X, Color = Link
        except TypeError:
            print(Formation, Link)
            print(Board)
            raise
        # Where to find a move: The four indexes around the link.
        aroundLink = ((Y - 1, X), (Y, X - 1), (Y, X + 1), (Y + 1, X))
        # Where NOT to look: In the formation and beyond the edge.
        Trespassing = Formation + [(-1, X), (Y, -1), (WIDTH, X), (Y, WIDTH)]
        # Where to search: aroundLink that is not trespassing.
        Search = (Index for Index in aroundLink if Index not in Trespassing)
        # The searched cells that match contain the necessary color.
        Linkage = (Index for Index in Search if Board[Index] == Color)
        for yTo, xTo in Linkage:
            foundMoves.append(((X, Y), (xTo, yTo), Formation))
    return foundMoves

if __name__ == '__main__':
    main()
