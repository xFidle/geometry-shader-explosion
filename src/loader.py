import numpy as np
import pywavefront
from OpenGL.GL import *
from pyglm import glm


class ObjectLoader:
    def __init__(self, filepath, format) -> None:
        self._scene = self._load_obj(filepath)
        self._format = self._parse_format(format)
        self._floats_per_vertex = sum(n_floats for _, n_floats, _ in self._format)
        self._vao, self._vbo, self._materials = self._create_buffers()

    def render(self, program):
        if self._vao is None or self._vbo is None:
            raise RuntimeError("object was already deleted")

        glBindVertexArray(self._vao)
        for material in self._materials:
            start, count = material.vbo_range
            self._upload_uniforms(program, material)
            glDrawArrays(GL_TRIANGLES, start, count)
        glBindVertexArray(0)

    def close(self):
        if self._vbo is not None:
            glDeleteBuffers(1, [self._vbo])

        if self._vao is not None:
            glDeleteVertexArrays(1, [self._vao])

        self._vao = None
        self._vbo = None

    class Material:
        def __init__(self, name, ambient, diffuse, specular, shininess, vbo_range):
            self.name = name
            self.ambient = ambient
            self.diffuse = diffuse
            self.specular = specular
            self.shininess = shininess
            self.vbo_range = vbo_range

    def _load_obj(self, filepath):
        scene = pywavefront.Wavefront(
            filepath, collect_faces=True, create_materials=True
        )
        return scene

    def _parse_format(self, format):
        result = []
        splitted = format.split("_")
        for i, part in enumerate(splitted):
            primitive = part[0]
            n_floats = int(part[1])
            offset = sum(int(splitted[j][1]) for j in range(i))
            result.append((primitive, n_floats, offset))

        return result

    def _create_buffers(self):
        all_vertices = []
        materials = []
        current_offset = 0

        for name, material in self._scene.materials.items():
            vertices = np.array(material.vertices, dtype=np.float32)
            all_vertices.append(vertices)
            vertex_count = len(vertices) // (self._floats_per_vertex)

            materials.append(
                self.Material(
                    name,
                    glm.vec3(material.ambient[:-1]),
                    glm.vec3(material.diffuse[:-1]),
                    glm.vec3(material.specular[:-1]),
                    material.shininess,
                    (current_offset, vertex_count),
                )
            )

            current_offset += vertex_count

        vertices = np.concatenate(all_vertices)

        vao = glGenVertexArrays(1)
        vbo = glGenBuffers(1)

        glBindVertexArray(vao)
        glBindBuffer(GL_ARRAY_BUFFER, vbo)
        glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)

        stride = 4 * (self._floats_per_vertex)

        matches = {"V": 0, "N": 1, "T": 2}
        for part in self._format:
            name, n_floats, offset = part
            glVertexAttribPointer(
                matches[name],
                n_floats,
                GL_FLOAT,
                GL_FALSE,
                stride,
                ctypes.c_void_p(4 * offset),
            )
            glEnableVertexAttribArray(matches[name])

        glBindVertexArray(0)

        return vao, vbo, materials

    def _upload_uniforms(self, program, material):
        ambient_loc = glGetUniformLocation(program, "material.ambient")
        diffuse_loc = glGetUniformLocation(program, "material.diffuse")
        specular_loc = glGetUniformLocation(program, "material.specular")
        shininess_loc = glGetUniformLocation(program, "material.shininess")

        glUniform3fv(ambient_loc, 1, glm.value_ptr(material.ambient))
        glUniform3fv(diffuse_loc, 1, glm.value_ptr(material.diffuse))
        glUniform3fv(specular_loc, 1, glm.value_ptr(material.specular))
        glUniform1f(shininess_loc, material.shininess)
