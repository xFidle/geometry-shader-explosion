import math
from OpenGL.GL import *


class Shader:
    def __init__(self, vertex_path, geometry_path, fragment_path):
        vertex = self._complie_shader(vertex_path, GL_VERTEX_SHADER)
        geometry = self._complie_shader(geometry_path, GL_GEOMETRY_SHADER)
        fragment = self._complie_shader(fragment_path, GL_FRAGMENT_SHADER)

        self._program = self._create_shader_program(vertex, geometry, fragment)

    @property
    def program(self):
        return self._program

    def _complie_shader(self, path, shader_type):
        if path is None:
            return None

        file_content = load_file(path)
        shader = glCreateShader(shader_type)
        glShaderSource(shader, file_content)
        glCompileShader(shader)

        if not glGetShaderiv(shader, GL_COMPILE_STATUS):
            error = glGetShaderInfoLog(shader).decode()
            raise RuntimeError(f"Shader compilation failed: {error}")

        return shader

    def _create_shader_program(self, vertex, geometry, fragment):
        program = glCreateProgram()
        glAttachShader(program, vertex)
        if geometry is not None:
            glAttachShader(program, geometry)
        glAttachShader(program, fragment)

        glLinkProgram(program)

        if not glGetProgramiv(program, GL_LINK_STATUS):
            error = glGetProgramInfoLog(program).decode()
            raise RuntimeError(f"Program linking failed: {error}")

        glDeleteShader(vertex)
        if geometry is not None:
            glDeleteShader(geometry)
        glDeleteShader(fragment)

        return program


def load_file(path):
    with open(path, "r") as fh:
        file_data = fh.read()
    return file_data
