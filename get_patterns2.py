from __future__ import print_function
from copy import deepcopy
import sys

import numpy
sys.path.append('.\\')
from BejeweledAI_v3b import (collect_basic_row_patterns, 
    improve_pattern_collection, collect_star_patterns, transpose_index_pairs)

ROW_BOARD = numpy.array([
        [1, 2, 2, 1, 2, 1, 2], # Pair and Split detection and handling.
        [3, 4, 3, 4, 3, 3, 4], # Pair and Split detection and handling.
        [5, 6, 6, 5, 6, 6, 5], # Pair and Split detection and handling.
        [7, 7, 8, 8, 8, 7, 7], # Pair and Combo detection and handling.
        [9, 9, 9, 1, 9, 9, 9], # Combo detection and handling.
        [2, 3, 2, 2, 2, 3, 2], # Combo detection and handling.
        [4, 5, 5, 5, 5, 5, 4]  # Combo detection and handling.
    ])

STAR_BOARD = numpy.array([ # Test star patterns detection and handling.
    list('GBBRB'),list('RGGBO'), list('GPWBO'), list('GPOOR'), list('PRPPO')
    ])

ROW_BASIC = [
    ([(0, 1), (0, 2)], (0, 0, 2)),
    ([(0, 1), (0, 2)], (0, 3, 2)),
    ([(0, 2), (0, 4)], (0, 3, 2)),
    ([(0, 3), (0, 5)], (0, 4, 1)),
    ([(0, 4), (0, 6)], (0, 5, 2)),
    ([(1, 0), (1, 2)], (1, 1, 3)),
    ([(1, 1), (1, 3)], (1, 2, 4)),
    ([(1, 2), (1, 4)], (1, 3, 3)),
    ([(1, 4), (1, 5)], (1, 3, 3)),
    ([(1, 4), (1, 5)], (1, 6, 3)),
    ([(2, 1), (2, 2)], (2, 0, 6)),
    ([(2, 1), (2, 2)], (2, 3, 6)),
    ([(2, 2), (2, 4)], (2, 3, 6)),
    ([(2, 4), (2, 5)], (2, 3, 6)),
    ([(2, 4), (2, 5)], (2, 6, 6)),
    ([(3, 0), (3, 1)], (3, 2, 7)),
    ([(3, 2), (3, 3)], (3, 1, 8)),
    ([(3, 2), (3, 3), (3, 4)], None),
    ([(3, 3), (3, 4)], (3, 5, 8)),
    ([(3, 5), (3, 6)], (3, 4, 7)),
    ([(4, 0), (4, 1), (4, 2)], None),
    ([(4, 1), (4, 2)], (4, 3, 9)),
    ([(4, 2), (4, 4)], (4, 3, 9)),
    ([(4, 4), (4, 5)], (4, 3, 9)),
    ([(4, 4), (4, 5), (4, 6)], None),
    ([(5, 0), (5, 2)], (5, 1, 2)),
    ([(5, 2), (5, 3)], (5, 1, 2)),
    ([(5, 2), (5, 3), (5, 4)], None),
    ([(5, 3), (5, 4)], (5, 5, 2)),
    ([(5, 4), (5, 6)], (5, 5, 2)),
    ([(6, 1), (6, 2)], (6, 0, 5)),
    ([(6, 1), (6, 2), (6, 3)], None),
    ([(6, 2), (6, 3), (6, 4)], None),
    ([(6, 3), (6, 4), (6, 5)], None),
    ([(6, 4), (6, 5)], (6, 6, 5)),
    ]

ROW_IMPROVED = [
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

STAR_ANSWER = [
    ([(0, 1), (0, 2), (1, 3), (2, 3)], (0, 3, 'B')),
    ([(0, 2), (0, 4), (1, 3), (2, 3)], (0, 3, 'B')),
    ([(0, 0), (1, 1), (1, 2), (2, 0)], (1, 0, 'G')),
    ([(1, 1), (1, 2), (2, 0), (3, 0)], (1, 0, 'G')),
    ([(1, 4), (2, 4), (3, 2), (3, 3)], (3, 4, 'O')),
    ([(2, 4), (3, 2), (3, 3), (4, 4)], (3, 4, 'O')),
    ([(2, 1), (3, 1), (4, 0), (4, 2)], (4, 1, 'P')),
    ([(2, 1), (3, 1), (4, 2), (4, 3)], (4, 1, 'P')),
    ]

def tester(Given, Answer):
    if Given == Answer:
        Pass = True
        print('CORRECT!!!')
    else:
        Pass = False
        GivenMessage = '{}IN EXPECTED ANSWER: \t{}\t{}'
        MissedMessage = 'MISSED: \t{}\t{}'
        for Pattern in Given:
            Inject = '' if Pattern in Answer else 'NOT '
            print(GivenMessage.format(Inject, *Pattern))
            
        [print(MissedMessage.format(*Pattern))
            for Pattern in Answer if Pattern not in Given]
    
    return Pass

print('<-- TEST 1, BASIC ROW PATTERNS -->')
print(ROW_BOARD)
basicRowPatterns = collect_basic_row_patterns(ROW_BOARD)
Pass = tester(basicRowPatterns, ROW_BASIC)
raw_input('...')

if Pass:
    print('<-- TEST 2, IMPROVED ROW PATTERNS -->')
    improvedRowPatterns = improve_pattern_collection(
        deepcopy(basicRowPatterns))
    Pass = tester(improvedRowPatterns, ROW_IMPROVED)
    raw_input('...')
else:
    exit(0)

if Pass:
    print(STAR_BOARD)
    print('<-- TEST 3, STAR PATTERNS -->')
    basicRowPatterns = collect_basic_row_patterns(STAR_BOARD)
    basicColumnPatterns = transpose_index_pairs(
        collect_basic_row_patterns(STAR_BOARD.T))
    starPatterns = collect_star_patterns(basicRowPatterns, basicColumnPatterns)
    tester(starPatterns, STAR_ANSWER)