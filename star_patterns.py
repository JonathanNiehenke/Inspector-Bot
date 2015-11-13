from __future__ import print_function
from copy import deepcopy
import numpy


Board = numpy.array([ # Test star patterns detection and handling.
    list('GBBRB'),list('RGGBO'), list('GPWBO'), list('GPOOR'), list('PRPPO')
    ])

ANSWER = [
    ([(0, 1), (0, 2)],              (0, 0, 2)), # Left pair and link,
    ([(0, 1), (0, 2), (0, 4)],      (0, 3, 2)), # joined into fire.
    ([(0, 3), (0, 5)],              (0, 4, 1)), # mid-right split.
    ([(0, 4), (0, 6)],              (0, 5, 2)), # Right split.
    
    ([(1, 0), (1, 2)],              (1, 1, 3)), # Left split.
    ([(1, 1), (1, 3)],              (1, 2, 4)), # Left-mid split,
    ([(1, 2), (1, 4), (1, 5)],      (1, 3, 3)), # mid fire.
    ([(1, 4), (1, 5)],              (1, 6, 3)), # Right pair and link.
    
    ([(2, 1), (2, 2)],              (2, 0, 6)), # Left pair and link.
    ([(2, 1), (2, 2), (2, 4), (2, 5)],      (2, 3, 6)), # Mid hyper.
    ([(2, 4), (2, 5)],              (2, 6, 6)), # Right pair and link.
    
    ([(3, 0), (3, 1)],              (3, 2, 7)), # Left pair right link.
    ([(3, 2), (3, 3), (3, 4)],      None),      # Mid combo.
    ([(3, 5), (3, 6)],              (3, 4, 7)), # Right pair left link.
    
    ([(4, 0), (4, 1), (4, 2)],      None),      # Left combo.
    ([(4, 4), (4, 5), (4, 6)],      None),      # Right combo.
    
    ([(5, 2), (5, 3), (5, 4)],      None),      # Mid combo
    
    ([(6, 1), (6, 2), (6, 3), (6, 4), (6, 5)], None) # Mid hyper combo.
    ]

def collect_basic_row_patterns(Board):
    '''Returns the basic patterns along the rows of a board.'''
    basicPatterns = []
    for I, Row in enumerate(Board):
        rowEnum = enumerate(Row)
        _, A = rowEnum.next()
        _, B = rowEnum.next()
        for J, C in rowEnum:
            
            try:
                Pattern, Link = identify_pattern(A, B, C, I, J)
            except TypeError: # base_patterns returned None.
                pass # Explicitly silenced!!!
            else:
                basicPatterns.append((Pattern, Link))
            finally:
                A, B = B, C
    
    return basicPatterns

def identify_pattern(A, B, C, I, J):
    '''Returns I, J index of found patterns and links.'''
    
    Rpair = B == C # Pair right of the Link.
    Lpair = A == B # Left of the Link.
    
    if not (A and B and C):
        Pattern = None # Ignore unknowns. Nothing to see here! :)
    elif Lpair and Rpair:
        Pattern = ([(I, J - 2), (I, J - 1), (I, J)], None) # A combo.
    elif Rpair:
        Pattern = ([(I, J - 1), (I, J)], (I, J - 2, B))
    elif Lpair:
        Pattern = ([(I, J - 2), (I, J - 1)], (I, J, A))
    elif A == C:
        Pattern = ([(I, J - 2), (I, J)], (I, J - 1, A)) # Split.
    else:
        Pattern = None # Nothing was found.
    
    return Pattern

def improve_pattern_collection(basicPatternLst):
    '''Creates a list of improved patterns with larger formations.'''
    improvedPatternLst = []
    for Formation, Link in basicPatternLst:
        
        try:
            previousFormation, previousLink = improvedPatternLst[-1]
        except IndexError: # improvedPatternLst is empty.
            previousFormation = [(-1, -1), (-1, -1)]
            previousLink = (-1, -1, -1)
        
        Overlaps = Formation[0] in previousFormation
        currentCombo, previousCombo = Link is None, previousLink is None
        
        if Link == previousLink:
            previousFormation.append(Formation[-1])
        elif currentCombo and Overlaps: # the previousFormation.
            # Replace the incomplete pattern with the combo.
            improvedPatternLst[-1] = (Formation, Link)
        elif not (previousCombo and Overlaps): # the Formation.
            # Formation is included in the improved list.
            improvedPatternLst.append((Formation, Link))
    
    return improvedPatternLst

basicRowPatterns = collect_basic_row_patterns(BOARD)
Found = improve_pattern_collection(basicRowPatterns)


print(BOARD)
if Found == ANSWER:
    print('CORRECT!!!')
else:
    [print('{} MASTER: \t{}\t{}'.format(
        'IN' if Info in ANSWER else 'NOT IN', *Info)) for Info in Found]
    [print('MISSED: \t{}\t{}'.format(*Info)) for Info in ANSWER
            if Info not in Found]
[print(Val) for Val in basicRowPatterns]
