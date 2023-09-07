__all__ = [
    'PixelMatrix',
]


import math

import panda3d.core as p3d


class PixelMatrix(p3d.Texture):

    _BLANK = p3d.LVector4i.zero()

    def get_size(self) -> p3d.LVector2i:
        return p3d.LVector2i(self.get_x_size(), self.get_y_size())

    size = property(get_size)

    def get_pixel(self, index: int = 0) -> p3d.LVector4i:
        """
        Returns the sub-values of a pixel at the supplied index or point.
        """
        index %= (self.get_x_size() * self.get_y_size()) + 1
        point = self._norm_pos_from_index(index)

        if (index := self._norm_index_from_pos(point)) == 0:
            return self._BLANK
        else:
            return self.__calc_pixel_by_index(index - 1)

    def _norm_pos_from_index(self, index: int) -> p3d.LPoint2i:
        """
        Returns the 2D (X, Y) coordinates for a given pixel, from the top-left
        corner of the PixelMatrix.
        """
        return p3d.LPoint2i(
            x = math.ceil(index / self.get_y_size()),
            y = ((index - 1) % self.get_x_size()) + 1,
            )

    def _norm_index_from_pos(self, point: p3d.LPoint2i) -> int:
        """
        Returns the 1D (N) coordinate for a given (X, Y) coordinate pair.
        """
        return ((point.x - 1) * self.get_x_size()) + point.y

    def __calc_pos_from_index(self, index: int) -> p3d.LPoint2i:
        """
        Returns the 2D (X, Y) coordinates for a given pixel, from the bottom-
        left corner of the PixelMatrix.
        """
        return p3d.LPoint2i(
            x = self.get_y_size() - math.floor(index / self.get_x_size()),
            y = (index % self.get_x_size()) + 1,
            )

    def __calc_pixel_by_index(self, index: int) -> p3d.LVector4i:
        """
        Returns the sub-values of a pixel.
        """
        if buffer := self.get_ram_image():
            point = self.__calc_pos_from_index(index)
            index = self._norm_index_from_pos(point) - 1

            px_size = 4 # BGRA
            px_data = [
                buffer.get_element(i)
                for i in range(index * px_size, index * px_size + px_size)
                ]

            return p3d.LVector4i(*px_data)
        else:
            return self._BLANK
