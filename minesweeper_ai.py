'''

'''
# Created 10/29/14
# By Jonathan Niehenke

# Style Sheet
# Variables = camelCase.
# Global variable = ALL CAPS.
# Function = lowercase_with_underscores.

#Notes and Ideas:
'''
'''

import win32gui # To locate window position.
import autopy # Moves the mouse, takes screen shots and looks at them.
import time # To slow it down.
import ctypes # Change console font color.
import random  # For a random sample of a set.

OUT_HANDLE = ctypes.windll.kernel32.GetStdHandle(-11)
FOCUS = set()

def __init__():
    global MINEFIELD_POS, WIDTH, FIELD_SIZE, MINEFIELD, HIDDEN
    MINEFIELD_POS, gridSize = find_grid('Minesweeper') # Finds game grid
    WIDTH, Height = gridSize
    FIELD_SIZE = WIDTH * Height
    MINEFIELD = list(enumerate([9] * FIELD_SIZE))
    HIDDEN = set(range(FIELD_SIZE))

def find_grid(windowName):
    WinHandle = win32gui.FindWindow(None, windowName)
    win32gui.SetForegroundWindow(WinHandle)
    Left, Top, Right, Bot = win32gui.GetWindowRect(WinHandle)
    Left, Top, Right, Bot = (Left + 15, Top + 101, Right - 11, Bot - 11)
    gridPos = (Left, Top, Right, Bot)
    gridSize = ((Right - Left) / 16, (Bot - Top) / 16)
    return gridPos, gridSize

def grab_screen_area():
    move_to_index(-(WIDTH/2) - WIDTH, False) # So mouse is off-board.
    #!! capture_screen((MINEFIELD_POS[2:], MINEFIELD_POS[2:])) results
    #!! in off-screen capture (black picture) or out of bounds error.
    screenArea = ((0,0), (MINEFIELD_POS[2:])) # (0, 0) prevents error.
    screenShot = autopy.bitmap.capture_screen(screenArea)
    return screenShot

def convert_to_screen(targetIndex, Mouse=False):
    gridY, gridX = divmod(targetIndex, WIDTH)
    xMultiplier = 16.33 if Mouse else 16 #! Fixes mouse inaccuracy.
    gridX = MINEFIELD_POS[0] + int(gridX * xMultiplier) + 8
    gridY = MINEFIELD_POS[1] + (gridY * 16) + 8 # +8 for center.
    return (gridX, gridY)

def screen_to_grid(targetIndex, screenShot):
    gridX, gridY = convert_to_screen(targetIndex)
    ColorLst = [(192, 192, 192), (0, 0, 255), (0, 128, 0), (255, 0, 0),
                (0, 0, 128), (128, 0, 0), (0, 128, 128), (0, 0, 0),
                (128, 128, 128)]
    C1 = autopy.color.hex_to_rgb(screenShot.get_color(gridX, gridY + 6))
    C2 = autopy.color.hex_to_rgb(screenShot.get_color(gridX - 1, gridY - 4))
    
    if C1 == (192, 192, 192) and C2 in ColorLst: # Uncovered & a value.
        MINEFIELD[targetIndex] = (targetIndex, ColorLst.index(C2))
        HIDDEN.remove(targetIndex)
        if [Pair[1] for Pair in adjacent(targetIndex) if Pair[1] == 9]:
            FOCUS.add(targetIndex)
    elif C1 == (128, 128, 128): # Covered ## grabs unknown from else.
        pass
        # if C2 == (255, 0, 0): # And a flag.
            # MINEFIELD[targetIndex] = (targetIndex, 'M')
            # HIDDEN.remove(targetIndex)
    else:
        print "Yeah, found a bug, cause that shouldn't happen."
        print C1, gridX, gridY
        debug(targetIndex)
        exit()

def mark_exposed():
    screenShot = grab_screen_area()
    for Idx in HIDDEN.copy():
        screen_to_grid(Idx, screenShot)
    print ''

def both_click():
    autopy.mouse.toggle(True)
    # time.sleep(0.001)
    autopy.mouse.click(autopy.mouse.RIGHT_BUTTON)
    autopy.mouse.toggle(False)

def move_to_index(targetIndex, Smooth=False):
    gridX, gridY = convert_to_screen(targetIndex, True)
    # Autopy sometimes believes points are out of bounds, its a lie.
    try:
        if Smooth:
            autopy.mouse.smooth_move(gridX, gridY)
        else:
            autopy.mouse.move(gridX, gridY)
    except ValueError:
        print 'Mouse Error; %d, %d' % (gridX, gridY)
        move_to_index(targetIndex, Smooth)
    time.sleep(1.0/16)

