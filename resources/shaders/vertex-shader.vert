#version 330 core

layout(location = 0) in vec3 in_position;
layout(location = 1) in vec3 in_normal;
layout(location = 2) in vec3 in_tex;

uniform mat4 projection_matrix;
uniform mat4 view_matrix;
uniform mat4 model_matrix;

out vertex_data {
   vec3 position;
   vec3 normal;
} vertex;

void main()
{
    vec4 worldPos = model_matrix * vec4(in_position, 1.0);

    vertex.position = worldPos.xyz;
    vertex.normal = mat3(transpose(inverse(model_matrix))) * in_normal;

    gl_Position = projection_matrix * view_matrix * worldPos;
}
