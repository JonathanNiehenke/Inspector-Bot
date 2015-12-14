"""
Bot that plays Bejeweled by reading the screen, moving the mouse and
making decisions usually favoring special gem creation.
"""
# Began 11/13/15
# By Jonathan Niehenke

# Definition Order -- Why? Improve reading navigation.
#   In order of use (hierarchical top to bottom). Unless shared by a
#   continuous defined group of functions or defined elsewhere which
#   would note a  #def@ comment.

from collections import namedtuple, OrderedDict
from itertools import chain, product
from random import choice

import win_terface

db=print


class BejeweledField(OrderedDict):
    width_by_gem, height_by_gem = 8, 8

    def __init__(self, *args, **kwargs):
        OrderedDict.__init__(self, *args, **kwargs)

    def collapse_pattern(self, Pattern):
        for X, Y in Pattern:
            self.collapse_gems(X, Y)

    def collapse_gems(self, X, Y):
        gather_above = ((X, Y) for Y in range(Y, -1, -1))
        Indexes, Gems = zip(*[(Index, self[Index]) for Index in gather_above])
        Gems = Gems[1:] + (' ',)
        for Index, Gem in zip(Indexes, Gems):
            self[Index] = Gem

    def collect_moves(self, Formations):
        """Returns list of moves that join Formations."""
        fieldDims = self.width_by_gem, self.height_by_gem
        foundMoves = []
        for Formation in Formations:
            foundMoves.extend(self.collect_connections(*Formation, *fieldDims))
        return sorted(foundMoves)

    def collect_connections(self, Pattern, Link, Width, Height):
        X, Y, Color = Link
        whereToLook = ((Y - 1, X), (Y, X - 1), (Y, X + 1), (Y + 1, X))
        fieldEdge = [(-1, X), (Y, -1), (X, Height), (Width, Y)]
        whereNotToLook = Formation + fieldEdge
        lookHere = (Index for Index in whereToLook
                    if Index not in whereNotToLook)
        foundConnecting = [(Pattern, Index, (X, Y)) for Index in lookHere
                           if Field[Index] == Color]
        return foundConnecting

    @property
    def rows(self):
        return zip(*[iter(self.items())] * self.width_by_gem)

    @property
    def columns(self):
        return zip(*self.rows)

    def __str__(self):
        Rows = zip(*[iter(self.values())] * self.width_by_gem)
        return '\n'.join(' '.join(Row) for Row in Rows)


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


def collect_something(Board):
    rowFormations, foundRowCombo = collect_row_formations(Board)
    colFormations, foundColCombo = collect_column_formations(Board)
    if foundRowCombo or foundColCombo:
        Combos =  collect_combos(rowFormations, colFormations)
        print_patterns(Board, Combos) # db
        comboPatterns = [Patterns for Patterns, _ in Combos]
        Board.collapse_pattern(chain(*comboPatterns)) # db ???
        Formations = collect_something(Board)
    else:
        Formations = collect_formations(rowFormations, colFormations)
    return Formations


def collect_row_formations(Board):
    Width, Height = Board.width_by_gem, Board.height_by_gem
    Formations, foundCombo = [], False
    for gemA, gemB, gemC, X, Y in gather_gem_trio(Board.rows):
        assert 0 <= X < Width and 0 <= Y < Height, 'Incorrect board dimensions.'
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


def collect_column_formations(Board):
    Formations, foundCombo = [], False
    for gemA, gemB, gemC, X, Y in gather_gem_trio(Board.columns):
        leftsidePair, rightsidePair = gemA == gemB, gemB == gemC
        if leftsidePair and rightsidePair:
            Formations.append(([(X, Y - 2), (X, Y - 1), (X, Y)], None))
            foundCombo = True
        elif leftsidePair :
            Formations.append(([(X, Y - 2), (X, Y - 1)], (X, Y, gemA)))
        elif rightsidePair:
            Formations.append(([(X, Y - 1), (X, Y)], (X, Y - 2, gemB)))
        elif gemA == gemC:
            Formations.append(([(X, Y - 2), (X, Y)], (X, Y - 1, gemA)))
    return Formations, foundCombo


def gather_gem_trio(boardVector):
    for Vector in boardVector:
        itVector = iter(Vector)
        (_, gemA), (_, gemB) = next(itVector), next(itVector)
        for (X, Y), gemC in itVector:
            if (gemA, gemB, gemC).count(' ') <= 1:
                yield gemA, gemB, gemC, X, Y
            gemA, gemB = gemB, gemC


def collect_combos(rowFormations, colFormations):
    rowCombos = [(P, Link) for P, Link in rowFormations if Link is None]
    colCombos = [(P, Link) for P, Link in colFormations if Link is None]
    Combos = collect_star(rowCombos, colCombos, Combo=True)
    if not Combos:
        Combos = improve_collections(rowCombos)
        Combos.extend(improve_collections(colCombos))
    return Combos


