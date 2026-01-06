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

uniform float magnitude;
uniform float time;
uniform vec3 explosion_origin;
uniform float falloff_radius;
uniform float falloff_strength;
uniform float impulse_decay;
uniform float random_stregth;
uniform float gravity_power;

uniform mat4 projection_matrix;
uniform mat4 view_matrix;
uniform mat4 model_matrix;

float falloff(float len) {
    return pow(clamp(1.0 - len / falloff_radius, 0.0, 1.0), falloff_strength);
}

float impulse() {
    return pow(time, impulse_decay) * magnitude;
}

vec3 randomise_vec(vec3 direction) {
    vec3 rand_dir = noise3(vertex[0].position);
    return normalize(direction + rand_dir * random_stregth);

}

vec3 surface_normal() {
    vec3 a = vec3(vertex[0].position) - vec3(vertex[1].position);
    vec3 b = vec3(vertex[2].position) - vec3(vertex[1].position);
    return -normalize(cross(a, b));
}

vec3 surface_center() {
    return (
        vertex[0].position + vertex[1].position + vertex[2].position
    ) / 3;
}

vec3 gravity() {
    return vec3(0, -1, 0) * gravity_power * time * time;
}

vec3 explode(vec3 pos) {
    vec3 dir = surface_center() - explosion_origin;
    float dist = length(dir);
    dir = normalize(dir);

    return pos + randomise_vec(dir) * impulse() + gravity();
}

void main() {
    for (int i = 0; i < 3; i++) {
        vec3 exploded = explode(vertex[i].position);
        gl_Position = projection_matrix * view_matrix * model_matrix * vec4(exploded,1.0);
        frag.position = exploded;
        frag.normal = surface_normal();
        EmitVertex();
    }
    EndPrimitive();
}
