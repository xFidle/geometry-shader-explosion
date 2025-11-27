#version 330

in vec3 in_position;
in vec3 in_normal;
in vec2 in_uv;

uniform mat4 projection_matrix;
uniform mat4 model_matrix;
uniform mat4 view_matrix;

out vec3 v_normal;
out vec2 v_uv;

void main()
{
    v_normal = mat3(model_matrix) * in_normal;
    v_uv = in_uv;
    gl_Position = projection_matrix * view_matrix * model_matrix * vec4(in_position, 1.0);
}