def adjacent(targetIndex):
    ''' Returns the cells around a target index.'''
    # Unexpected results while targetIndex is on the edge are prevented
    # by shifting the targetIndex away from the edge and fixing the
    # results afterwards.
    if targetIndex % WIDTH == 0:
        adjacentLst = adjacent(targetIndex + 1)
        for Idx, Val in enumerate(adjacentLst):
            if Idx in [2, 5]: adjacentLst[Idx] = (-1, 0)
            else: adjacentLst[Idx] = Val
        adjacentLst[:] = [(-1, 0)] + adjacentLst[:-1]
    elif targetIndex % WIDTH == WIDTH - 1:
        adjacentLst = adjacent(targetIndex - 1)
        for Idx, Val in enumerate(adjacentLst):
            if Idx in [3, 6]: adjacentLst[Idx] = (-1, 0)
            else: adjacentLst[Idx] = Val
        adjacentLst[:] = adjacentLst[1:] + [(-1, 0)]
    elif targetIndex / WIDTH == 0:
        adjacentLst = adjacent(targetIndex + WIDTH)
        adjacentLst = [(-1, 0)]*3 + adjacentLst[:-3]
    elif targetIndex / WIDTH == WIDTH / FIELD_SIZE:
        adjacentLst = adjacent(targetIndex - WIDTH)
        adjacentLst = adjacentLst[3:] + [(-1, 0)] * 3
    else:
        adjacentLst = []
        Start = targetIndex - WIDTH - 1
        End = targetIndex + WIDTH
        for Idx in xrange(Start, End, WIDTH):
            adjacentLst.extend(MINEFIELD[Idx:Idx + 3])
    
    return adjacentLst

def flag(Lst):
    for targetIndex, Val in Lst:
        print 'Flag: %d' % targetIndex,
        MINEFIELD[targetIndex] = (targetIndex, 'M')
        move_to_index(targetIndex)
        # time.sleep(0.001)
        autopy.mouse.click(autopy.mouse.RIGHT_BUTTON)
        HIDDEN.remove(targetIndex)

def reveal(targetIndex):
    print 'Reveal: %d' % targetIndex,
    move_to_index(targetIndex)
    both_click()

def direct_logic():
    ''' Applies no-brain logic to '''
    for targetIndex in FOCUS.copy():
        cellValue = MINEFIELD[targetIndex][1]
        adjacentLst = adjacent(targetIndex)
        minesLst = [(Idx, Val) for Idx, Val in adjacentLst if Val == 'M']
        hiddenLst = [(Idx, Val) for Idx, Val in adjacentLst if Val == 9]
        Mines, Hidden = len(minesLst), len(hiddenLst)
        if not Hidden: # If none are hidden around it forget about it.
            FOCUS.remove(targetIndex)
        elif cellValue - Mines == Hidden: # If hidden are obvious mines
            flag(hiddenLst)
        elif cellValue == Mines: # If cell is completely safe.
            reveal(targetIndex)
        # elif cellValue == 'M':
            # move_to_index(targetIndex)
            # autopy.mouse.click(autopy.mouse.RIGHT_BUTTON)

def explore():
    ''' Randomly picks a cell still HIDDEN and checks for a mine.'''
    targetIndex = random.sample(HIDDEN, 1)[0]
    move_to_index(targetIndex)
    autopy.mouse.click()
    screenShot = grab_screen_area()
    gridX, gridY = convert_to_screen(targetIndex)
    Color = autopy.color.hex_to_rgb(screenShot.get_color(gridX, gridY + 6))
    if Color == (0, 0, 0):
        print '\nHit a mine, while exploring. Guess my luck ran out.\n'
        HIDDEN.clear()

def text_color(Text, colorCode):
    ctypes.windll.kernel32.SetConsoleTextAttribute(OUT_HANDLE, colorCode)
    print Text,
    ctypes.windll.kernel32.SetConsoleTextAttribute(OUT_HANDLE, 0x000A)

def thought_viewer():
    print ''
    for Idx, Val in MINEFIELD:
        if not Idx % WIDTH:
            print ''
        
        if Idx in FOCUS:
            text_color(Val, 0x000E)
        elif Idx in HIDDEN:
            text_color(Val, 0x0008)
        elif Val == 'M':
            text_color(Val, 0x0047)
        else:
            print Val,
    
    print ''

def main():
    while HIDDEN:
        thought_viewer() # To see what it sees. Diagnostic uses.
        Previous = MINEFIELD[:]
        mark_exposed() # Reads the screen and marks it in memory.
        direct_logic() # The no-brain logic to solve lots.
        Same = MINEFIELD == Previous
        
        # if not Same:
            # continue
        # else:
            # print 'Advance Logic'
            # Same = MINEFIELD == Previous
        
        if Same: # If advanced logic does not change.
            explore()

def debug(targetIndex):
    print ''
    cellValue = MINEFIELD[targetIndex][1]
    adjacentLst = adjacent(targetIndex)
    Mines = len([(Idx, Val) for Idx, Val in adjacentLst if Val == 'M'])
    Hidden = len([(Idx, Val) for Idx, Val in adjacentLst if Val == 9])
    print adjacentLst
    print 'Flag: cellValue %d - Mines %d == Hidden %d' % (cellValue, Mines, Hidden)
    print 'Reveal: cellValue %d == Mines %d' % (cellValue, Mines)
    thought_viewer()
    print ''
    print 'HIDDEN\n', HIDDEN
    print '\nFOCUS\n', FOCUS

def new():
    # screenShot = grab_screen_area()
    # screenShot.save(r'E:\Desktop\MsweepV1\%d.png' % int(time.time()))
    move_to_index(-(WIDTH/2) - WIDTH)
    autopy.mouse.click()
    FOCUS.clear()

if __name__ == '__main__':
    __init__()
    main()
    # for i in xrange(50):
        # __init__()
        # main()
        # new()
        # time.sleep(1)