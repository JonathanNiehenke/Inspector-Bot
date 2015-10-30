'''
Minesweeper AI

Concepts
> Game environment.
  + Board Size. (Beginner: 9x9M10, Intermediate: 16x16M40, Expert: 16x30M99)
  + Movement Type.
  + Win and loss conditions.
> Adjacent
> Leading Edge
> Overlapping
> Deductive and reasoning.
> Exploration.
'''
# Created 10/29/14
# By Jonathan Niehenke

# Style Sheet
# Variable = r'\b[A-Z]\w+?\b|\b\w+?(?:[A-Z]\w+?)+\b'
# Global variable = r'\b[A-Z_]'
# Function = r'\b([a-z]+_?)+\b'

#Ideas:
'''
Maintain a list of focused array indexes and a list of ignored indexes.
Recursive is possible:
  Reveal baseline = if cellValue equals minesAround than reveal all uncovered.
  Mark baseline = if cellVulue subtracted by minesAround than mark all uncovered.
'''

import win32gui
import autopy
import time

FRONTLINE = set()
# BACKLINE = set()
# Array Conversion from Index to coordinate pairs.
# y, x = divmod(Index - 1, WIDTH)

def __init__():
    global MINEFIELD_POS, WIDTH, FIELD_SIZE, MINEFIELD, HIDDEN
    WinPos = find_window('Minesweeper') # Finds Minesweeper window.
    MINEFIELD_POS, gridSize = find_grid(WinPos) # Shrinks to grid.
    WIDTH, Height = gridSize
    FIELD_SIZE = WIDTH * Height
    MINEFIELD = list(enumerate([9] * FIELD_SIZE))
    HIDDEN = set(range(FIELD_SIZE))

def find_window(Name):
    WinHandle = win32gui.FindWindow(None, Name)
    win32gui.SetForegroundWindow(WinHandle)
    WinPos = win32gui.GetWindowRect(WinHandle)
    return (WinPos)

def find_grid(WinPos):
    Left, Top, Right, Bot = WinPos
    Left, Top, Right, Bot = (Left + 15, Top + 101, Right - 11, Bot - 11)
    gridPos = (Left, Top, Right, Bot)
    gridSize = ((Right - Left) / 16, (Bot - Top) / 16)
    return gridPos, gridSize

def grab_screen_area():
    #!! capture_screen((MINEFIELD_POS[2:], MINEFIELD_POS[2:])) results
    #!! in off-screen capture (black picture) or out of bounds error.
    screenArea = ((0,0), (MINEFIELD_POS[2:])) # (0, 0) prevents error.
    screenShot = autopy.bitmap.capture_screen(screenArea)
    return screenShot

def convert_to_screen(targetIndex):
    gridY, gridX = divmod(targetIndex, WIDTH)
    gridX = MINEFIELD_POS[0] + (gridX * 16) + 9 # +9 to hit center.
    gridY = MINEFIELD_POS[1] + (gridY * 16) + 8 # +8 to hit center.
    return (gridX, gridY)
    

def screen_to_grid(targetIndex, screenShot):
    gridX, gridY = convert_to_screen(targetIndex)
    Color = autopy.color.hex_to_rgb(screenShot.get_color(gridX, gridY))
    
    if Color == (0, 0, 255):
        MINEFIELD[targetIndex] = (targetIndex, 1)
        HIDDEN.discard(targetIndex)
        FRONTLINE.add(targetIndex)
    elif Color == (0, 128, 0):
        MINEFIELD[targetIndex] = (targetIndex, 2)
        HIDDEN.discard(targetIndex)
        FRONTLINE.add(targetIndex)
    elif Color == (255, 0, 0):
        MINEFIELD[targetIndex] = (targetIndex, 3)
        HIDDEN.discard(targetIndex)
        FRONTLINE.add(targetIndex)
    elif Color == (0, 0, 128):
        MINEFIELD[targetIndex] = (targetIndex, 4)
        HIDDEN.discard(targetIndex)
        FRONTLINE.add(targetIndex)
    elif Color == (128, 0, 0):
        MINEFIELD[targetIndex] = (targetIndex, 5)
        HIDDEN.discard(targetIndex)
        FRONTLINE.add(targetIndex)
    elif Color == (0, 128, 128):
        MINEFIELD[targetIndex] = (targetIndex, 6)
        HIDDEN.discard(targetIndex)
        FRONTLINE.add(targetIndex)
    elif Color == (0, 0, 0):
        MINEFIELD[targetIndex] = (targetIndex, 7)
        HIDDEN.discard(targetIndex)
        FRONTLINE.add(targetIndex)
    elif Color == (128, 128, 128):
        MINEFIELD[targetIndex] = (targetIndex, 8)
        HIDDEN.discard(targetIndex)
        FRONTLINE.add(targetIndex)
    else:
        Color = screenShot.get_color(gridX, gridY - 7)
        if autopy.color.hex_to_rgb(Color) == (192, 192, 192):
            MINEFIELD[targetIndex] = (targetIndex, 0)
            HIDDEN.discard(targetIndex)
        

