import math

from panda3d import core as p3d


class PixelMatrix(object):

    _BLANK = p3d.LVector4i.zero()

    def __init__(self, tex: p3d.Texture, mode = 'BGRA'):
        if tex and tex.hasRamImage():
            width, height = (tex.getXSize(), tex.getYSize())
            data = tex.getRamImageAs(mode)
        else:
            width = height = 0
            data = b''

        self.__size = p3d.LVector2i(width, height)
        self.__mode = mode
        self.__data = memoryview(data)

    @property
    def width(self) -> int:
        return self.__size.x

    @property
    def height(self) -> int:
        return self.__size.y

    @property
    def mode(self) -> str:
        return self.__mode

    def __calcPixelByIndex(self, index: int) -> p3d.LVector4i:
        """
        Returns the sub-values of a pixel. Index expected in range [0, 256).
        """
        point = self.__calcPosFromIndex(index)
        index = self._normIndexFromPos(point) - 1
        pxSize = len(self.mode)
        pxData = self.__data[index * pxSize : index * pxSize + pxSize]
        return p3d.LVector4i(*pxData)

    def __calcPosFromIndex(self, index: int) -> p3d.LPoint2i:
        """
        Returns the 2D (X, Y) coordinates for a given pixel, from the bottom-
        left corner of the PixelMatrix. Index expected in range [0, 256).
        """
        return p3d.LPoint2i(
            x = self.height - math.floor(index / self.width),
            y = (index % self.width) + 1)

    def _normPosFromIndex(self, index: int) -> p3d.LPoint2i:
        """
        Returns the 2D (X, Y) coordinates for a given pixel, from the top-left
        corner of the PixelMatrix. Index expected in range (0, 256].
        """
        return p3d.LPoint2i(
            x = math.ceil(index / self.height),
            y = ((index - 1) % self.width) + 1)

    def _normIndexFromPos(self, point: p3d.LPoint2i) -> int:
        """
        Returns the 1D (N) coordinate for a given (X, Y) coordinate pair.
        """
        return ((point.x - 1) * self.width) + point.y

    def get(self, point: p3d.LPoint2i = None, index: int = 0) -> p3d.LVector4i:
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
