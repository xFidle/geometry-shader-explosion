import math


WINDOW_TITLE = "Geometry Shader Explosion"
WINDOW_SIZE = (1000, 1000)
FPS = 60

VERT_SHADER = "resources/shaders/vertex-shader.vert"
GEOM_SHADER = "resources/shaders/geometry-shader.geom"
FRAG_SHADER = "resources/shaders/fragment-shader.frag"

SCENE = "resources/models/car.obj"
SCENE_FORMAT = "N3F_V3F"

CAMERA_POSITION = (1.0, 1.0, 1.0)
CAMERA_FRONT =(-3, -3, -3)
CAMERA_UP = (0.0, 1.0, 0.0)
