import random
import sys
import tkinter as tk
from tkinter import filedialog

import imgui
import imgui.integrations.pygame
import pygame
from OpenGL.GL import *
from pygame.event import Event
from pyglm import glm

from camera import Camera
from config import Config
from loader import ObjectLoader
from shaders import Shader


class Window:
    def __init__(self):
        self._config = Config.from_file()

        pygame.init()
        display_flags = pygame.DOUBLEBUF | pygame.OPENGL
        pygame.display.gl_set_attribute(pygame.GL_MULTISAMPLEBUFFERS, 1)
        pygame.display.gl_set_attribute(pygame.GL_MULTISAMPLESAMPLES, 4)
        pygame.display.gl_set_attribute(
            pygame.GL_CONTEXT_PROFILE_MASK, pygame.GL_CONTEXT_PROFILE_CORE
        )
        pygame.display.set_caption(self._config.window.title)
        self._screen = pygame.display.set_mode(self._config.window.size, display_flags)
        self._clock = pygame.time.Clock()
        self._running = True
        self._time = 0
        self._seed = random.random() * 100
        self._stopped = self._config.simulation.stopped

        self._initalize_shader()
        self._initialize_camera()
        self._initialize_simulation_params()
        self._initalize_objects()
        self._initialize_ui()

    def run(self):
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_CULL_FACE)
        pygame.event.set_grab(True)
        while self._running:
            events = pygame.event.get()
            mouse_rel = pygame.mouse.get_rel()

            self._handle_input(events, mouse_rel)

            self._delta_time = self._clock.get_time() / 1000
            if not self._stopped:
                self._time = max(0, self._time + self._delta_time * self._time_mult)

            self._update()
            self._render_ui()

            pygame.display.flip()
            self._clock.tick(self._config.window.fps)

        self._cleanup()
        pygame.quit()
        sys.exit()

    def _initalize_shader(self):
        self._shader = Shader(
            self._config.shaders.vertex,
            self._config.shaders.geometry,
            self._config.shaders.fragment,
        )

    def _initialize_camera(self):
        self._camera = Camera(
            position=glm.vec3(*self._config.camera.position),
            front=glm.vec3(*self._config.camera.front),
            up=glm.vec3(*self._config.camera.up),
            aspect_ratio=self._config.window.size[0] / self._config.window.size[1],
        )

    def _initialize_simulation_params(self):
        self._time_mult = self._config.simulation.time_multiplier
        self._magnitude = self._config.simulation.magnitude
        self._explosion_origin = self._config.simulation.explosion_origin.copy()
        self._falloff_strength = self._config.simulation.falloff_strength
        self._falloff_radius = self._config.simulation.falloff_radius
        self._random_strength = self._config.simulation.random_strength
        self._impulse_decay = self._config.simulation.impulse_decay
        self._gravity_power = self._config.simulation.gravity_power

        self._new_magnitude = self._config.simulation.magnitude
        self._new_explosion_origin = self._config.simulation.explosion_origin.copy()
        self._new_falloff_strength = self._config.simulation.falloff_strength
        self._new_falloff_radius = self._config.simulation.falloff_radius
        self._new_random_strength = self._config.simulation.random_strength
        self._new_impulse_decay = self._config.simulation.impulse_decay
        self._new_gravity_power = self._config.simulation.gravity_power
        self._new_model_path = self._config.models.car
        self._new_model_format = self._config.models.car_format

    def _initalize_objects(self):
        self._model = ObjectLoader(
            self._config.models.car, self._config.models.car_format
        )
        self._model_matrix = glm.mat4(1.0)

        self._indicator = ObjectLoader(
            self._config.models.indicator, self._config.models.indicator_format
        )
        self._indicator_model_matrix = glm.translate(
            glm.mat4(1.0), glm.vec3(*self._explosion_origin)
        )

    def _initialize_ui(self):
        imgui.create_context()
        imgui.get_io().display_size = self._config.window.size
        imgui.get_io().fonts.get_tex_data_as_rgba32()
        self._ui_renderer = imgui.integrations.pygame.PygameRenderer()

    def _reset_simulation(self):
        self._time = 0
        self._magnitude = self._new_magnitude
        self._falloff_strength = self._new_falloff_strength
        self._falloff_radius = self._new_falloff_radius
        self._random_strength = self._new_random_strength
        self._impulse_decay = self._new_impulse_decay
        self._gravity_power = self._new_gravity_power

        self._indicator_model_matrix = glm.translate(
            self._indicator_model_matrix,
            glm.vec3(self._new_explosion_origin) - glm.vec3(self._explosion_origin),
        )

        self._explosion_origin = self._new_explosion_origin

        self._model = ObjectLoader(self._new_model_path, self._new_model_format)
        self._model_matrx = glm.mat4(1.0)

    def _render_ui(self):
        glUseProgram(0)
        glBindVertexArray(0)
        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glEnable(GL_CULL_FACE)

        imgui.new_frame()

        imgui.begin("Controls")

        if self._stopped:
            if imgui.button("Resume"):
                self._stopped = False
        else:
            if imgui.button("Stop"):
                self._stopped = True

        _, self._time_mult = imgui.input_double(
            "Time multipler", self._time_mult, 0.1, format="%.3f"
        )

        if imgui.button("Reset"):
            self._reset_simulation()

        imgui.same_line()

        if imgui.button("Reset & reseed"):
            self._seed = random.random() * 100
            self._reset_simulation()

        imgui.text("Settings below take effect after reset")

        if imgui.button("Choose model"):
            root = tk.Tk()
            root.withdraw()
            self._new_model_path = filedialog.askopenfilename()

        imgui.same_line()
        imgui.text(f"Path: {self._new_model_path}")

        imgui.same_line()
        _, self._new_model_format = imgui.input_text(
            "OBJ Format", self._new_model_format
        )

        _, self._new_explosion_origin = imgui.input_float3(
            "Explosion origin",
            *self._new_explosion_origin,
            format="%.3f",
        )
        _, self._new_magnitude = imgui.input_double(
            "Magnitude", self._new_magnitude, 0.1, format="%.3f"
        )
        _, self._new_falloff_strength = imgui.input_double(
            "Falloff strength", self._new_falloff_strength, 0.1, format="%.3f"
        )
        _, self._new_falloff_radius = imgui.input_double(
            "Falloff radius", self._new_falloff_radius, 0.1, format="%.3f"
        )
        _, self._new_random_strength = imgui.input_double(
            "Random strength", self._new_random_strength, 0.1, format="%.3f"
        )
        _, self._new_impulse_decay = imgui.input_double(
            "Impulse decay", self._new_impulse_decay, 0.1, format="%.3f"
        )
        _, self._new_gravity_power = imgui.input_double(
            "Gravity power", self._new_gravity_power, 0.1, format="%.3f"
        )

        imgui.end()

        imgui.render()
        self._ui_renderer.render(imgui.get_draw_data())

    def _update(self):
        glClearColor(0.25, 0.25, 0.25, 1.0)
        glClear(GL_COLOR_BUFFER_BIT)
        glClear(GL_DEPTH_BUFFER_BIT)
        glUseProgram(self._shader.program)

        should_explode = glGetUniformLocation(self._shader.program, "should_explode")
        time = glGetUniformLocation(self._shader.program, "time")
        magnitude = glGetUniformLocation(self._shader.program, "magnitude")
        explosion_origin = glGetUniformLocation(
            self._shader.program, "explosion_origin"
        )
        falloff_radius = glGetUniformLocation(self._shader.program, "falloff_radius")
        falloff_strength = glGetUniformLocation(
            self._shader.program, "falloff_strength"
        )
        random_strength = glGetUniformLocation(self._shader.program, "random_strength")
        impulse_decay = glGetUniformLocation(self._shader.program, "impulse_decay")
        gravity_power = glGetUniformLocation(self._shader.program, "gravity_power")
        seed = glGetUniformLocation(self._shader.program, "seed")

        glUniform1f(time, self._time)
        glUniform1f(magnitude, self._magnitude)
        glUniform3f(
            explosion_origin,
            self._explosion_origin[0],
            self._explosion_origin[1],
            self._explosion_origin[2],
        )
        glUniform1f(falloff_radius, self._falloff_radius)
        glUniform1f(falloff_strength, self._falloff_strength)
        glUniform1f(random_strength, self._random_strength)
        glUniform1f(impulse_decay, 1 - self._impulse_decay)
        glUniform1f(gravity_power, self._gravity_power)
        glUniform1f(seed, self._seed)

        self._camera.upload_uniforms(self._shader.program)

        glUniform1i(should_explode, 1)
        self._model.render(self._shader.program, self._model_matrix)

        glUniform1i(should_explode, 0)
        self._indicator.render(self._shader.program, self._indicator_model_matrix)

    def _handle_input(self, events: list[Event], mouse_rel: tuple[int, int]):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self._running = False

            if event.type == pygame.QUIT:
                self._running = False

            self._ui_renderer.process_event(event)
        self._ui_renderer.process_inputs()

        if not imgui.get_io().want_capture_keyboard:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_w]:
                self._camera.move_forward(self._delta_time)
            if keys[pygame.K_s]:
                self._camera.move_backward(self._delta_time)
            if keys[pygame.K_a]:
                self._camera.move_left(self._delta_time)
            if keys[pygame.K_d]:
                self._camera.move_right(self._delta_time)

        if not imgui.get_io().want_capture_mouse:
            mouse_buttons = pygame.mouse.get_pressed()
            if mouse_buttons[0]:
                dx, dy = mouse_rel
                self._camera.mouse_callback(dx, dy)

    def _cleanup(self):
        glDeleteProgram(self._shader.program)
        self._model.close()
        self._indicator.close()
