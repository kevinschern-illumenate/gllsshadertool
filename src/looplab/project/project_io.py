"""Project I/O utilities for save/load operations.

This module provides functions for saving and loading LoopLab projects.
The actual Project class is in app.models - this module provides
additional utilities.
"""

from pathlib import Path
from typing import Optional
import json

from ..app.models import Project, save_project, load_project


def get_project_extension() -> str:
    """Get the project file extension."""
    return ".llp"


def is_project_file(path: str) -> bool:
    """Check if a path is a LoopLab project file.
    
    Args:
        path: File path to check
        
    Returns:
        True if the file has the project extension
    """
    return Path(path).suffix.lower() == get_project_extension()


def get_recent_projects_path() -> Path:
    """Get path to recent projects file.
    
    Returns:
        Path to the recent projects JSON file
    """
    # Use platform-appropriate location
    import os
    
    if os.name == 'nt':  # Windows
        base = Path(os.environ.get('APPDATA', '~'))
    else:  # macOS/Linux
        base = Path.home() / '.config'
    
    return base / 'looplab' / 'recent_projects.json'


def save_recent_projects(paths: list[str]) -> bool:
    """Save list of recent project paths.
    
    Args:
        paths: List of project file paths
        
    Returns:
        True if successful
    """
    try:
        recent_path = get_recent_projects_path()
        recent_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(recent_path, 'w') as f:
            json.dump({"recent": paths[:10]}, f)  # Keep max 10
        
        return True
    except Exception:
        return False


def load_recent_projects() -> list[str]:
    """Load list of recent project paths.
    
    Returns:
        List of project file paths (may be empty)
    """
    try:
        recent_path = get_recent_projects_path()
        if not recent_path.exists():
            return []
        
        with open(recent_path, 'r') as f:
            data = json.load(f)
        
        # Filter to existing files
        paths = data.get("recent", [])
        return [p for p in paths if Path(p).exists()]
    except Exception:
        return []


def add_to_recent_projects(path: str):
    """Add a project path to the recent list.
    
    Args:
        path: Project file path to add
    """
    recent = load_recent_projects()
    
    # Remove if already in list
    if path in recent:
        recent.remove(path)
    
    # Add to front
    recent.insert(0, path)
    
    # Save
    save_recent_projects(recent)


def export_project_to_folder(project: Project, folder: str) -> bool:
    """Export project and shader to a folder.
    
    Creates a self-contained folder with the project file
    and a copy of the shader source.
    
    Args:
        project: Project to export
        folder: Target folder path
        
    Returns:
        True if successful
    """
    try:
        folder_path = Path(folder)
        folder_path.mkdir(parents=True, exist_ok=True)
        
        # Copy shader source
        if project.shader_path:
            shader_source = Path(project.shader_path)
            if shader_source.exists():
                dest_shader = folder_path / shader_source.name
                dest_shader.write_text(shader_source.read_text())
                
                # Update project to use relative path
                project.shader_path = shader_source.name
        
        # Save project
        project_path = folder_path / "project.llp"
        return save_project(project, project_path)
        
    except Exception:
        return False
