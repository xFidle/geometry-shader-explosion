import sys

import imgui
import imgui.integrations.opengl
import imgui.integrations.pygame
import pygame
from OpenGL.GL import *
from pygame.event import Event
from pyglm import glm

import config as cfg
from camera import Camera
from loader import ObjectLoader
from shaders import Shader


class Window:
    def __init__(self):
        pygame.init()
        display_flags = pygame.DOUBLEBUF | pygame.OPENGL
        pygame.display.gl_set_attribute(pygame.GL_MULTISAMPLEBUFFERS, 1)
        pygame.display.gl_set_attribute(pygame.GL_MULTISAMPLESAMPLES, 4)
        pygame.display.gl_set_attribute(
            pygame.GL_CONTEXT_PROFILE_MASK, pygame.GL_CONTEXT_PROFILE_CORE
        )
        self._screen = pygame.display.set_mode(cfg.WINDOW_SIZE, display_flags)
        pygame.display.set_caption(cfg.WINDOW_TITLE)
        self._running = True
        self._clock = pygame.time.Clock()
        self._time = 0
        self._time_mult = 1.0
        self._magnitude = 2
        self._stopped = False
        self._explosion_origin = [0, 0, 0]
        self._falloff_strength = 3.0
        self._falloff_radius = 1.0
        self._random_stregth = 0.01
        self._impulse_decay = .20
        self._gravity_power = .25

        self._init_ui()

    def _init_ui(self):
        imgui.create_context()
        imgui.get_io().display_size = cfg.WINDOW_SIZE
        imgui.get_io().fonts.get_tex_data_as_rgba32()
        self._ui_renderer = imgui.integrations.pygame.PygameRenderer()

    def _render_ui(self):
        glUseProgram(0)
        glBindVertexArray(0)
        glBindBuffer(GL_ARRAY_BUFFER, 0)
        # glDisable(GL_CULL_FACE)
        # glDisable(GL_DEPTH_TEST)

        imgui.new_frame()

        imgui.begin("Controls")

        if self._stopped:
            if imgui.button("Resume"):
                self._stopped = False
        else:
            if imgui.button("Stop"):
                self._stopped = True

        if imgui.button("Reset"):
            self._time = 0

        _, self._time_mult = imgui.input_double(
            "Time multipler", self._time_mult, 0.1, format="%.3f"
        )

        imgui.end()

        imgui.render()
        self._ui_renderer.render(imgui.get_draw_data())

    def run(self):
        self._initialize()

        while self._running:
            events = pygame.event.get()
            mouse_rel = pygame.mouse.get_rel()

            self._handle_input(events, mouse_rel)

            self._delta_time = self._clock.get_time() / 1000
            if not self._stopped:
                self._time += self._delta_time * self._time_mult

            self._update()
            self._render_ui()

            pygame.display.flip()
            self._clock.tick(cfg.FPS)

        self.cleanup()
        pygame.quit()
        sys.exit()

    def cleanup(self):
        glDeleteProgram(self._shader.program)
        self._scene.close()

    def _initialize(self):
        self._shader = Shader(
            cfg.VERT_SHADER,
            cfg.GEOM_SHADER,
            cfg.FRAG_SHADER,
        )

        self._camera = Camera(
            position=glm.vec3(*cfg.CAMERA_POSITION),
            front=glm.vec3(*cfg.CAMERA_FRONT),
            up=glm.vec3(*cfg.CAMERA_UP),
            aspect_ratio=cfg.WINDOW_SIZE[0] / cfg.WINDOW_SIZE[1],
        )

        self._scene = ObjectLoader(cfg.SCENE, cfg.SCENE_FORMAT)

        glEnable(GL_DEPTH_TEST)
        glDisable(GL_CULL_FACE)
        pygame.event.set_grab(True)

    def _update(self):
        # glDisable(GL_CULL_FACE)
        # glEnable(GL_DEPTH_TEST)
        # glFrontFace(GL_CCW)

        glClearColor(0.25, 0.25, 0.25, 1.0)
        glClear(GL_COLOR_BUFFER_BIT)
        glClear(GL_DEPTH_BUFFER_BIT)
        glUseProgram(self._shader.program)

        time = glGetUniformLocation(self._shader.program, "time")
        magnitude = glGetUniformLocation(self._shader.program, "magnitude")
        explosion_origin = glGetUniformLocation(
            self._shader.program, "explosion_origin"
        )
        falloff_radius = glGetUniformLocation(self._shader.program, "falloff_radius")
        falloff_strength = glGetUniformLocation(
            self._shader.program, "falloff_strength"
        )
        random_stregth = glGetUniformLocation(self._shader.program, "random_stregth")
        impulse_decay = glGetUniformLocation(self._shader.program, "impulse_decay")
        gravity_power = glGetUniformLocation(self._shader.program, "gravity_power")

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
        glUniform1f(random_stregth, self._random_stregth)
        glUniform1f(impulse_decay, 1 - self._impulse_decay)
        glUniform1f(gravity_power, self._gravity_power)

        self._camera.upload_uniforms(self._shader.program)
        self._scene.render(self._shader.program)

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
