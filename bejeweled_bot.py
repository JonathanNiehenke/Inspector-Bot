'''
Bot that plays Bejeweled by reading the screen, moving the mouse and
making decisions usually favoring special gem creation.
'''
# Began 11/13/15
# By Jonathan Niehenke

# Naming Styles -- Why? For variable and function distinction.
#   Variables = mixedCamelCase, Global variable = ALL_CAPS,
#   Function/Methods/Modules = lowercase_with_underscores,
#   Class = CamelCase

# Definition Order -- Why? Improve reading navigation.
#   In order of use (hierarchical top to bottom). Unless shared by a
#   continuous defined group of functions or defined elsewhere which
#   would note a  #def@ comment.

from collections import OrderedDict
from itertools import chain, product
from random import choice


class BejeweledField(OrderedDict):
    width_by_gem, height_by_gem = 8, 8

    def __init__(self, *args, **kwargs):
        OrderedDict.__init__(self, *args, **kwargs)

    def collapse_pattern(self, Pattern):
        for X, Y in Pattern:
            self.collapse_gems(X, Y)

    def collapse_gems(self, X, Y):
        Indexes, Gems = zip(*
            [(Index, self[Index]) for Index in self.collect_above(X, Y)])
        print('Drop: {}'.format(Gems[0]))
        Gems = Gems[1:] + (' ',)
        for Index, Gem in zip(Indexes, Gems):
            self[Index] = Gem

    def collect_above(self, X, Y):
        while Y >= 0:
            yield (X, Y)
            Y -= 1

    @property
    def rows(self):
        return zip(*[iter(self.values())] * self.width_by_gem)

    @property
    def columns(self):
        return zip(*self.rows)

    def __str__(self):
        return '\n'.join(' '.join(Row) for Row in self.rows)


class BejeweledInterface(BejeweledField):
    def __init__(self, *args, **kwargs):
        OrderedDict.__init__(self, *args, **kwargs)
        window = win_terface(Bejeweled2, bringTop=True)

    def read_field(self):
        pass

    def swap_gems(self, fromIndex, toIndex):
        Drag = (fromIndex, ('Left', 'Press'), toIndex, ('Left', 'Release'))
        win_terface.execute_mouse(*Drag)

    def convert_to_screen(self, X, Y):
        pass


def collect_formations(Board):
    rowFormations, foundRowCombo = collect_row_formations(Board, Empty=1)
    colFormations, foundColCombo = collect_column_formations(Board, Empty=1)
    if foundRowCombo or foundColCombo:
        print('Caught combo')
        improvedCombos = collect_combos(rowFormations, colFormations)
        comboPatterns = [Patterns for Patterns, _ in chain(*improvedCombos)]
        print(comboPatterns)
        Board.collapse_pattern(chain(*comboPatterns))
        improvedRowFormations, improvedColFormations, starFormations = (
            collect_formations(Board))
    else:
        print('Missed combo')
        improvedRowFormations = improve_collections(rowFormations)
        improvedColFormations = improve_collections(colFormations)
        starFormations = collect_star_formations(rowFormations, colFormations)
    return improvedRowFormations, improvedColFormations, starFormations

def collect_row_formations(Board, Empty):
    Formations, foundCombo = [], False
    for gemA, gemB, gemC, X, Y in gather_gem_trio(Board.rows, Empty):
        leftsidePair, rightsidePair = gemA == gemB, gemB == gemC
        if leftsidePair and rightsidePair:
            Formations.append(([(X - 2, Y), (X - 1, Y), (X, Y)], None))
            foundCombo = True
        elif leftsidePair :
            Formations.append(([(X - 2, Y), (X - 1, Y)], (X, Y, gemA)))
        elif rightsidePair:
            Formations.append(([(X - 1, Y), (X, Y)], (X - 2, Y, gemB)))
        elif gemA == gemC:
            Formations.append(([(X - 2, Y), (X, Y)], (X - 1, Y, gemA)))
    return Formations, foundCombo


def collect_column_formations(Board, Empty):
    Formations, foundCombo = [], False
    for gemA, gemB, gemC, X, Y in gather_gem_trio(Board.columns, Empty):
        leftsidePair, rightsidePair = gemA == gemB, gemB == gemC
        if leftsidePair and rightsidePair:
            Formations.append(([(Y, X - 2), (Y, X - 1), (Y, X)], None))
            foundCombo = True
        elif leftsidePair :
            Formations.append(([(Y, X - 2), (Y, X - 1)], (Y, X, gemA)))
        elif rightsidePair:
            Formations.append(([(Y, X - 1), (Y, X)], (Y, X - 2, gemB)))
        elif gemA == gemC:
            Formations.append(([(Y, X - 2), (Y, X)], (Y, X - 1, gemA)))
    return Formations, foundCombo


def gather_gem_trio(boardVector, Empty=1):
    for Y, Vector in enumerate(boardVector):
        rowEnumerator = enumerate(Vector)
        (_, gemA), (_, gemB) = next(rowEnumerator), next(rowEnumerator)
        for X, gemC in rowEnumerator:
            if (gemA, gemB, gemC).count(' ') <= Empty:
                yield gemA, gemB, gemC, X, Y
            gemA, gemB = gemB, gemC


