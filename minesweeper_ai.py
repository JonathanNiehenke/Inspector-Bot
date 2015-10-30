'''
Bot that plays a game of minesweeper by visually looking at the board,
moving the mouse and making decisions.
'''
# Created 11/7/14
# Version 3
# By Jonathan Niehenke

# Style Sheet
# Variables = camelCase.
# Global variable = ALL_CAPS.
# Function = lowercase_with_underscores.

# Ideas
'''
Optimize:
    Don't double check direct logic till a zero is found on board.
    Use Array or Numpy array.
'''

import win32gui # To locate window position.
import autopy # Moves the mouse and takes and looks at screen shots.
import time # To force a pause slowing it down.
import ctypes # Change console font color.
import random  # For a random sample of a set.

OUT_HANDLE = ctypes.windll.kernel32.GetStdHandle(-11)
FOCUS = set()

def init():
    '''Defines variables that may change between games.'''
    global MINEFIELD_POS, WIDTH, HEIGHT, MINEFIELD, HIDDEN, MINE_COUNT
    MINEFIELD_POS, gridSize = find_grid('Minesweeper') # Finds game grid
    WIDTH, HEIGHT = gridSize
    fieldSize = WIDTH * HEIGHT
    MINEFIELD = list(enumerate([9] * fieldSize))
    HIDDEN = set(range(fieldSize))
    MINE_COUNT = find_count()
    ratioNum = round(float(fieldSize)/MINE_COUNT, 2)
    print 'Its about 1 mine per %d of cells.' % ratioNum
    # time.sleep(1.5)

def find_grid(windowName):
    '''Finds the minesweeper grid. Returning its position and size.'''
    WinHandle = win32gui.FindWindow(None, windowName)
    win32gui.SetForegroundWindow(WinHandle)
    Left, Top, Right, Bot = win32gui.GetWindowRect(WinHandle)
    Left, Top, Right, Bot = (Left + 15, Top + 101, Right - 11, Bot - 11)
    gridPos = (Left, Top, Right, Bot)
    gridSize = ((Right - Left) / 16, (Bot - Top) / 16)
    return gridPos, gridSize

def grab_board_area():
    '''Takes a sreenShot of the minesweeper board.'''
    move_to_index(-(WIDTH/2) - WIDTH, False) # So mouse is off-board.
    #!! capture_screen((MINEFIELD_POS[2:], MINEFIELD_POS[2:])) results
    #!! in off-screen capture (black picture) or out of bounds error.
    screenArea = ((0,0), (MINEFIELD_POS[2:])) # (0, 0) prevents error.
    screenShot = autopy.bitmap.capture_screen(screenArea)
    return screenShot

def rgb_pixel(Image, x, y):
    '''Returns the RGB color of the coordinate in Image.'''
    color = Image.get_color(x, y)
    return autopy.color.hex_to_rgb(color)

def find_count():
    '''Reads the number of mines from the board.'''
    Left, Top = MINEFIELD_POS[:2]
    Left, Top = (Left + 6, Top - 40) # Right + 44, Bot - 18
    Coords = ((6,2), (2, 6), (10, 6), (6, 11), (2, 16), (10, 16), (6, 20))
    digiMaster = ('1110111', '0010010', '1011101', '1011011', '0111010',
                  '1101011', '1101111', '1010010', '1111111', '1111011')
    screenShot = grab_board_area()
    Count = 0
    for Power in xrange(2, -1, -1):
        digiStr = '' 
        for x, y in Coords:
            Color = rgb_pixel(screenShot, x + Left, y + Top)
            digiStr += '1' if Color == (255, 0, 0) else '0'
        Count += digiMaster.index(digiStr) * 10**Power
        Left += 13
    return Count

def convert_to_screen(targetIndex, Mouse=False):
    '''Converts a grid index to a screen coordinate.'''
    gridY, gridX = divmod(targetIndex, WIDTH)
    xMultiplier = 16.33 if Mouse else 16 #! Fixes mouse inaccuracy.
    gridX = MINEFIELD_POS[0] + int(gridX * xMultiplier) + 8
    gridY = MINEFIELD_POS[1] + (gridY * 16) + 8 # +8 for center.
    return (gridX, gridY)

def screen_to_grid(targetIndex, screenShot):
    '''Reads a minesweeper cell and marks it in memory.'''
    gridX, gridY = convert_to_screen(targetIndex)
    ColorLst = [(192, 192, 192), (0, 0, 255), (0, 128, 0), (255, 0, 0),
                (0, 0, 128), (128, 0, 0), (0, 128, 128), (0, 0, 0),
                (128, 128, 128)]
    C1 = rgb_pixel(screenShot, gridX, gridY + 6)
    C2 = rgb_pixel(screenShot, gridX - 1, gridY - 4)
    
    if C1 == (192, 192, 192) and C2 in ColorLst: # Uncovered & a value.
        MINEFIELD[targetIndex] = (targetIndex, ColorLst.index(C2))
        HIDDEN.remove(targetIndex)
        if [Pair[1] for Pair in adjacent(targetIndex) if Pair[1] == 9]:
            FOCUS.add(targetIndex)
    elif C1 == (128, 128, 128): # Grabs covered from else.
        pass # Including hidden, flagged and question marked. 
    else: # Catches mines and other inconsistencies.
        print "Yeah, found a bug, cause that shouldn't happen."
        debug(targetIndex)
        exit()

