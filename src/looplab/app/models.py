"""Project model and settings management."""

import json
import random
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Optional, Any


@dataclass
class PreviewSettings:
    """Settings for the preview window."""
    
    render_scale: float = 1.0  # 0.25 to 1.0
    supersampling: bool = False
    target_fps: float = 30.0


@dataclass
class OfflineSettings:
    """Settings for offline rendering."""
    
    width: int = 1920
    height: int = 1080
    fps: float = 30.0
    supersample_scale: int = 1  # 1, 2, or 4
    accumulation_samples: int = 1  # 1 to N samples per frame
    save_png_sequence: bool = True
    encode_video: bool = True


@dataclass
class ExportSettings:
    """Settings for video export."""
    
    output_directory: str = ""
    codec: str = "h264"  # h264, h265, prores
    quality: str = "high"  # low, medium, high
    

@dataclass
class ParameterValue:
    """Stored value for a user parameter."""
    
    name: str
    param_type: str
    value: Any


@dataclass
class Project:
    """Complete project model storing all settings and state.
    
    This is the root data structure that gets saved/loaded as JSON.
    """
    
    # Shader source
    shader_path: str = ""
    shader_source: str = ""  # Embedded shader (optional)
    
    # Timeline
    duration: float = 30.0
    current_time: float = 0.0
    
    # Random seed for reproducibility
    seed: float = 0.0
    
    # Settings
    preview: PreviewSettings = field(default_factory=PreviewSettings)
    offline: OfflineSettings = field(default_factory=OfflineSettings)
    export: ExportSettings = field(default_factory=ExportSettings)
    
    # User parameters from shader
    parameters: list[ParameterValue] = field(default_factory=list)
    
    def generate_new_seed(self):
        """Generate a new random seed."""
        self.seed = random.random() * 1000.0
    
    def get_parameter_value(self, name: str) -> Any:
        """Get the value of a parameter by name."""
        for param in self.parameters:
            if param.name == name:
                return param.value
        return None
    
    def set_parameter_value(self, name: str, value: Any):
        """Set the value of a parameter by name."""
        for param in self.parameters:
            if param.name == name:
                param.value = value
                return
        # Add new parameter if not found
        self.parameters.append(ParameterValue(name=name, param_type="float", value=value))
    
    def to_dict(self) -> dict:
        """Convert project to a serializable dictionary."""
        return {
            "shader_path": self.shader_path,
            "shader_source": self.shader_source,
            "duration": self.duration,
            "current_time": self.current_time,
            "seed": self.seed,
            "preview": asdict(self.preview),
            "offline": asdict(self.offline),
            "export": asdict(self.export),
            "parameters": [asdict(p) for p in self.parameters],
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Project":
        """Create a project from a dictionary."""
        project = cls()
        
        project.shader_path = data.get("shader_path", "")
        project.shader_source = data.get("shader_source", "")
        project.duration = data.get("duration", 30.0)
        project.current_time = data.get("current_time", 0.0)
        project.seed = data.get("seed", 0.0)
        
        if "preview" in data:
            project.preview = PreviewSettings(**data["preview"])
        if "offline" in data:
            project.offline = OfflineSettings(**data["offline"])
        if "export" in data:
            project.export = ExportSettings(**data["export"])
        
        if "parameters" in data:
            project.parameters = [
                ParameterValue(**p) for p in data["parameters"]
            ]
        
        return project


def save_project(project: Project, path: str | Path) -> bool:
    """Save a project to a JSON file.
    
    Args:
        project: The project to save
        path: Output file path
        
    Returns:
        True if successful, False otherwise
    """
    try:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(path, 'w') as f:
            json.dump(project.to_dict(), f, indent=2)
        
        return True
    except Exception:
        return False


def load_project(path: str | Path) -> Optional[Project]:
    """Load a project from a JSON file.
    
    Args:
        path: Input file path
        
    Returns:
        Project if successful, None otherwise
    """
    try:
        path = Path(path)
        if not path.exists():
            return None
        
        with open(path, 'r') as f:
            data = json.load(f)
        
        return Project.from_dict(data)
    except Exception:
        return None
