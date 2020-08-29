load-display pandagl

win-origin -2 -2
win-size 512 512
window-title Scene Maker
fullscreen #f

notify-level info

model-path $THIS_PRC_DIR/../data
model-cache-dir $THIS_PRC_DIR/../.cache
model-cache-models #f

model-cache-textures #f
model-cache-compressed-textures #f
compressed-textures #f

textures-square none
textures-power-2 none
# fake-texture-image fake_4x4.png
texture-anisotropic-degree 100

tile-sheet-path tilesheet.png
tile-sheet-mode RGBA
