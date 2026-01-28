"""Project schema definitions.

This module defines the schema and validation for LoopLab projects.
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional


# Current schema version
SCHEMA_VERSION = "1.0"


def validate_project_data(data: Dict[str, Any]) -> tuple[bool, str]:
    """Validate project data dictionary.
    
    Args:
        data: Dictionary to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    # Check required fields
    required_fields = ["shader_path", "duration", "seed"]
    for field in required_fields:
        if field not in data:
            return False, f"Missing required field: {field}"
    
    # Validate duration
    duration = data.get("duration")
    if not isinstance(duration, (int, float)) or duration <= 0:
        return False, "Invalid duration value"
    
    # Validate seed
    seed = data.get("seed")
    if not isinstance(seed, (int, float)):
        return False, "Invalid seed value"
    
    # Validate preview settings if present
    if "preview" in data:
        preview = data["preview"]
        if not isinstance(preview, dict):
            return False, "Invalid preview settings"
        
        if "render_scale" in preview:
            scale = preview["render_scale"]
            if not isinstance(scale, (int, float)) or scale <= 0 or scale > 1:
                return False, "Invalid render_scale (must be 0-1)"
    
    # Validate offline settings if present
    if "offline" in data:
        offline = data["offline"]
        if not isinstance(offline, dict):
            return False, "Invalid offline settings"
        
        if "width" in offline:
            width = offline["width"]
            if not isinstance(width, int) or width <= 0:
                return False, "Invalid width"
        
        if "height" in offline:
            height = offline["height"]
            if not isinstance(height, int) or height <= 0:
                return False, "Invalid height"
        
        if "fps" in offline:
            fps = offline["fps"]
            if not isinstance(fps, (int, float)) or fps <= 0:
                return False, "Invalid fps"
    
    return True, ""


def migrate_project_data(data: Dict[str, Any], from_version: str) -> Dict[str, Any]:
    """Migrate project data from an older schema version.
    
    Args:
        data: Project data dictionary
        from_version: Source schema version
        
    Returns:
        Migrated data dictionary
    """
    # For now, no migrations needed
    data["schema_version"] = SCHEMA_VERSION
    return data


def get_default_project_data() -> Dict[str, Any]:
    """Get default project data structure.
    
    Returns:
        Dictionary with default values
    """
    return {
        "schema_version": SCHEMA_VERSION,
        "shader_path": "",
        "shader_source": "",
        "duration": 30.0,
        "current_time": 0.0,
        "seed": 0.0,
        "preview": {
            "render_scale": 1.0,
            "supersampling": False,
            "target_fps": 30.0,
        },
        "offline": {
            "width": 1920,
            "height": 1080,
            "fps": 30.0,
            "supersample_scale": 1,
            "accumulation_samples": 1,
            "save_png_sequence": True,
            "encode_video": True,
        },
        "export": {
            "output_directory": "",
            "codec": "h264",
            "quality": "high",
        },
        "parameters": [],
    }