def collect_formations(rowFormations, colFormations):
    improvedRowFormations = improve_collections(rowFormations)
    improvedColFormations = improve_collections(colFormations)
    starFormations = collect_star(rowFormations, colFormations, Combo=False)
    return improvedRowFormations, improvedColFormations, starFormations


def improve_collections(basicFormations):
    improvedFormations = [([(-1, -1), (-1, -1)], (-1, -1, -1))]
    for Pattern, Link in basicFormations:
        previousPattern, previousLink = improvedFormations[-1]
        if Link == previousLink and previousPattern[-1] in Pattern:
            previousPattern.append(Pattern[-1])
        else:
            # Copies to prevent modification to basicFormations.
            improvedFormations.append((list(Pattern), Link))
    return improvedFormations[1:]


def collect_star(rowFormations, colFormations, Combo):
    Intersections = collect_intersections(rowFormations, colFormations, Combo)
    if Intersections:
        filter_crossing = (filter_crossing_combos if Combo
                           else filter_crossing_formations)
        crossingRowFilter =  filter_crossing(rowFormations, Intersections)
        crossingColFilter =  filter_crossing(colFormations, Intersections)
        starFormations = join_crossing(
            crossingRowFilter, crossingColFilter, Combo)
    else:
        starFormations = []
    return starFormations


def collect_intersections(rowFormations, colFormations, Combo):
    if rowFormations and colFormations:
        rowPatterns, rowLinks = zip(*rowFormations)
        colPatterns, colLinks = zip(*colFormations)
        if Combo:
            Intersections = set(chain(*rowPatterns)) & set(chain(*colPatterns))
        else:
            Intersections = set(rowLinks) & set(colLinks)
    else:
        Intersections = set()
    return Intersections

        
def filter_crossing_combos(Combos, Intersections):
    for Pattern, _ in Combos:
        for Link in set(Pattern) & Intersections:
            yield (Pattern, Link)


def filter_crossing_formations(Formations, Intersections):
    for Pattern, Link in Formations:
        if Link in Intersections:
            yield (Pattern, Link)


def join_crossing(crossingRowFormations, crossingColFormations, Combo):
    organizedRowFormations = organize_formation(crossingRowFormations)
    organizedColFormations = organize_formation(crossingColFormations)
    crossingFormations = join_organized(
        organizedRowFormations, organizedColFormations, Combo)
    return crossingFormations


def organize_formation(Formation):
    Order = {}
    for Pattern, Link in Formation:
        Order.setdefault(Link, []).append(Pattern)
    return Order


def join_organized(organizedRowFormations, organizedColFormations, Combo):
    if Combo:
        remove_redundant_gem(organizedColFormations)
    crossingFormations = []
    for Link in organizedRowFormations:
        patternPairs = product(organizedRowFormations[Link],
                               organizedColFormations[Link])
        crossingFormations.extend([(rowPattern + colPattern, Link)
                                   for rowPattern, colPattern in patternPairs])
    return crossingFormations


def remove_redundant_gem(organizedColCombo):
    for Link, Patterns in organizedColCombo.items():
        for Index, Pattern in enumerate(Patterns):
            # Copies to prevent modification to basicFormations.
            patternCopy = list(Pattern)
            patternCopy.remove(Link)
            Patterns[Index] = patternCopy


def print_patterns(Field, Formations):
    byPatternLen = OrderedDict(((5, set()), (4, set()), (3, set()), (2, set())))
    for Pattern, _ in Formations:
        byPatternLen[len(Pattern)].update(Pattern)
    colorArgs = byPatternLen.values()
    win_terface.print_colorized_board(Field.rows, *colorArgs, end=' ')
    print()
    

def print_moves(Field, Formations):
    colorArgs = [list(chain(*Group)) for Group in zip(Formations)]
    win_terface.print_colorized_board(Field.rows, *colorArgs, end=' ')
    

def improved_field():
    Field = (
        'YYBBBYYB', # Combo and Pair detection and handling.
        'GGGRRGGG', # Combo and Pair detection and handling.
        'POPOOOPO', # Combo and Split detection and handling.
        'SYYYYYSY', # Combo and Split detection and handling.
        'BGGBGBGB', # Pair and Split detection and handling.
        'ORORORRO', # Pair and Split detection and handling.
        'PSSPSSPP', # Pair and Split detection and handling.
        )
    bjwdField = BejeweledField(
        (((X, Y), V) for Y, Row in enumerate(Field) for X, V in enumerate(Row)))
    return bjwdField


def star_field():
    Field = (
        'WBBWWGGW',
        'BWOOPPWG',
        'BOWYYWPG',
        'WOYWWBPW',
        'WRYWWBSW',
        'GRWBBWSO',
        'GWRRSSWO',
        'WGGWWOOW',
        )
    bjwdField = BejeweledField(
        (((X, Y), V) for Y, Row in enumerate(Field) for X, V in enumerate(Row)))
    return bjwdField


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
    Formations = collect_something(Test)
    # for Formation in chain(*Formations):
        # print(Formation)
    print_patterns(Test, chain(*Formations))

if __name__ == '__main__':
    main()
