'''
    Take redundant translations of a bejeweled board one gem at a time
with multiple deciphers. Update their cipher dictionary with the
translation of the others when no translation is returned. In conflict
of one another display whats being read to the user and write the
users response into their cipher dictionary.
'''

from __future__ import print_function
from cPickle import dump, load
from itertools import izip
import time
from PIL import Image
import numpy


class GemTranslator(object):
    '''Wraps gem translators.'''

    def __init__(self, simplifyBoardFunc, cipherDict, *args):
        self.convert_board = simplifyBoardFunc
        if type(cipherDict) == dict:
            self.Cipher = cipherDict
        else:
            self.filePathName = cipherDict
            try:
                self.Cipher = self.load_cipher()
            except IOError:
                print('Cipher was not found. Starting from scratch.')
                self.Cipher = {}
        self.convertBoardArgs = args

    def new_board(self, boardArray):
        '''Converts the gems into cipher keys.'''
        self.keyGrid = self.convert_board(boardArray, *self.convertBoardArgs)

    def translate(self, Index):
        # !! Independent conversion to key because of write_to_cipher.
        self.cipherKey = self.keyGrid[Index]
        return self.cipherKey, self.Cipher.get(self.cipherKey)

    def write_to_cipher(self, Index, Answer):
        self.cipherKey = self.keyGrid[Index]
        self.Cipher[self.cipherKey] = Answer

    def load_cipher(self):
        '''Loads the cipher from a saved file.'''
        return load(open(self.filePathName, 'rb'))

    def save_cipher(self):
        '''Saves a cipher to a file.'''
        dump(self.Cipher, open(self.filePathName, 'wb'))


def main(boardQ, masterArray):
    pass


def read_queue(boardQ):
    print('read_queue has started.')
    while True:
        try:
            boardArray, masterArray = boardQ.get()
        except:
            break
        else:
            reader_handler(boardArray, masterArray)
        finally:
            boardQ.task_done()


def reader_handler(boardArray, masterArray):
    '''Take redundant readings of the board.'''
    for Translator in readerLst:
        Translator.new_board(boardArray)
    for Index, Answer in numpy.ndenumerate(masterArray):
        Result = []
        for Translator in readerLst:
            Result.append(trainer(Translator, Index, Answer))
        Incorrect, Keys = zip(*Result)
        if any(Incorrect):
            I, J = Index
            missedDict[tuple(Keys)] = receive_gem(I, J, boardArray)
    return missedDict


def trainer(Translator, Index, Answer):
    translatedKey, translatedResult = Translator.translate(Index)

    if not translatedResult:
        Translator.write_to_cipher(Index, Answer)
        Incorrect = False
    else:
        Incorrect = translatedResult != Answer

    return Incorrect, translatedKey


def query_referee():
    '''Asks the user for the correct answers.'''
    print("{} conflicts.".format(len(missedDict)))
    Score = [0 for _ in readerLst]
    for Keys, gemArray in missedDict.iteritems():
        Image.fromarray(numpy.uint8(gemArray)).show()
        Correct = raw_input('\rIt was...? ')
        for Idx, (Translator, Key) in enumerate(izip(readerLst, Keys)):
            Score[Idx] += 1 if Translator.Cipher[Key] == Correct else 0
            Translator.Cipher[Key] = Correct
    print(Score)


def save_ciphers():
    for Translator in readerLst:
        Translator.save_cipher()


def receive_gem(Y, X, screenArray, Section=None):
    try:
        addTop, addLeft, selectHight, selectWidth = Section
    except TypeError:
        addTop, addLeft, selectHight, selectWidth = 0, 0, 82, 82
    Top, Left = Y*82 + addTop, X*82 + addLeft
    return screenArray[Top:Top+selectHight, Left:Left+selectHight]


def convert_to_key(boardArray, colorPallet):
    gemGrid = collect_1pixel(boardArray)
    return normalize_value(nearest_color, -1, gemGrid, colorPallet)


def collect_1pixel(boardArray):
    '''Reduce each gem to a single RGB value.'''
    rowIndexLst = [X*82 + 41 for X in xrange(8)]
    colIndexLst = [Y*82 + 41 for Y in xrange(8)]
    return boardArray[rowIndexLst,:][:,colIndexLst]


def normalize_value(normalizeFunc, actingScope, disArray, *args):
    expectedArray = numpy.empty((8, 8), dtype=object)
    for Index in numpy.ndindex(disArray.shape[:actingScope]):
        expectedArray[Index] = normalizeFunc(disArray[Index], *args)
    return expectedArray