def mark_exposed():
    '''Reads the minesweeper board and marks in memory.'''
    screenShot = grab_board_area()
    for Idx in HIDDEN.copy():
        screen_to_grid(Idx, screenShot)
    # print ''

def both_click():
    '''Preforms a left and right click.'''
    autopy.mouse.toggle(True)
    autopy.mouse.click(autopy.mouse.RIGHT_BUTTON)
    autopy.mouse.toggle(False)

def move_to_index(targetIndex, Smooth=False):
    '''Moves the mouse onto the cell on the screen.'''
    gridX, gridY = convert_to_screen(targetIndex, True)
    #! Autopy sometimes believes points are out of bounds, its a lie.
    try:
        if Smooth:
            autopy.mouse.smooth_move(gridX, gridY)
        else:
            autopy.mouse.move(gridX, gridY)
    except ValueError:
        print 'Mouse Error; %d, %d' % (gridX, gridY)
        move_to_index(targetIndex, Smooth)
    # time.sleep(.5)

def grid_chunk(Start, Width, Height):
    '''Creates a partial targeted copy of a grid.'''
    # Unexpected results while targetIndex is on the edge are prevented
    # by shifting the targetIndex away from the edge and fixing the
    # results afterwards.
    End = Start + WIDTH*Height
    if Start % WIDTH == WIDTH - 1: # If beyond the left edge.
        Chunk = grid_chunk(Start + 1, Width, Height)
        rightEdge = range(Width - 1, Width*Height - 1, Width)
        for Idx, Val in enumerate(Chunk):
            if Idx in rightEdge: Chunk[Idx] = (-1, 0)
            # else: Chunk[Idx] = Val
        Chunk[:] = [(-1, 0)] + Chunk[:-1]
    elif End % WIDTH == WIDTH - 2: # If beyond the right edge.
        Chunk = grid_chunk(Start - 1, Width, Height)
        leftEdge = range(Width, Width*Height, Width)
        for Idx, Val in enumerate(Chunk):
            if Idx in leftEdge: Chunk[Idx] = (-1, 0)
            # else: Chunk[Idx] = Val
        Chunk[:] = Chunk[1:] + [(-1, 0)]
    elif Start / WIDTH == -1: # If beyond the top edge.
        Chunk = grid_chunk(Start + WIDTH, Width, Height)
        Chunk = [(-1, 0)]*Width + Chunk[:-Width]
    elif End / WIDTH == HEIGHT + 1: # If beyond the edge.
        Chunk = grid_chunk(Start - WIDTH, Width, Height)
        Chunk = Chunk[Width:] + [(-1, 0)] * Width
    else:
        Chunk = []
        for i in xrange(Height):
            Chunk.extend(MINEFIELD[Start: Start + Width])
            Start += WIDTH
    return Chunk

def adjacent(targetIndex):
    '''Returns the cells around a target index.'''
    chunkStart = targetIndex - WIDTH - 1
    return grid_chunk(chunkStart, 3, 3)

def cell_info(adjacentLst):
    '''Returns relevant information about what is around the cell.''' 
    cellValue = adjacentLst[4][1]
    Flags = len([(Idx, Val) for Idx, Val in adjacentLst if Val == 'F'])
    Requires = cellValue - Flags
    hiddenLst = [(Idx, Val) for Idx, Val in adjacentLst if Val == 9]
    Hidden = len(hiddenLst)
    return Requires, Hidden, hiddenLst
    
def flag(Lst):
    '''Preforms a flag mark on minesweeper board.'''
    global MINE_COUNT
    for targetIndex, Val in Lst:
        # print 'Flag: %d' % targetIndex,
        MINEFIELD[targetIndex] = (targetIndex, 'F')
        MINE_COUNT -= 1
        move_to_index(targetIndex)
        autopy.mouse.click(autopy.mouse.RIGHT_BUTTON)
        HIDDEN.remove(targetIndex)

def reveal(targetIndex):
    '''Preforms a reveal click on the minesweeper board.'''
    # print 'Reveal: %d' % targetIndex,
    move_to_index(targetIndex)
    both_click()

def open_cell(Lst):
    for targetIndex in Lst:
        move_to_index(targetIndex)
        autopy.mouse.click()

def direct_logic():
    ''' Applies the obvious logic of a single cell to the board.'''
    for targetIndex in FOCUS.copy():
        adjacentLst = adjacent(targetIndex)
        Requires, Hidden, hiddenLst = cell_info(adjacentLst)
        if not Hidden: # If none are hidden.
            FOCUS.remove(targetIndex)
        elif not Requires: # If all required mine were found.
            reveal(targetIndex)
            # print ''
        elif Requires == Hidden: # If hidden are mines.
            flag(hiddenLst)
            # print ''

