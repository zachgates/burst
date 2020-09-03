load-display pandagl

win-origin -2 -2
win-size 512 512
window-title Scene Maker
fullscreen #f

notify-level info

model-path $THIS_PRC_DIR/data
model-cache-textures #f
model-cache-dir $THIS_PRC_DIR/../.cache

textures-square none
textures-power-2 none
# fake-texture-image fake_4x4.png
texture-anisotropic-degree 100
