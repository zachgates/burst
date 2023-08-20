__all__ = [
    'SceneRendererBase',
]


import panda3d.core as p3d

from direct.showbase.DirectObject import DirectObject


class SceneRendererBase(DirectObject):

    def pack(self):
        dg = p3d.Datagram()
        dg.add_fixed_string(self.title, 0xFF)
        self.resolution.write_datagram(dg)
        dg.add_uint8(self.frame_rate)
        return dg

    def __init__(self, title: str, resolution: p3d.LVector2i):
        super().__init__()

        self._win_props = p3d.WindowProperties()
        self._win_props.set_title(title)
        self._win_props.set_size(resolution)
        self._win_props.set_fixed_size(True)
        self._adjust_window_properties()

        globalClock.set_mode(p3d.ClockObject.MLimited)
        self.set_frame_rate(1)

    def _adjust_window_properties(self):
        if base.win:
            base.win.request_properties(self._win_props)

    def get_title(self) -> str:
        return self._win_props.get_title()

    def set_title(self, title: str):
        self._win_props.set_title(title)
        self._adjust_window_properties()

    title = property(get_title, set_title)

    def get_resolution(self) -> p3d.LVector2i:
        return p3d.LVector2i(self._win_props.get_size())

    def set_resolution(self, resolution: p3d.LVector2i):
        self._win_props.set_size(resolution)
        self._adjust_window_properties()

    resolution = property(get_resolution, set_resolution)

    def get_frame_rate(self) -> int:
        return self._frame_rate

    def set_frame_rate(self, frame_rate: int):
        self._frame_rate = frame_rate
        globalClock.set_frame_rate(self._frame_rate)

    frame_rate = property(get_frame_rate, set_frame_rate)
