#version 330 core

in frag_data {
    vec3 position;
    vec3 normal;
} frag;

out vec4 f_color;

struct Material {
    vec3 ambient;
    vec3 diffuse;
    vec3 specular;
    float shininess;
};

uniform vec3 camera_position;
uniform Material material;

struct Light {
    vec3 position;
    vec3 ambient;
    vec3 diffuse;
    vec3 specular;
};

Light light = Light(
        camera_position,
        vec3(0.2, 0.2, 0.2),
        vec3(1.0, 1.0, 1.0),
        vec3(0.2, 0.2, 0.2)
    );

void main()
{
    vec3 ambient = light.ambient * material.ambient;

    vec3 N = normalize(frag.normal);
    vec3 L = normalize(light.position - frag.position);
    vec3 V = normalize(camera_position - frag.position);
    vec3 R = reflect(-L, N);

    float cosNL = max(dot(N, L), 0.0);
    vec3 diffuse = light.diffuse * cosNL * material.diffuse;

    float cosVR = max(dot(V, R), 0.0);
    float spec = pow(cosVR, material.shininess);
    vec3 specular = light.specular * spec * material.specular;

    vec3 phong_color = clamp(ambient + diffuse + specular, 0.0, 1.0);
    f_color = vec4(phong_color, 1.0);
}
