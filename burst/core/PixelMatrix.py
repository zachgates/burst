__all__ = [
    'PixelMatrix',
]


import math

import panda3d.core as p3d

from burst.core import Rule2D


class PixelMatrix(object):

    _BLANK = p3d.LVector4i.zero()

    @classmethod
    def get_ram_format(cls):
        return cls._FORMAT

    def __init__(self, tex: p3d.Texture):
        if tex and tex.has_ram_image():
            width, height = (tex.get_x_size(), tex.get_y_size())
            data = tex.get_ram_image()
        else:
            width = height = 1
            data = bytearray(4)

        self.__size = Rule2D(width, height)
        self.__data = memoryview(data)

    @property
    def width(self) -> int:
        return self.__size.x

    @property
    def height(self) -> int:
        return self.__size.y

    @property
    def data(self) -> memoryview:
        return self.__data

    def __calc_pixel_by_index(self, index: int) -> p3d.LVector4i:
        """
        Returns the sub-values of a pixel.
        """
        if self.data:
            point = self.__calc_pos_from_index(index)
            index = self._norm_index_from_pos(point) - 1
            px_size = 4 # BGRA
            px_data = self.data[index * px_size : index * px_size + px_size]
            return p3d.LVector4i(*px_data)
        else:
            return self._BLANK

    def __calc_pos_from_index(self, index: int) -> p3d.LPoint2i:
        """
        Returns the 2D (X, Y) coordinates for a given pixel, from the bottom-
        left corner of the PixelMatrix.
        """
        return p3d.LPoint2i(
            x = self.height - math.floor(index / self.width),
            y = (index % self.width) + 1,
            )

    def _norm_pos_from_index(self, index: int) -> p3d.LPoint2i:
        """
        Returns the 2D (X, Y) coordinates for a given pixel, from the top-left
        corner of the PixelMatrix.
        """
        return p3d.LPoint2i(
            x = math.ceil(index / self.height),
            y = ((index - 1) % self.width) + 1,
            )

    def _norm_index_from_pos(self, point: p3d.LPoint2i) -> int:
        """
        Returns the 1D (N) coordinate for a given (X, Y) coordinate pair.
        """
        return ((point.x - 1) * self.width) + point.y

    def get(self, index: int = 0) -> p3d.LVector4i:
        """
        Returns the sub-values of a pixel at the supplied index or point.
        """
        index %= (self.width * self.height) + 1
        point = self._norm_pos_from_index(index)

        if (index := self._norm_index_from_pos(point)) == 0:
            return self._BLANK
        else:
            return self.__calc_pixel_by_index(index - 1)
