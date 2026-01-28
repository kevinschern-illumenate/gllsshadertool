"""Uniform handling for shaders.

This module manages the standard uniforms passed to shaders:
- u_resolution: Viewport resolution (vec2)
- u_time: Time in seconds (float)
- u_phase: Loop phase 0..2π (float)
- u_frame: Current frame index (int)
- u_duration: Loop duration (float)
- u_seed: Random seed for reproducibility (float)
- u_loop: Loop vector cos/sin pair (vec2)
"""

from dataclasses import dataclass, field
from typing import Dict, Any


@dataclass
class StandardUniforms:
    """Standard uniforms for shader rendering.
    
    Attributes:
        resolution: Viewport resolution (width, height)
        time: Current time in seconds
        phase: Loop phase (0 to 2π)
        frame: Current frame index
        duration: Loop duration in seconds
        seed: Random seed for reproducibility
        loop: Loop vector (cos(phase), sin(phase))
        jitter: Subpixel jitter for accumulation AA (x, y in pixels)
    """
    
    resolution: tuple[float, float] = (1920.0, 1080.0)
    time: float = 0.0
    phase: float = 0.0
    frame: int = 0
    duration: float = 30.0
    seed: float = 0.0
    loop: tuple[float, float] = (1.0, 0.0)  # cos(0), sin(0)
    jitter: tuple[float, float] = (0.0, 0.0)  # Subpixel jitter for AA
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert uniforms to a dictionary for OpenGL binding."""
        return {
            "u_resolution": self.resolution,
            "u_time": self.time,
            "u_phase": self.phase,
            "u_frame": self.frame,
            "u_duration": self.duration,
            "u_seed": self.seed,
            "u_loop": self.loop,
            "u_jitter": self.jitter,
        }


@dataclass
class UserParameter:
    """User-defined shader parameter parsed from comments.
    
    Supported formats in shader:
    // @param name float 0.0 1.0 0.5
    // @param name vec3 0.0 0.0 0.0 1.0 1.0 1.0 0.5 0.5 0.5
    """
    
    name: str
    param_type: str  # "float", "vec2", "vec3", "vec4", "color"
    min_value: Any = None
    max_value: Any = None
    default_value: Any = None
    current_value: Any = None
    
    def __post_init__(self):
        if self.current_value is None:
            self.current_value = self.default_value


@dataclass
class UniformManager:
    """Manages all uniforms (standard + user-defined) for shaders."""
    
    standard: StandardUniforms = field(default_factory=StandardUniforms)
    user_params: Dict[str, UserParameter] = field(default_factory=dict)
    
    def set_resolution(self, width: float, height: float):
        """Update the resolution uniform."""
        self.standard.resolution = (width, height)
    
    def set_frame_info(self, time: float, phase: float, frame: int,
                       loop_x: float, loop_y: float):
        """Update time-related uniforms from timeline frame info."""
        self.standard.time = time
        self.standard.phase = phase
        self.standard.frame = frame
        self.standard.loop = (loop_x, loop_y)
    
    def set_seed(self, seed: float):
        """Update the random seed."""
        self.standard.seed = seed
    
    def set_jitter(self, jitter_x: float, jitter_y: float):
        """Set subpixel jitter for accumulation AA."""
        self.standard.jitter = (jitter_x, jitter_y)
    
    def add_user_param(self, param: UserParameter):
        """Add or update a user parameter."""
        self.user_params[param.name] = param
    
    def get_user_param_value(self, name: str) -> Any:
        """Get current value of a user parameter."""
        if name in self.user_params:
            return self.user_params[name].current_value
        return None
    
    def set_user_param_value(self, name: str, value: Any):
        """Set value of a user parameter."""
        if name in self.user_params:
            self.user_params[name].current_value = value
    
    def get_all_uniforms(self) -> Dict[str, Any]:
        """Get all uniforms as a dictionary for shader binding."""
        uniforms = self.standard.to_dict()
        for name, param in self.user_params.items():
            uniforms[f"u_{name}"] = param.current_value
        return uniforms
    
    def clear_user_params(self):
        """Clear all user-defined parameters."""
        self.user_params.clear()


def parse_param_comment(line: str) -> UserParameter | None:
    """Parse a @param comment from shader source.
    
    Format: // @param name type min max default
    Examples:
        // @param speed float 0.0 10.0 1.0
        // @param color color 1.0 0.5 0.0
        
    Args:
        line: A line from shader source
        
    Returns:
        UserParameter if valid, None otherwise
    """
    line = line.strip()
    if not line.startswith("// @param"):
        return None
    
    parts = line[len("// @param"):].strip().split()
    if len(parts) < 2:
        return None
    
    name = parts[0]
    param_type = parts[1].lower()
    
    try:
        if param_type == "float":
            if len(parts) >= 5:
                return UserParameter(
                    name=name,
                    param_type="float",
                    min_value=float(parts[2]),
                    max_value=float(parts[3]),
                    default_value=float(parts[4])
                )
            elif len(parts) >= 3:
                # Just a default value
                return UserParameter(
                    name=name,
                    param_type="float",
                    min_value=0.0,
                    max_value=1.0,
                    default_value=float(parts[2])
                )
        elif param_type == "color":
            if len(parts) >= 5:
                return UserParameter(
                    name=name,
                    param_type="color",
                    min_value=(0.0, 0.0, 0.0),
                    max_value=(1.0, 1.0, 1.0),
                    default_value=(float(parts[2]), float(parts[3]), float(parts[4]))
                )
        elif param_type in ("vec2", "vec3", "vec4"):
            # Parse vector types
            dim = int(param_type[-1])
            if len(parts) >= 2 + dim:
                values = [float(parts[2 + i]) for i in range(dim)]
                return UserParameter(
                    name=name,
                    param_type=param_type,
                    min_value=tuple([0.0] * dim),
                    max_value=tuple([1.0] * dim),
                    default_value=tuple(values)
                )
    except (ValueError, IndexError):
        return None
    
    return None


def parse_params_from_source(source: str) -> list[UserParameter]:
    """Parse all @param comments from shader source.
    
    Args:
        source: Complete shader source code
        
    Returns:
        List of UserParameter objects
    """
    params = []
    for line in source.split("\n"):
        param = parse_param_comment(line)
        if param:
            params.append(param)
    return params