def nearest_color(pixelRGB, colorPallet):
    '''Returns the nearest element in colorPallet to the pixelRGB.'''
    rgbDeviations = numpy.absolute(colorPallet - pixelRGB)
    assert rgbDeviations.shape[-1] == 3
    totalDeviations = rgbDeviations.sum(-1)
    return tuple(colorPallet[totalDeviations.argmin()])


def convert_pair_to_key(boardArray, colorPallet):
    gemGrid = collect_2pixels(boardArray)
    return normalize_value(nearest_color_pair, -2, gemGrid, colorPallet)


def collect_2pixels(boardArray):
    '''Reduce each gem to a pair of RGB values.'''
    topRowIndexLst = [X*82 + 31 for X in xrange(8)]
    botRowIndexLst = [X*82 + 51 for X in xrange(8)]
    columnIndexLst = [Y*82 + 41 for Y in xrange(8)]
    gemTop = boardArray[topRowIndexLst,:][:,columnIndexLst]
    gemBot = boardArray[botRowIndexLst,:][:,columnIndexLst]
    assert gemTop.shape == (8, 8, 3) and gemBot.shape == (8, 8, 3)
    return numpy.dstack((gemTop, gemBottom)).reshape(8, 8, 2, 3)


def nearest_color_pair(pixelPair, colorPallet):
        nearestPair = (nearest_color(pixelRGB, colorPallet)
                       for pixelRGB in pixelPair)
        return tuple(nearestPair)


def sum_of_gems(boardArray, actingAxis, Section):
    dtype = int if actingAxis is None else object
    gemBoard = numpy.empty((8, 8), dtype)
    for Y, X in numpy.ndindex(8, 8):
        gemSection = receive_gem(Y, X, boardArray, Section)
        sumVal = gemSection.sum(actingAxis)
        try:
            gemBoard[Y, X] = tuple(gemSection.sum(actingAxis))
        except TypeError:
            gemBoard[Y, X] = gemSection.sum(actingAxis)
    return gemBoard

color8 = numpy.array([
    [0,       0,   0],
    [0,       0, 255],
    [0,    255,   0],
    [0,    255, 255],
    [255,    0,   0],
    [255,    0, 255],
    [255, 255,   0],
    [255, 255, 255],
    ])

color27 = numpy.array([
    [0,      0,   0],
    [0,      0, 127],
    [0,      0, 255],
    [0,   127,   0],
    [0,   127, 127],
    [0,   127, 255],
    [0,   255,   0],
    [0,   255, 127],
    [0,   255, 255],
    [127,   0,   0],
    [127,   0, 127],
    [127,   0, 255],
    [127, 127,   0],
    [127, 127, 127],
    [127, 127, 255],
    [127, 255,   0],
    [127, 255, 127],
    [127, 255, 255],
    [255,   0,   0],
    [255,   0, 127],
    [255,   0, 255],
    [255, 127,   0],
    [255, 127, 127],
    [255, 127, 255],
    [255, 255,   0],
    [255, 255, 127],
    [255, 255, 255],
    ])

readerLst = [
    GemTranslator(convert_to_key, '.\\Cipher_1_27.pkl', color27),
    GemTranslator(convert_pair_to_key, '.\\Cipher_2_8.pkl', color8),
    GemTranslator(convert_pair_to_key, '.\\Cipher_2_27.pkl', color27),
    # GemTranslator(
    #   sum_of_gems, '.\\Cipher_sum1_400.pkl', None, (31, 31, 20, 20)),
    # GemTranslator(
    #   sum_of_gems, '.\\Cipher_sum3_400.pkl', (0, 1), (31, 31, 20, 20)),
    # GemTranslator(
    #   sum_of_gems, '.\\Cipher_sum1_82.pkl', None, (0, 41, 82, 1)),
    # GemTranslator(
    #   sum_of_gems, '.\\Cipher_sum3_82.pkl', (0, 1), (0, 41, 82, 1))
    ]

missedDict = {}

''' # reader_1_custom
averageSamples = numpy.array([ # Average of image samples.
            [19, 136, 252], [28, 173, 41], [230, 110, 37], [241, 14, 240],
            [234, 234, 234], [250, 28, 57], [253, 246, 34]
            ])
Cipher_1_custom = {Val: Val for Val in 'BGOPRSYH'}


def tolerent_deviation(pixelRGB, colorPallet):
    Deviations = numpy.absolute(colorPallet - Pixel).sum(1)
    if Deviations.min() > 120: # 216 colors for tolerance.
        Color = 'H'
    else:
        Color = colorDict[Deviations.argmin()]
    return Color
'''

if __name__ == '__main__':
    pass