def collect_combos(rowFormations, colFormations):
    rowCombos = [(P, Link) for P, Link in rowFormations if Link is None]
    colCombos = [(P, Link) for P, Link in colFormations if Link is None]
    improvedRowCombos = improve_collections(rowCombos)
    improvedColCombos = improve_collections(colCombos)
    # if rowCombos and colCombos:
        # starCombos = collect_star_combos(rowCombos, colCombos)
    # else:
        # starCombos = []
    return improvedRowCombos, improvedColCombos


def improve_collections(basicFormations):
    bogusValues = ([(-1, -1), (-1, -1)], (-1, -1, -1))
    improvedFormations = [bogusValues]
    for Pattern, Link in basicFormations:
        previousPattern, previousLink = improvedFormations[-1]
        patternsOverlap = previousPattern[-1] in Pattern
        if Link == previousLink and patternsOverlap:
            previousPattern.append(Pattern[-1])
        else:
            # Copies to prevent modification to the basicFormations.
            improvedFormations.append((list(Pattern), Link))
    return improvedFormations[1:]


def collect_star_combos(rowCombos, colCombos):
    Intersections = collect_intersections(rowCombos, colCombos, Combo=True)
    if Intersections:
        crossingRowCombos = assemble_crossing_combos(rowCombos, Intersections)
        crossingColCombos = assemble_crossing_combos(colCombos, Intersections)
        starCombos = join_crossing_formations(
            crossingRowCombos, crossingColCombos)
    else:
        starCombos = []
    return starCombos


def collect_star_formations(rowFormations, colFormations):
    Intersections = collect_intersections(rowFormations, colFormations)
    if Intersections:
        crossingRowFormations = assemble_crossing_formations(
            rowFormations, Intersections)
        crossingColFormations = assemble_crossing_formations(
            colFormations, Intersections)
        starFormations = join_crossing_formations(
            crossingRowFormations, crossingColFormations)
    else:
        starFormations = []
    return starFormations


def collect_intersections(rowFormations, colFormations, Combo=False):
    twoVectors = rowFormations and colFormations
    if twoVectors and Combo:
        rowPatterns, _ = zip(*rowFormations)
        columnPatterns, _ = zip(*colFormations)
        Intersections = set(chain(*rowPatterns)) & set(chain(*columnPatterns))
    elif twoVectors:
        _, rowLinks = zip(*rowFormations)
        _, columnLinks = zip(*colFormations)
        Intersections = set(rowLinks) & set(columnLinks)
    else:
        Intersections = set()
    return Intersections


def assemble_crossing_combos(Combos, Intersections):
    crossingCombos = []
    for Pattern, _ in Combos:
        for Link in set(Pattern) & Intersections:
            crossingCombos.append(Pattern, Link)
    return crossingCombos


def assemble_crossing_formations(Formations, Intersections):
    crossingFormations = ((Pattern, Link) for Pattern, Link in Formations
                          if Link in Intersections)
    return crossingFormations


def join_crossing_formations(crossingRowFormations, crossingColFormations):
    organizedRowFormations = organize_formation(crossingRowFormations)
    organizedColFormations = organize_formation(crossingColFormations)
    crossingFormations = join_organized_formations(
        organizedRowFormations, organizedColFormations)
    return crossingFormations


def organize_formation(Formation):
    Order = {}
    for Pattern, Link in Formation:
        Order.setdefault(Link, []).append(Pattern)
    return Order


def join_organized_formations(organizedRowFormations, organizedColFormations):
    crossingFormations = []
    for Link in organizedRowFormations:
        patternPairs = product(
            organizedRowFormations[Link], organizedColFormations[Link])
        for rowPattern, colPattern in patternPairs:
            crossingFormations.append((rowPattern + colPattern, Link))
    return crossingFormations


def improved_field():
    Field = (
        'BGGBGBGB', # Pair and Split detection and handling.
        'ORORORRO', # Pair and Split detection and handling.
        'PSSPSSPP', # Pair and Split detection and handling.
        'YYBBBYYB', # Pair and Combo detection and handling.
        'GGGRRGGG', # Combo and Pair detection and handling.
        'POPOOOPO', # Combo and Split detection and handling.
        'SYYYYYSY'  # Combo and Split detection and handling.
        )
    bjwdField = BejeweledField(
        (((X, Y), V) for Y, Row in enumerate(Field) for X, V in enumerate(Row)))
    return bjwdField


def star_field():
    Field = (
        'WBBWWGGW',
        'BWOOPPWG',
        'YYWYYWPG',
        'WOYWWBPW',
        'WRYWWBSW',
        'GRWBBWSO',
        'GWRRSSWO',
        'WGGWWOOW')
    bjwdField = BejeweledField(
        (((X, Y), V) for Y, Row in enumerate(Field) for X, V in enumerate(Row)))
    return bjwdField


def random_field():
    Field = (tuple((choice('BGROPSY') for _ in range(8)) for _ in range(8)))
    bjwdField = BejeweledField(
        (((X, Y), V) for Y, Row in enumerate(Field) for X, V in enumerate(Row)))
    return bjwdField


def main():
    Test = random_field()
    improvedRowFormations, improvedColFormations, starFormations = collect_formations(Test)
    print(Test, end='\n\n')
    for Formation in chain(improvedRowFormations, improvedColFormations):
        print(Formation)
    print()
    for Formation in starFormations:
        print(Formation)

if __name__ == '__main__':
    main()
