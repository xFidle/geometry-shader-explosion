#version 330 core

layout(triangles) in;
layout(triangle_strip, max_vertices = 3) out;

in vertex_data {
    vec3 position;
    vec3 normal;
} vertex[];

out frag_data {
    vec3 position;
    vec3 normal;
} frag;


void main() {
    for (int i = 0; i < 3; i++) {
        gl_Position = gl_in[i].gl_Position;
        frag.position = vertex[i].position;
        frag.normal = vertex[i].normal;
        EmitVertex();
    }
    EndPrimitive();
}
