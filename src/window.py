import sys
from pathlib import Path

import pygame
from OpenGL.GL import *
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
        self.screen = pygame.display.set_mode(cfg.WINDOW_SIZE, display_flags)
        pygame.display.set_caption(cfg.WINDOW_TITLE)
        self.running = True
        self.clock = pygame.time.Clock()
        self.time = 0

    def _initialize(self):
        self.shader = Shader(
            cfg.VERT_SHADER,
            cfg.GEOM_SHADER,
            cfg.FRAG_SHADER,
        )

        self.camera = Camera(
            position=glm.vec3(*cfg.CAMERA_POSITION),
            target=glm.vec3(*cfg.CAMERA_TARGET),
            up=glm.vec3(*cfg.CAMERA_UP),
            aspect_ratio=cfg.WINDOW_SIZE[0] / cfg.WINDOW_SIZE[1],
        )

        self.scene = ObjectLoader(cfg.SCENE, cfg.SCENE_FORMAT)

        glEnable(GL_DEPTH_TEST)
        glDisable(GL_CULL_FACE)

    def _update(self):
        glClearColor(0.25, 0.25, 0.25, 1.0)
        glClear(GL_COLOR_BUFFER_BIT)
        glClear(GL_DEPTH_BUFFER_BIT)
        glUseProgram(self.shader.program)

        self.camera.upload_uniforms(self.shader.program)
        self.scene.upload_uniforms(self.shader.program)
        self.scene.render()

    def cleanup(self):
        glDeleteProgram(self.shader.program)
        self.scene.close()

    def run(self):
        self._initialize()

        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            self.delta_time = self.clock.get_time() / 1000
            self.time += self.delta_time
            self.update()

            pygame.display.flip()
            self.clock.tick(cfg.FPS)

        self.cleanup()
        pygame.quit()
        sys.exit()
