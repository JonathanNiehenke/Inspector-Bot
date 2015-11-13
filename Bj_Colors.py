from __future__ import print_function
from PIL import Image
import numpy

def iter_files():
    colorDict = {Color: [] for Color in list('BGOPRSYH')}
    fileLst = [r'.\Bj_low.png', r'.\Bj_high.png', r'.\Bj_ultra.png']
    for File in fileLst:
        screenArray = numpy.array(Image.open(File))
        gridArray = gem_pixels(screenArray)
        gridColors = numpy.apply_along_axis(gem_colors, 2, gridArray)
        fileDict = sort_gems(gridColors, gridArray)
        print(File)
        for Color, valueLst in fileDict.iteritems():
            colorDict[Color].extend(valueLst)
    return colorDict
        

def gems(screenArray, Offset=0, Select=82):
    gemPixels, Show = [], ''
    
    for Y, X in [(0,0), (0,1), (0,2), (0,4), (0,6), (1,0), (2,5)]: #, (6,5)
        Top, Left = Y*82+Offset,X*82+Offset
        Gem = screenArray[Top,Left]
        # if not Show:
            # Image.fromarray(Gem).show()
            # Show = raw_input()
        gemPixels.append(Gem)
    return numpy.array(gemPixels)

def gem_pixels(screenArray):
    gemPixels = []
    for Y in xrange(8):
        gemPixels.append([screenArray[Y*82+41,X*82+41] for X in xrange(8)])
    return numpy.array(gemPixels)

def gem_colors(Pixel):
    colorLst = numpy.array([
            [19, 136, 252], [28, 173, 41], [230, 110, 37], [241, 14, 240],
            [234, 234, 234], [250, 28, 57], [253, 246, 34]
            ])
    # [16, 134, 252], [30, 184, 54], [238, 134, 52],
    # [240, 14, 240], [250, 25, 54], [234, 234, 234],
    # [252, 244, 34]])
    colorCode = {0: 'B', 1: 'G', 2: 'O', 3: 'P', 4: 'R', 5: 'S', 6: 'Y'}
    Deviations = numpy.absolute(colorLst - Pixel).sum(1)
    
    if Deviations.min() > 130:
        Color = 'H'
    else:
        Color = colorCode[Deviations.argmin()]
    return Color

def sort_gems(gridColors, gridArray):
    colorDict = {Color: [] for Color in list('BGOPRSYH')}
    zippedArray = numpy.dstack((gridColors, gridArray)).reshape(-1, 4)
    for Color, Rd, Gn, Be in zippedArray:
        colorDict[Color].append([int(Rd), int(Gn), int(Be)])
    return colorDict
        
        

if __name__ == '__main__':
    colorDict = iter_files()
    for Color, valueLst in colorDict.iteritems():
        Mean = numpy.mean(numpy.array(valueLst), 0)
        print(Color, Mean)