#!/usr/bin/python
# coding: utf-8

from struct import unpack


class ImageProcessorException(Exception):
    pass


class BitmapProcessor():
    """
    """

    def __init__(self, width, height, color_depth, compression):

        self.width = width
        self.height = height
        self.color_depth = color_depth
        self.compression = compression

    def process_image(self, filename):
        with open(filename, 'rb') as f:
            byte = f.read(1)
            byte_image = ''
            while byte != '':
                byte_image += byte
                byte = f.read(1)

        bfType, bfSize, bfReserved, bfOffBits, \
        biSize, biWidth, biHeight, biPlanes, biBitCount, biCompression, \
        biSizeImage, biXPelsPerMeter, biYPerlsPerMeter, biClrUsed, \
        biClrImportant = unpack(
            '<2sIIIIIihhIIIIII', byte_image[:54])

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

        byte_image = byte_image[bfOffBits:]
        # print ''.join('%02x ' % ord(i) for i in byte_image[:128/8])       # debug
        # print ''.join('{0:0>8b} '.format(ord(i)) for i in byte_image[:16])       # debug

        lines = {}
        for i in range(abs(biHeight)):
        # print ''.join('{0:0>8b} '.format(ord(i)) for i in byte_image[i * 16:(i + 1) * 16])       # debug
            if biHeight > 0:
                lines[biHeight - 1 - i] = byte_image[i * 16:(i + 1) * 16]
            else:
                lines[i] = byte_image[i * 16:(i + 1) * 16]

        return lines
