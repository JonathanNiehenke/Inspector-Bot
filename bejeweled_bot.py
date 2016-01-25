"""
Bot that plays Bejeweled by reading the screen, moving the mouse and
making decisions usually favoring special gem creation.
"""
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

# To do:
    # Include special gem management
    # Include special gem effect

from collections import namedtuple, OrderedDict
from itertools import chain, product
from time import sleep, time

import win_terface
import bejeweled_helper

db=print

Form = namedtuple('Formation', ['Pattern', 'Link'])
Link = namedtuple('Link', ['Coord', 'Color'])
Cont = namedtuple('Connection', ['Pattern', 'moveFrom', 'moveTo'])


class BejeweledField(OrderedDict):
    """Object mimicing Bejewled2 field and mechanics."""
    height_by_gem, width_by_gem = 8, 8

    def __init__(self, *args, **kwargs):
        OrderedDict.__init__(self, *args, **kwargs)

    def connect_gems(self, Move):
        Pattern, From, To = Move
        self.swap_gems(From, To)
        self.collapse_pattern(Pattern + [To])

    def swap_gems(self, From, To):
        self[From], self[To] = self[To], self[From]

    def collapse_pattern(self, Pattern):
        for gemX, gemY in Pattern:
            gather_above = ((gemX, Y) for Y in range(0, gemY + 1))
            Coordes, Gems = zip(*[(Coord, self[Coord]) for Coord in gather_above])
            Gems = (' ',) + Gems[:-1]
            for Coord, Gem in zip(Coordes, Gems):
                self[Coord] = Gem

    def update(self, updaterFunc):
        for Coord in Field:
            Field[Coord] = updaterFunc(Coord)

    def clear(self):
        Height, Width = self.height_by_gem, self.width_by_gem
        Coords = ((X, Y) for Y in range(Height) for X in range(Width))
        self = {Coord: ' ' for Coord in Coords}

    def assert_dims(self):
        (rowMin, rowMax), (colMin, colMax) = ((min(Vector), max(Vector))
                                              for Vector in zip(*self.keys()))
        Msg = 'Vector Min: {}, Max: {}'.format
        assert rowMin == 0 and rowMax == self.height_by_gem - 1, Msg(rowMin, rowMax)
        assert colMin == 0 and colMax == self.width_by_gem - 1, Msg(colMin, colMax)

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

    # left_field_margin, top_field_margin, gem_size = 306, 32, 84
    left_field_margin, top_field_margin, gem_size = 195, 46, 52.625
    indexCollection = set(product(list(range(8)), repeat=2))

    def __init__(self, *args, **kwargs):
        OrderedDict.__init__(self, *args, **kwargs)
        self.game_window = win_terface.WindowElement(
            'MainWindow', 'Bejeweled 2 Deluxe 1.1', bringTop=True)
        self.window_left, self.window_top, _, _ = self.game_window.position
        self.read_field((X, Y) for Y in range(8) for X in range(8))
        print(self)

    def read_field(self, indexCollection=None):
        if indexCollection is None:
            indexCollection = self.keys()
        captureImage = self.game_window.screen_capture()
        for Gem in indexCollection:
            self[Gem] = self.decipher_gem(Gem, captureImage)

    def decipher_gem(self, Gem, captureImage):
        windowX, windowY = self.convert_gem_index_to_window(*Gem)
        pixelRGB = captureImage[windowX, windowY]
        Max, Min = max(pixelRGB), min(pixelRGB)
        Chroma = Max - Min 
        if Chroma:
            Hue = self.identify_hue(*pixelRGB, Max, Chroma)
            try:
                Color = self.decipher_hue(Hue)
            except ValueError:
                print(Gem, Hue, Chroma, Max)
                raise
                # Filename = '@{}_{}{}{}{}'.format(time(), Gem, Hue, Chroma, Max)
                # captureImage.save('E:\\Desktop\\BB\\{}.bmp'.format(Filename))
        else:
            Color = 'S'
        return Color

    def identify_hue(self, Red, Green, Blue, Max, Chroma):
        if Max == Red:
            Hue = ((Green - Blue) / Chroma) % 6
        elif Max == Green:
            Hue = ((Blue - Red) / Chroma) + 2
        else:
            Hue = ((Red - Green) / Chroma) + 4
        return int(Hue * 60)


    def decipher_hue(self, Hue):
        if Hue <= 15 or 350 <= Hue:
            Color = 'R'
        elif 26 <= Hue <= 54:
            Color = 'O'
        elif 50 <= Hue <= 65:
            Color = 'Y'
        elif 110 <= Hue <= 140:
            Color = 'G'
        elif 180 <= Hue <= 240:
            Color = 'B'
        elif 280 <= Hue <= 320:
            Color = 'P'
        elif 160 <= Hue < 180:
            print('Incountered Menu')
            raise ValueError
        else:
            raise ValueError
        return Color


    def execute_drag(self, From, To):
        win_terface.execute_mouse(
            self.convert_gem_index_to_screen(*From), ('Left', 'Press'))
        sleep(1/16)
        win_terface.execute_mouse(
            self.convert_gem_index_to_screen(*To), ('Left', 'Release'))

    def convert_gem_index_to_screen(self, X, Y):
        """Converts gem index to the expected screen X and Y."""
        windowX, windowY = self.convert_gem_index_to_window(X, Y)
        return self.window_left + windowX, self.window_top + windowY

    def convert_gem_index_to_window(self, X, Y):
        """Converts the X, Y of a gem to its X, Y in the window."""
        windowX = self.left_field_margin + int(self.gem_size * X) + 26
        windowY = self.top_field_margin + int(self.gem_size * Y) + 8
        return windowX, windowY

