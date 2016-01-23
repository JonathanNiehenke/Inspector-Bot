from collections import OrderedDict
from itertools import chain
from random import choice

import win_terface

def print_patterns(Field, Formations):
    print('Patterns')
    byPatternLen = OrderedDict(((5, set()), (4, set()), (3, set()), (2, set())))
    for Pattern, _ in chain(*Formations):
        byPatternLen[len(Pattern)].update(Pattern)
    colorArgs = byPatternLen.values()
    win_terface.print_colorized_board(Field.rows, *colorArgs)
    print()
    

def print_moves(Field, Moves):
    print('Moves')
    Pattern, From, To = zip(*Moves)
    win_terface.print_colorized_board(
        Field.rows, From, To, [], set(chain(*Pattern)))
    print()
    

def improved_field():
    Field = (
        'OPSOPSOP',
        'YYBBBYYB', # Combo and Pair detection and handling.
        'GGGRRGGG', # Combo and Pair detection and handling.
        'POPOOOPO', # Combo and Split detection and handling.
        'SYYYYYSY', # Combo and Split detection and handling.
        'BGGBGBGB', # Pair and Split detection and handling.
        'ORORORRO', # Pair and Split detection and handling.
        'PSSPSSPP', # Pair and Split detection and handling.
        )
    return Field


def star_field():
    Field = (
        'WBBWWGGW',
        'BAOOPPDG',
        'BOWYYWPG',
        'WOYWWBPW',
        'WRYWWBSW',
        'GRWBBWSO',
        'GWRRSSWO',
        'WGGWWOOW',
        )
    return Field


def star_combo_field():
    Field = (
        'WBBWWGGW',
        'BWOOPPWG',
        'BOWYYWPG',
        'WOYWWBPW',
        'WRYWWBSW',
        'GRWBBWSO',
        'GRRRSSWO',
        'WGGWWOOW',
        )
    return Field

def move_field():
    Field = (
        'ACDEFABC',
        'ACDEFABC',
        'BORACDEO',
        'BORACDEO',
        'PRZBZZFS',
        'OSYGYYFS',
        'GPSACDEP',
        'GPSACDEP',
        )
    return Field

def random_field():
    Field = (tuple((choice('BGROPSY') for _ in range(8)) for _ in range(8)))
    return Field
