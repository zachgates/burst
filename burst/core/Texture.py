__all__ = [
    'Texture',
]


import typing

import numpy as np

from panda3d import core as p3d


class Texture(p3d.Texture):

    def __init__(self, name: str, size: p3d.LVector2i):
        super().__init__(name)

        self.__size = size
        self.__data = None

        self.set_fullpath(name)
        self.setup_2d_texture(
            self.__size.x,
            self.__size.y,
            p3d.Texture.T_unsigned_byte,
            p3d.Texture.F_rgba,
            )

    @property
    def buffer(self) -> typing.Union[p3d.PTAUchar, p3d.CPTAUchar]:
        return self.__data

    def get_ram_image(self) -> np.ndarray:
        if hash(super().get_ram_image()) != hash(self.__data):
            raise OSError('ram image changed')
        else:
            return np.reshape(self.__data, (self.__size.x, self.__size.y, 4))

    def get_ram_image_as(self, format):
        raise NotImplementedError()

    def set_ram_image(self, data: typing.Union[p3d.PTAUchar, p3d.CPTAUchar]):
        if not isinstance(data, (p3d.PTAUchar, p3d.CPTAUchar)):
            raise TypeError('expected PTAUchar or CPTAUchar')
        else:
            self.__data = data
            super().set_ram_image(self.__data)

    def set_ram_image_as(self, data, format):
        raise NotImplementedError()
