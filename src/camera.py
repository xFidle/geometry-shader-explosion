import math

import glm
from OpenGL.GL import *


class Camera:
    def __init__(
        self,
        position,
        target,
        up,
        speed=1.0,
        fov=math.radians(60.0),
        aspect_ratio=1.0,
        near=1.0,
        far=100.0,
    ):
        self.position = position
        self.target = target
        self.up = up
        self.speed = speed
        self.fov = fov
        self.aspect_ratio = aspect_ratio
        self.near = near
        self.far = far

    def upload_uniforms(self, program):
        view = self._view_matrix()
        proj = self._proj_matrix()

        proj_loc = glGetUniformLocation(program, "projection_matrix")
        view_loc = glGetUniformLocation(program, "view_matrix")
        model_loc = glGetUniformLocation(program, "model_matrix")
        camera_loc = glGetUniformLocation(program, "camera_position")

        identity = glm.mat4(1.0)
        glUniformMatrix4fv(model_loc, 1, GL_FALSE, glm.value_ptr(identity))
        glUniformMatrix4fv(view_loc, 1, GL_FALSE, glm.value_ptr(view))
        glUniformMatrix4fv(proj_loc, 1, GL_FALSE, glm.value_ptr(proj))
        glUniform3fv(camera_loc, 1, glm.value_ptr(self.position))

    def orbit(self, radius, time):
        _, _, cam_z = self.position
        cam_x = math.sin(time) * radius
        cam_y = math.cos(time) * radius
        self.position = (cam_x, cam_y, cam_z)

    def _view_matrix(self):
        return glm.lookAt(self.position, self.target, self.up)

    def _proj_matrix(self):
        return glm.perspective(self.fov, self.aspect_ratio, self.near, self.far)
