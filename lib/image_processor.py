#!/usr/bin/python
# coding: utf-8

"""
@file   image_processor.py
@brief  Contains stuff to process images
"""

from struct import unpack


class ImageProcessorException(Exception):
    pass


class BitmapProcessor():
    """
    @class  BitmapProcessor
    @brief  Processes bitmap images
    """

    def __init__(self, width, height, color_depth, compression):
        """
        @brief  Creates a BitmapProcessor and sets some necessary values
        @param  width INT The maximum width of images
        @param  height INT The maximum height of images
        @param  color_depth INT The allowed color depth
        @param  compression INT The allowed compression
        """
        self.width = width
        self.height = height
        self.color_depth = color_depth
        self.compression = compression

    def process_image(self, filename):
        """
        @brief  Reads the image, checks its properties and returns the image data
        @param  filename STRING
        """
        # read the file in binary form
        with open(filename, 'rb') as f:
            byte = f.read(1)
            byte_image = ''
            while byte != '':
                byte_image += byte
                byte = f.read(1)

        # parse the bitmaps header
        bfType, bfSize, bfReserved, bfOffBits, \
        biSize, biWidth, biHeight, biPlanes, biBitCount, biCompression, \
        biSizeImage, biXPelsPerMeter, biYPerlsPerMeter, biClrUsed, \
        biClrImportant = unpack(
            '<2sIIIIIihhIIIIII', byte_image[:54])

        # @todo: Raise different exceptions for different cases?
        if bfType != 'BM':
            raise ImageProcessorException('File magic bytes do not match "BM"!')
        if biWidth != self.width:
            raise ImageProcessorException(
                'Image width does not match display width!')
        if abs(biHeight) != self.height:
            raise ImageProcessorException(
                'Image height does not match display height!')
        if biBitCount != self.color_depth:
            raise ImageProcessorException(
                'Image color depth does not meet display specifications!')
        if biCompression != self.compression:
            raise ImageProcessorException(
                'Image compression does not meet display specifications!')

        # jump to the actual image data
        byte_image = byte_image[bfOffBits:]

        # process the image data
        lines = {}
        for i in range(abs(biHeight)):
            if biHeight > 0:
                lines[biHeight - 1 - i] = byte_image[i * 16:(i + 1) * 16]
            else:
                lines[i] = byte_image[i * 16:(i + 1) * 16]

        return lines
