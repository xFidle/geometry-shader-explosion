import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Self


@dataclass(frozen=True)
class WindowConfig:
    title: str
    size: tuple[int, int]
    fps: int


@dataclass(frozen=True)
class ShadersConfig:
    vertex: str
    geometry: str
    fragment: str


@dataclass(frozen=True)
class ModelsConfig:
    car: str
    car_format: str
    indicator: str
    indicator_format: str


@dataclass(frozen=True)
class CameraConfig:
    position: tuple[float, float, float]
    front: tuple[float, float, float]
    up: tuple[float, float, float]


@dataclass(frozen=True)
class SimulationConfig:
    time_multiplier: float
    magnitude: int
    stopped: bool
    explosion_origin: list[float]
    falloff_strength: float
    falloff_radius: float
    random_strength: float
    impulse_decay: float
    gravity_power: float


@dataclass(frozen=True)
class Config:
    window: WindowConfig
    shaders: ShadersConfig
    models: ModelsConfig
    camera: CameraConfig
    simulation: SimulationConfig

    @classmethod
    def from_file(cls, path: Path | None = None) -> Self:
        if path is None:
            path = Path(__file__).parent.parent / "config.toml"

        with open(path, "rb") as f:
            data = tomllib.load(f)

        return cls(
            window=WindowConfig(**data["window"]),
            shaders=ShadersConfig(**data["shaders"]),
            models=ModelsConfig(**data["models"]),
            camera=CameraConfig(**data["camera"]),
            simulation=SimulationConfig(**data["simulation"]),
        )