def collect_something(Field):
    rowMatches, foundRowCombo = collect_matches(Field.rows)
    colMatches, foundColCombo = collect_matches(Field.columns)
    if foundRowCombo or foundColCombo:
        Combos =  collect_combos(rowMatches, colMatches)
        bejeweled_helper.print_patterns(Field, [Combos]) # db
        comboPatterns, _ = zip(*Combos)
        Field.collapse_pattern(chain(*comboPatterns)) # db  need ???
        Formations = collect_something(Field)
    else:
        improvedFormations = collect_formations(rowMatches, colMatches)
        Formations = improvedFormations + [rowMatches + colMatches]
    return Formations


def collect_matches(fieldVector):
    Matches, foundCombo = [], False
    zipTrio = (zip(*Trio) for Trio in gather_gem_trio(fieldVector))
    for Coords, Colors in zipTrio:
        uniqueColors = len(set(Colors))
        if uniqueColors == 2 and Colors.count(' ') <= 1:
            Matches.append(construct_formation(Coords, Colors))
        elif uniqueColors == 1 and ' ' not in Colors:
            Matches.append(Form(list(Coords), None))
            foundCombo = True
    return Matches, foundCombo


def gather_gem_trio(boardVector):
    for Vector in boardVector:
        itVector = iter(Vector)
        gemA, gemB = next(itVector), next(itVector)
        for gemC in itVector:
            yield (gemA, gemB, gemC)
            gemA, gemB = gemB, gemC


def construct_formation(Coords, Colors):
    (coordA, coordB, coordC), (colorA, colorB, colorC) = Coords, Colors
    if colorA == colorB:
        Formation = Form([coordA, coordB], Link(coordC, colorA))
    elif colorB == colorC:
        Formation = Form([coordB, coordC], Link(coordA, colorB))
    else:
        Formation = Form([coordA, coordC], Link(coordB, colorA))
    return Formation


def collect_combos(rowMatches, colMatches):
    rowCombos = [(P, Link) for P, Link in rowMatches if Link is None]
    colCombos = [(P, Link) for P, Link in colMatches if Link is None]
    Combos = collect_star(rowCombos, colCombos, isCombo=True)
    if not Combos:
        Combos = improve_collections(rowCombos)
        Combos.extend(improve_collections(colCombos))
    return Combos


def collect_formations(rowFormations, colFormations):
    improvedRowFormations = improve_collections(rowFormations)
    improvedColFormations = improve_collections(colFormations)
    starFormations = collect_star(rowFormations, colFormations, isCombo=False)
    return [starFormations, improvedRowFormations, improvedColFormations]


def improve_collections(basicMatches):
    """Returns a collection of larger matches (Normal 3 -> Hyper 5)."""
    improvedMatches = [([(-1, -1), (-1, -1)], ((-1, -1), -1))]
    for Pattern, Link in basicMatches:
        previousPattern, previousLink = improvedMatches[-1]
        if Link == previousLink and previousPattern[-1] in Pattern:
            previousPattern.append(Pattern[-1])
        else:
            # Copies to prevent source (basicMatches) modification.
            copiedPattern =  list(Pattern)
            improvedMatches.append(Form(copiedPattern, Link))
    return improvedMatches[1:]


