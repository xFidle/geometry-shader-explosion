import math

import glm
from OpenGL.GL import *
import config as cfg

class Camera:
    def __init__(
        self,
        position,
        front,
        up,
        speed=2.0,
        sensitivity=0.1,
        fov=math.radians(45.0),
        aspect_ratio=(cfg.WINDOW_SIZE[0] / cfg.WINDOW_SIZE[1]),
        near=0.01,
        far=100.0,
    ):
        self._position = position
        self._front = front
        self._up = up
        self._speed = speed
        self._sensitivity = sensitivity
        self._fov = fov
        self._aspect_ratio = aspect_ratio
        self._near = near
        self._far = far

        self._first_mouse = True

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
        glUniform3fv(camera_loc, 1, glm.value_ptr(self._position))

    def move_forward(self, delta_time):
        self._position += self._front * self._speed * delta_time

    def move_backward(self, delta_time):
        self._position -= self._front * self._speed * delta_time

    def move_right(self, delta_time):
        self._position += (
            glm.normalize(glm.cross(self._front, self._up)) * self._speed * delta_time
        )

    def move_left(self, delta_time):
        self._position -= (
            glm.normalize(glm.cross(self._front, self._up)) * self._speed * delta_time
        )

    def mouse_callback(self, dx, dy):
        if self._first_mouse:
            fx, fy, fz = self._front
            self._yaw = math.degrees(math.atan2(fz, fx))
            self._pitch = math.degrees(math.atan2(fy, math.sqrt(fx**2 + fz**2)))
            self._first_mouse = False

        dx *= self._sensitivity
        dy *= self._sensitivity

        self._yaw += dx
        self._pitch -= dy

        self._pitch = max(min(self._pitch, 89.0), -89.0)

        direction = glm.vec3(
            math.cos(math.radians(self._yaw)) * math.cos(math.radians(self._pitch)),
            math.sin(math.radians(self._pitch)),
            math.sin(math.radians(self._yaw)) * math.cos(math.radians(self._pitch)),
        )
        self._front = glm.normalize(direction)

    def _view_matrix(self):
        return glm.lookAt(self._position, self._position + self._front, self._up)

    def _proj_matrix(self):
        return glm.perspective(self._fov, self._aspect_ratio, self._near, self._far)