def mark_exposed():
    screenShot = grab_screen_area()
    for Idx in HIDDEN.copy():
        screen_to_grid(Idx, screenShot)

def both_click():
    autopy.mouse.toggle(True)
    autopy.mouse.click(autopy.mouse.RIGHT_BUTTON)
    autopy.mouse.toggle(False)

def move_to_index(targetIndex, Smooth=False):
    gridX, gridY = convert_to_screen(targetIndex)
    try:
        if Smooth:
            autopy.mouse.smooth_move(gridX + 12, gridY)
        else:
            autopy.mouse.move(gridX + 12, gridY)
    except ValueError:
        print targetIndex, (gridX, gridY)
        exit()
    

def adjacent(targetIndex):
    '''
    Returns the cells around a target index. Arguments are the array,
    width of the grid the array represents, and the target index. 
    '''
    # Unexpected results while targetIndex is on the edge are prevented
    # by shifting the targetIndex away from the edge and fixing the
    # results afterwards.
    if targetIndex % WIDTH == 0: # If on left edge.
        adjacentLst = adjacent(targetIndex + 1)
        adjacent_fix(adjacentLst, 0, 3, 6)
    elif targetIndex % WIDTH == WIDTH - 1: # If on right edge.
        adjacentLst = adjacent(targetIndex - 1)
        adjacent_fix(adjacentLst, 2, 5, 8)
    elif targetIndex / WIDTH == 0: # If on top edge.
        adjacentLst = adjacent(targetIndex + WIDTH)
        adjacent_fix(adjacentLst, 0, 1, 2)
    elif targetIndex / WIDTH == 8: # If on bottom edge.
        adjacentLst = adjacent(targetIndex - WIDTH)
        adjacent_fix(adjacentLst, 6, 7, 8)
    else:
        Start, End = targetIndex - WIDTH - 1, targetIndex + WIDTH
        adjacentLst = []
        for Index in xrange(Start, End, WIDTH):
            adjacentLst.extend(MINEFIELD[Index: Index + 3])
    
    return adjacentLst

def adjacent_fix(Lst, *Indexes):
    for Idx, Val in enumerate(Lst):
            Lst[Idx] = (-1, 0) if Idx in Indexes else Val

def flag(Lst):
    for targetIndex in Lst:
        print 'flag: %d' % targetIndex,
        move_to_index(targetIndex)
        autopy.mouse.click(autopy.mouse.RIGHT_BUTTON)
        MINEFIELD[targetIndex] = (targetIndex, 'M')
        HIDDEN.remove(targetIndex)

def free_flag(Set):
    for targetIndex in Set.copy():
        cellValue = MINEFIELD[targetIndex][1]
        adjacentLst = adjacent(targetIndex)
        simpleLst = [Val for Idx, Val in adjacentLst if Val in ['M', 9]]
        Mines, Covered = simpleLst.count('M'), simpleLst.count(9)
        if cellValue - Mines == Covered:
            flagLst = [Idx for Idx, Val in adjacentLst if Val == 9]
            flag(flagLst)

def free_reveal(Set):
    for targetIndex in Set.copy():
        cellValue = MINEFIELD[targetIndex][1]
        adjacentLst = adjacent(targetIndex)
        simpleLst = [Val for Idx, Val in adjacentLst if Val in ['M', 9]]
        Mines, Covered = simpleLst.count('M'), simpleLst.count(9)
        if cellValue == Mines:
            print 'Reveal: %d' % targetIndex,
            move_to_index(targetIndex)
            both_click()
            Set.remove(targetIndex)

def thought_viewer():
    Thoughts = MINEFIELD[:]
    while Thoughts:
        for i in xrange(WIDTH):
            print Thoughts.pop(0)[1],
        print ''
    print ''

def main():
    move_to_index(WIDTH * 3 + 3)
    autopy.mouse.click()
    Previous = None
    while MINEFIELD != Previous:
        Previous = MINEFIELD[:]
        mark_exposed()
        thought_viewer()
        free_flag(FRONTLINE)
        print ''
        free_reveal(FRONTLINE)
        print ''
            
def new():
    screenShot = grab_screen_area()
    screenShot.save(r'E:\Desktop\MsweepV1\%d.png' % int(time.time()))
    move_to_index(-(WIDTH/2) - WIDTH)
    autopy.mouse.click()

if __name__ == '__main__':
    __init__()
    main()
    print HIDDEN, FRONTLINE
    # for i in xrange(50):
        # __init__()
        # try:
            # main()
        # finally:
            # new()
        # time.sleep(1)