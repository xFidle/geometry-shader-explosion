import math

WINDOW_TITLE = "Geometry Shader Explosion"
WINDOW_SIZE = (1600, 1000)
FPS = 60

VERT_SHADER = "resources/shaders/vertex-shader.vert"
GEOM_SHADER = "resources/shaders/geometry-shader.geom"
FRAG_SHADER = "resources/shaders/fragment-shader.frag"

CAR = "resources/models/car.obj"
CAR_FORMAT = "N3F_V3F"

INDICATOR = "resources/models/bomb.obj"
INDICATOR_FORMAT = "T2F_N3F_V3F"

CAMERA_POSITION = (5.0, 5.0, 5.0)
CAMERA_FRONT = (-5.0, -5.0, -5.0)
CAMERA_UP = (0.0, 1.0, 0.0)
