from panda3d.core import NodePath, CardMaker, TextureStage, TransparencyAttrib
from direct.showbase.ShowBase import ShowBase

from src.visual.nodes import PivotNode2D


class TestApp(ShowBase):

    def run(self):
        # Find the texture
        texture = loader.loadTexture('phase_3.5/maps/walls_palette_3cmla_1.jpg')

        # Create the 2d plane
        cm = CardMaker('wall_lg_brick')
        cm.setFrame(0, 1, 0, 1)

        # Create the card with the texture
        frame = hidden.attachNewNode(cm.generate())
        frame.setTexture(texture)
        # Account for transparency
        frame.setTransparency(TransparencyAttrib.MBinary)
        # Fit the texture to the plane
        frame.setTexOffset(TextureStage.getDefault(), 0.257813006639481, 0.757812976837158)
        frame.setTexScale(TextureStage.getDefault(), 0.484374970197677, 0.234375)
        # Use both sides to handle orientation
        frame.setTwoSided(True)

        # First wall
        n1 = PivotNode2D(frame, render)
        n1.setSx(2)
        # Second wall
        n2 = n1.copyTo(render)
        n2.setX(2)

        # Run the scene
        ShowBase.run(self)


if __name__ == '__main__':
    app = TestApp()
    app.run()