def collect_star(rowMatches, colMatches, isCombo):
    Intersections = collect_intersections(rowMatches, colMatches, isCombo)
    if Intersections:
        filter_crossing = (filter_crossing_combos if isCombo
                           else filter_crossing_formations)
        crossingRowFilter =  filter_crossing(rowMatches, Intersections)
        crossingColFilter =  filter_crossing(colMatches, Intersections)
        starMatches = join_crossing(
            crossingRowFilter, crossingColFilter, isCombo)
    else:
        starMatches = []
    return starMatches


def collect_intersections(rowMatches, colMatches, isCombo):
    if rowMatches and colMatches:
        rowPatterns, rowLinks = zip(*rowMatches)
        colPatterns, colLinks = zip(*colMatches)
        if isCombo:
            Intersections = set(chain(*rowPatterns)) & set(chain(*colPatterns))
        else:
            Intersections = set(rowLinks) & set(colLinks)
    else:
        Intersections = set()
    return Intersections

        
def filter_crossing_combos(Combos, Intersections):
    for Pattern, _ in Combos:
        for Intersection in set(Pattern) & Intersections:
            yield (Pattern, Intersection)


def filter_crossing_formations(Formations, Intersections):
    for Pattern, Intersection in Formations:
        if Intersection in Intersections:
            yield (Pattern, Intersection)


def join_crossing(crossingRowMatches, crossingColMatches, isCombo):
    organizedRowMatches = organize_formation(crossingRowMatches)
    organizedColMatches = organize_formation(crossingColMatches)
    crossingMatches = join_organized(
        organizedRowMatches, organizedColMatches, isCombo)
    return crossingMatches


def organize_formation(Formation):
    Order = {}
    for Pattern, Link in Formation:
        Order.setdefault(Link, []).append(Pattern)
    return Order


def join_organized(organizedRowMatches, organizedColMatches, isCombo):
    if isCombo:
        remove_redundant_gem(organizedColMatches)
    crossingMatches = []
    for Intersection in organizedRowMatches:
        patternPairs = product(organizedRowMatches[Intersection],
                               organizedColMatches[Intersection])
        crossingMatches.extend([(rowPattern + colPattern, Intersection)
                                   for rowPattern, colPattern in patternPairs])
    return crossingMatches


def remove_redundant_gem(organizedColCombo):
    for Intersection, Patterns in organizedColCombo.items():
        for Coord, Pattern in enumerate(Patterns):
            # Copies to prevent source (basicFormations) modification.
            copiedPattern = list(Pattern)
            copiedPattern.remove(Intersection)
            Patterns[Coord] = copiedPattern


def collect_moves(Field, Formations):
    """Returns list of moves that join Formations."""
    foundMoves = []
    for Formation in chain(*Formations):
        foundMoves.extend(collect_connections(Field, Formation))
    return foundMoves


def collect_connections(Field, Formation):
    """Return list of moves completing the Formation."""
    (Pattern, Link), Width, Height = Formation, 8, 8
    ((X, Y), Color) = Link
    whereToLook = set([(X - 1, Y), (X, Y - 1), (X, Y + 1), (X + 1, Y)])
    lookHere = whereToLook - set(Pattern)
    Connections = [Cont(Pattern, Coord, (X, Y)) for Coord in lookHere
                   if Field.get(Coord) == Color]
    return Connections


def play_bejeweled(Field):
    while True:
        Formations = collect_something(Field)
        # bejeweled_helper.print_patterns(Field, Formations) # db
        Moves = collect_moves(Field, Formations)
        # bejeweled_helper.print_moves(Field, Moves) #db
        _, From, To = sorted(Moves, key=lambda x: (6 - len(x[0]), x[0]))[0]
        Field.execute_drag(From, To)
        sleep(2.5)
        Field.read_field()
        db(Field, end='\n\n')
        
def main():
    # Field = BejeweledInterface()
    # Field = bejeweled_helper.move_field()
    # bjwdField = BejeweledField(
        # (((X, Y), V) for Y, Row in enumerate(Field) for X, V in enumerate(Row)))
    play_bejeweled(BejeweledInterface(BejeweledField()))


if __name__ == '__main__':
    main()
