class SceneRenderer2D(object):

    @classmethod
    def makeAtlas(cls, name: str, data: bytes, size: tuple):
        tex = burst.p3d.Texture()
        tex.setup2dTexture(*size, burst.p3d.Texture.TUnsignedByte, burst.p3d.Texture.FRgba)
        tex.setFullpath(name)
        tex.setName(name)
        tex.setRamImage(data)
        burst.p3d.TexturePool.addTexture(tex)

    def __init__(self,
                 scene_name: str, scene_res: tuple,
                 atlas_name: str, atlas_data: bytes, atlas_size: tuple,
                 atlas_rules: dict):
        super().__init__()
        self.adjustWindow(scene_name, scene_res)
        self.makeAtlas(atlas_name, atlas_data, atlas_size)
        self.tiles = burst.tile.TileSet(atlas_name, **atlas_rules)

    def adjustWindow(self, scene_name: str, scene_res: tuple):
        prop = burst.p3d.WindowProperties()
        prop.setTitle(scene_name)
        prop.setSize(scene_res)
        base.win.requestProperties(prop)

    def makeTile(self, index: int) -> burst.p3d.NodePath:
        # TEMP
        if not hasattr(self, '_cm'):
            self._cm = burst.p3d.CardMaker(f'{self.tiles.name}')
            self._cm.setFrameFullscreenQuad()

        np = hidden.attachNewNode(self._cm.generate())
        np.setTexture(self.tiles.get(index))
        np.node().setName(f'{index}_{self._cm.name}')
        return np
