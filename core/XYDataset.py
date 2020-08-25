from panda3d import core as p3d


class XYDataset(object):

    _DTYPE = p3d.LPoint2i
    _EMPTY = p3d.LVector4i.zero()

    def __init__(self, width, height, data, mode):
        self.__size = p3d.LVector2i(width, height)
        self.__mode = mode
        self._data = memoryview(data)
        self._grid = {}

    @property
    def width(self):
        return self.__size.x

    @property
    def height(self):
        return self.__size.y

    def get(self, point: _DTYPE):
        return tuple(self._grid.get(point, self._EMPTY))

    def select(self, start: [int, _DTYPE], end: [int, _DTYPE] = None):
        """
        Generate a slice of the 2D (X, Y) matrix.
        """
        try:
            # Getting a single "start" point
            if end is None:
                cell = None
                try:
                    # Get the point by index
                    cell = self[start]
                except TypeError:
                    # Get the point from the grid
                    assert isinstance(start, self._DTYPE)
                    cell = self.get(start)
                finally:
                    # Wrap the single cell
                    yield iter([cell])
            else:
                try:
                    # Get points by index
                    yield (self[n] for n in range(start, end + 1))

                except TypeError:
                    # Get points from the grid
                    assert isinstance(start, self._DTYPE)
                    assert isinstance(end, self._DTYPE)

                    # Generate [start, end] slice
                    for x in range(start.x, end.x + 1):
                        yield (self.get(self._DTYPE(x, y))
                               for y in range(start.y, end.y + 1))

        except AssertionError:
            LOG.warning(f'invalid selection: {start} -> {end}')
            return None
