import math


class PixelMatrix(object):

    _BLANK = burst.p3d.LVector4i.zero()

    def __init__(self, tex: burst.p3d.Texture):
        if tex and tex.hasRamImage():
            width, height = (tex.getXSize(), tex.getYSize())
            data = tex.getRamImageAs('BGRA')
        else:
            width = height = 0
            data = bytes()

        self.__size = burst.core.Rule2D(width, height)
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

    def __calcPixelByIndex(self, index: int) -> burst.p3d.LVector4i:
        """
        Returns the sub-values of a pixel.
        """
        if self.data:
            point = self.__calcPosFromIndex(index)
            index = self._normIndexFromPos(point) - 1
            px_size = 4 # BGRA
            px_data = self.data[index * px_size : index * px_size + px_size]
            return burst.p3d.LVector4i(*px_data)
        else:
            return self._BLANK

    def __calcPosFromIndex(self, index: int) -> burst.p3d.LPoint2i:
        """
        Returns the 2D (X, Y) coordinates for a given pixel, from the bottom-
        left corner of the PixelMatrix.
        """
        return burst.p3d.LPoint2i(
            x = self.height - math.floor(index / self.width),
            y = (index % self.width) + 1)

    def _normPosFromIndex(self, index: int) -> burst.p3d.LPoint2i:
        """
        Returns the 2D (X, Y) coordinates for a given pixel, from the top-left
        corner of the PixelMatrix.
        """
        return burst.p3d.LPoint2i(
            x = math.ceil(index / self.height),
            y = ((index - 1) % self.width) + 1)

    def _normIndexFromPos(self, point: burst.p3d.LPoint2i) -> int:
        """
        Returns the 1D (N) coordinate for a given (X, Y) coordinate pair.
        """
        return ((point.x - 1) * self.width) + point.y

    def get(self,
            point: burst.p3d.LPoint2i = None,
            index: int = 0,
            ) -> burst.p3d.LVector4i:
        """
        Returns the sub-values of a pixel at the supplied index or point.
        """
        if index or point is None:
            index %= (self.width * self.height) + 1
            point = self._normPosFromIndex(index)
        else:
            point.x %= (self.height + 1)
            point.y %= (self.width + 1)

        index = self._normIndexFromPos(point)
        if index == 0:
            return self._BLANK
        else:
            return self.__calcPixelByIndex(index - 1)
