import math
from pathlib import Path
from typing import override

import glm
import moderngl as mgl
import moderngl_window as mglw
from objloader import Obj

from config import GL_VERSION, WINDOW_SIZE, WINDOW_TITLE
from util import load_file, root_dir


class Window(mglw.WindowConfig):
    gl_version = GL_VERSION
    window_size = WINDOW_SIZE
    title = WINDOW_TITLE
    resource_dir = root_dir() / "resources"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        shaders_path = self.resource_dir / "shaders"
        objects_path = self.resource_dir / "objects"
        self.shader_program = self.ctx.program(
            vertex_shader=load_file(shaders_path / "vertex-shader.vert"),
            # geometry_shader=load_file(shaders_path / "geometry-shader.geom"),
            fragment_shader=load_file(shaders_path / "fragment-shader.frag"),
        )
        self.model = GeometryModel(self.ctx, objects_path / "cube.obj")
        self.vao = self.model.vertex_array(self.shader_program)

    @override
    def on_render(self, time, frame_time) -> None:
        self.ctx.clear(0.25, 0.25, 0.25, 0.25)

        eye = (5.0, 5.0, 5.0)
        proj = glm.perspective(math.radians(60.0), self.wnd.aspect_ratio, 1.0, 1000.0)
        look = glm.lookAt(eye, (0, 0, 0), (0.0, 0.0, 1.0))

        self.shader_program["projection_matrix"].write(proj)
        self.shader_program["model_matrix"].write(glm.mat4(1.0))
        self.shader_program["view_matrix"].write(look)

        self.vao.render(mgl.TRIANGLES)


class GeometryModel:
    def __init__(self, ctx: mgl.Context, path: Path):
        obj = Obj.open(path)
        self.ctx: mgl.Context = ctx
        self.vbo: mgl.Buffer = ctx.buffer(obj.pack(("vx vy vz nx ny nz tx ty")))

    def vertex_array(self, program: mgl.Program) -> mgl.VertexArray:
        return self.ctx.vertex_array(
            program,
            [(self.vbo, "3f 2f 3f", "in_position", "in_normal", "in_uv")],
        )