def indirect_logic():
    '''Applies the overlapping logic of multiple cells to the board.'''
    #! Will try flagging the same index
    # Needs to update as it flags and opens.
    # May need optimization it notably pauses during this.
    for targetIndex in FOCUS.copy():
        targetLst = adjacent(targetIndex)
        targetInfo = cell_info(targetLst)
        del targetLst[4] # Removes itself the targetIndex and value.
        adjacentFocus = [(Idx, Val) for Idx, Val in targetLst if Idx in FOCUS]
        for otherIndex, Val in adjacentFocus:
            otherInfo = cell_info(adjacent(otherIndex))
            hiddenSharedLst = [Pair for Pair in targetInfo[2]
                                  if Pair in otherInfo[2]]
            hiddenNotSharedLst = [Pair for Pair in targetInfo[2]
                                  if not Pair in hiddenSharedLst]
            hiddenNotShared = len(hiddenNotSharedLst)
            minesNotShared = targetInfo[0] - min(targetInfo[0], otherInfo[0])

            # if non-shared hidden cells == required - shared mines.
            if hiddenNotShared == minesNotShared and hiddenNotSharedLst:
                # time.sleep(.5)
                flag(hiddenNotSharedLst)
                targetInfo = cell_info(adjacent(targetIndex))
                # print ''
            # if a cell's last mine IS shared and completes another.
            elif (otherInfo[2] == hiddenSharedLst and
                    not minesNotShared and hiddenNotSharedLst):
                # time.sleep(.5)
                open_cell([Idx for Idx, Val in hiddenNotSharedLst])
                targetInfo = cell_info(adjacent(targetIndex))
                # print ''

# def adjacent_focus():
    # '''Finds a series of adjacent focused cells.'''
    # searchLst, senarioFocus = [FOCUS.copy().pop()], set()
    # while searchLst:
        # for Idx, Val in adjacent(searchLst.pop(0)):
            # if Idx in FOCUS and not Idx in senarioFocus:
                # searchLst.append(Idx)
                # senarioFocus.add(Idx)
    # return senarioFocus

# def senario_area(senarioFocus):
    # Vert, Flat = zip(*[divmod(Idx, WIDTH) for Idx in senarioFocus])
    # Left, Top, Right, Bot = (min(Flat), min(Vert), max(Flat), max(Vert))
    # Left, Top, Right, Bot = Left - 1, Top - 1, Right + 2, Bot + 2
    # senarioWidth, senarioHeight = Right - Left, Bot - Top
    # senarioStart = Top*WIDTH + Left
    # return grid_chunk(senarioStart, senarioWidth, senarioHeight)

def explore():
    '''Randomly picks a cell still hidden and checks for a mine.'''
    targetIndex = random.sample(HIDDEN, 1)[0]
    open_cell([targetIndex])
    screenShot = grab_board_area()
    gridX, gridY = convert_to_screen(targetIndex)
    Color = rgb_pixel(screenShot, gridX, gridY + 6)
    if Color == (0, 0, 0):
        print "Found a mine while exploring. Guess my luck ran out."
        exit()

def text_color(Text, colorCode):
    ctypes.windll.kernel32.SetConsoleTextAttribute(OUT_HANDLE, colorCode)
    print Text,
    ctypes.windll.kernel32.SetConsoleTextAttribute(OUT_HANDLE, 0x000A)

def thought_viewer():
    print '\nMines left: %d' % MINE_COUNT
    for Idx, Val in MINEFIELD:
        if not Idx % WIDTH:
            print ''
        
        if Idx in FOCUS:
            text_color(Val, 0x000E)
        elif Idx in HIDDEN:
            text_color(Val, 0x0008)
        elif Val == 'F':
            text_color(Val, 0x0047)
        else:
            print Val,
    
    print ''

def main():
    Check = 2
    while HIDDEN:
        Previous = MINEFIELD[:]
        mark_exposed() # Reads the screen and marks it in memory.
        direct_logic() # The logic to solve using single cell info.
        # thought_viewer() # To see what it sees. Diagnostic uses.
        Check = Check - 1 if MINEFIELD == Previous else 2
        
        if not Check: # Double checks before using advanced_logic.
            indirect_logic()
            Check = Check if MINEFIELD == Previous else 2
            
        if not Check: # If advanced logic did nothing.
            # break
            explore()

def debug(targetIndex):
    print ''
    cellValue = MINEFIELD[targetIndex][1]
    adjacentLst = adjacent(targetIndex)
    Flags = len([(Idx, Val) for Idx, Val in adjacentLst if Val == 'F'])
    Hidden = len([(Idx, Val) for Idx, Val in adjacentLst if Val == 9])
    print adjacentLst
    print 'Flag: cellValue %d - Flags %d == Hidden %d' % (cellValue, Flags, Hidden)
    print 'Reveal: cellValue %d == Flags %d' % (cellValue, Flags)
    thought_viewer()
    print ''
    print 'HIDDEN\n', HIDDEN
    print '\nFOCUS\n', FOCUS

def new():
    screenShot = grab_board_area()
    screenShot.save(r'E:\Desktop\MsweepV1\%d.png' % int(time.time()))
    move_to_index(-(WIDTH/2) - WIDTH)
    autopy.mouse.click()

if __name__ == '__main__':
    init()
    main()