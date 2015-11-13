def translate_board3(filePathName=''):
    '''Simplifies the screen of gems into a grid of colors.'''
    boardImage = ImageGrab.grab(GRID_POS)
    pixelGrid = reduce_gems(numpy.array(boardImage))
    boardTranslation =  numpy.apply_along_axis(rgb_cipher, 2, pixelGrid)
    
    if filePathName:
        translateBoard = write_translation_overlay(
            boardImage, boardTranslation)
        translateBoard.save(filePathName, 'PNG')
        
    return boardTranslation

def reduce_gems(screenArray):
    '''Reduce each gem to a single RGB value.'''
    gemPixels = []
    for Y in xrange(8):
        Top = Y*82+43
        gemPixels.append([screenArray[Top,X*82+38] for X in xrange(8)])
    return numpy.array(gemPixels)

def rgb_cipher(gemPixel):
    '''Decodes the RGB value to a representing letter.'''
    colorDeviations = numpy.absolute(COLOR_ARRAY - gemPixel).sum(1)
    colorRGB = tuple(COLOR_ARRAY[colorDeviations.argmin()])
    return COLOR_CIPHER[colorRGB]

def pupil:
    pass

def ():
