from panda3d import core as p3d

from .XYDataset import XYDataset


class PixelSet(XYDataset):

    _BLANK = p3d.LVector4i.zero()

    def __init__(self, tex: p3d.Texture, mode = 'BGRA'):
        if tex and tex.hasRamImage():
            width, height = (tex.getXSize(), tex.getYSize())
            data = tex.getRamImageAs(mode)
        else:
            width = height = 0
            data = b''

        super().__init__(width, height, data, mode)

        for offset in range(0, len(data), len(mode)):
            # Determine cell data
            color = self._data[offset : offset + len(mode)]
            index = offset // len(mode)
            point = p3d.LPoint2i(
                x = self.height - (index // self.width),
                y = index % self.width + 1)

            # Define the cell
            self._grid[point] = color
