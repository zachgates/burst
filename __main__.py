import builtins

from direct.showbase.ShowBase import ShowBase

from .core.AppData import AppData


class BurstApp(ShowBase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.data = AppData()

    def run(self):
        self.data.load('tilesheet.png', {'tile_size': 4, 'tile_run': 4, 'tile_offset': 0})
        np = self.data.loader.make(13)
        super().run()


builtins.burst = BurstApp()
burst.run()
