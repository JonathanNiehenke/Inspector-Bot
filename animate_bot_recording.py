#!/usr/bin/env python

from gimpfu import (gimp, RGB, pdb, register, main,
                    PF_DIRNAME, PF_STRING, PF_OPTION, PF_SLIDER, PF_TOGGLE)
import os


def animate_recording(imageDirectory, outFilename, delayType, delayArg, Loop):
    """Create and save a gif from a directory of image files."""
    imageFiles = group_images(imageDirectory)
    if delayType:
        layeredImage = layer_images(imageFiles)
    else:
        layeredImage = layer_replay_images(imageFiles, delayArg)
    outFilePathname = os.path.join(imageDirectory, os.pardir, outFilename)
    save_gif(layeredImage, outFilePathname, 1000 // delayArg, Loop)


def group_images(imageDirectory):
    """Return paths to files in imageDirectory."""
    for Filename in sorted(os.listdir(imageDirectory)):
        filePathname = os.path.join(imageDirectory, Filename)
        if os.path.isfile(filePathname):
            yield filePathname


def layer_images(imageFiles):
    """Joins imageFiles as layers."""
    initialFile = next(imageFiles)
    layeredImage = pdb.gimp_file_load(initialFile, initialFile)
    for imageFile in imageFiles:
        newLayer = pdb.gimp_file_load_layer(layeredImage, imageFile)
        pdb.gimp_image_insert_layer(layeredImage, newLayer, None, 0)
    return layeredImage 


def layer_replay_images(imageFiles, delayMultiplier=1):
    """Joins imageFiles as delayed layers."""
    layeredImage, currentFile = gimp.Image(1, 1, RGB), next(imageFiles)
    currentLayer = pdb.gimp_file_load_layer(layeredImage, currentFile)
    layeredImage.resize(currentLayer.width, currentLayer.height, 0, 0)
    for nextFile in imageFiles:
        Delay = identify_delay(currentFile, nextFile) * delayMultiplier
        insert_layer(layeredImage, currentLayer, Delay)
        currentFile = nextFile
        currentLayer = pdb.gimp_file_load_layer(layeredImage, currentFile)
    else:
        insert_layer(layeredImage, currentLayer, Delay * 4)
    return layeredImage 


def identify_delay(currentFile, nextFile):
    currentFilename = os.path.basename(currentFile)
    nextFilename  = os.path.basename(nextFile)
    return float(nextFilename[:-4]) - float(currentFilename[:-4])


def insert_layer(layeredImage, currentLayer, Delay):
    """Insert currentLayer into layeredImage with Delay."""
    layerName = '({}ms)'.format(int(Delay))
    pdb.gimp_item_set_name(currentLayer, layerName)
    pdb.gimp_image_insert_layer(layeredImage, currentLayer, None, 0)


def save_gif(layeredImage, outFilePathname, defaultDelay, Loop):
    pdb.gimp_image_convert_indexed(layeredImage, 0, 2, 0, True, True, 0)
    pdb.file_gif_save(layeredImage, None, outFilePathname, outFilePathname,
                      False, Loop, defaultDelay, 0)

register(
    'animate_bot_recording',
    'Join images into a animated gif.',
    'Create a gif image from a directory of images in alphabetical ordered.',
    'Jonathan Niehenke',
    'Jonathan Niehenke',
    '2015',
    'animate bot recording...',
    '',
    [
        (PF_DIRNAME, 'imageDirectory', 'Directory contianing the images',
            '~/Pictures/Animate/'),
        (PF_STRING, 'outFilename', 'Save image as', 'Untitled.gif'),
        (PF_OPTION, 'delayType', 'Type of Delay', 0, ['Replay', 'Fixed']),
        (PF_SLIDER, 'delayArg',
            'Replay speed (<1 is faster)\nOr Frames per Second',
            1, (0.125, 10, 0.125)),
        (PF_TOGGLE, 'Loop', 'Loop the image', True),
        ],
    [],
    animate_recording,
    menu="<Image>/File/Create",
    )

main()
