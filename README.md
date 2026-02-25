# Geometry Shader Explosion

## Overview
An interactive OpenGL demonstration of real-time 3D model explosion effects
achieved using a geometry shader. The shader subdivides each triangle of the
model into smaller ones, creating hundreds of individual primitives that
scatter throughout 3D space. The simulation is highly customizable, with 
many effects that can be used to achieve the desired effect.

## Demo


## Installation
This project uses [`uv`](https://github.com/astral-sh/uv) - dependencies are pinned in *uv.lock*.

Install dependencies:
```bash
uv sync
```

Run the application:
```
uv run python src/main.py
```

## Controls

| Key | Action |
|-----|--------|
| W/S/A/D | Move camera |
| Mouse | Look around |
| ESC | Quit |
| UI panel | Adjust explosion parameters |

## Configuration
All program parameters can be customized in `config.toml` at the project
root. This includes window settings, initial camera position, default explosion
values and model paths.

For example, to set up the window, adjust these options:
```toml
[window]
title = "Geometry Shader Explosion"
size = [1600, 1000]
fps = 60
```


## Explosion Parameters
Many of the parameters defined initially in `config.toml` can be adjusted
dynamically while the program is running. Some changes require resetting
the simulation to take effect.

Available parameters control the following aspects of the simulation:
- **3D Model** - OBJ file used as source mesh for the explosion (ensure the
 file format is specified correctly; for examples, see `config.toml`)
- **Time Multiplier** - simulation speed; values greater than 1.0 accelerate time
while negative values play the simulation in reverse
- **Explosion Origin** - XYZ coordinates in world space defining explosion origin
- **Magnitude** - initial explosion force
- **Falloff Radius** - maximum distance affected by explosion
- **Falloff Strength** - exponent controlling how quickly force decreases with distance
- **Random Strength** - strength of random direction scatter
- **Impulse Decay** - exponent defining how momentum changes over time
- **Gravity Power** - downward acceleration applied to all primitives

To better understand how each parameter affects the explosion, see the geometry shader logic:
```glsl
float falloff(float len) {
    return pow(clamp(1.0 - len / falloff_radius, 0.0, 1.0), falloff_strength);
}

float impulse() {
    return pow(time, impulse_decay) * magnitude;
}

vec3 gravity() {
    return vec3(0, -1, 0) * gravity_power * time * time;
}

vec3 explode(vec3 pos) {
    vec3 dir = surface_center() - explosion_origin;
    float dist = length(dir);
    dir = normalize(dir);
    return pos + randomise_vec(dir) * impulse() * falloff(dist) + gravity();
}
```
