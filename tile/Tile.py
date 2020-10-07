class Tile(burst.p3d.Texture):

    def __init__(self, name: str, index: int = 0):
        super().__init__(name)
        self.__idx = index

    def __hash__(self):
        return self.name

    @property
    def index(self):
        return self.__idx
