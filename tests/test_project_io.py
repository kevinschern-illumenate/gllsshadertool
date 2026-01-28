"""Tests for project I/O and models."""

import json
import tempfile
from pathlib import Path
import pytest

# Import modules under test
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from looplab.app.models import (
    Project, PreviewSettings, OfflineSettings, ExportSettings,
    ParameterValue, save_project, load_project
)
from looplab.project.schema import (
    validate_project_data, get_default_project_data, SCHEMA_VERSION
)


class TestProject:
    """Tests for Project class."""
    
    def test_default_values(self):
        """Test default project values."""
        project = Project()
        
        assert project.shader_path == ""
        assert project.duration == 30.0
        assert project.seed == 0.0
        assert project.current_time == 0.0
    
    def test_generate_new_seed(self):
        """Test seed generation."""
        project = Project()
        old_seed = project.seed
        
        project.generate_new_seed()
        
        # Seed should change (extremely unlikely to be same)
        assert project.seed != old_seed
        assert 0 <= project.seed <= 1000.0
    
    def test_parameter_value_storage(self):
        """Test parameter value get/set."""
        project = Project()
        
        # Set a parameter
        project.set_parameter_value("speed", 2.5)
        
        # Get it back
        assert project.get_parameter_value("speed") == 2.5
        
        # Update it
        project.set_parameter_value("speed", 5.0)
        assert project.get_parameter_value("speed") == 5.0
    
    def test_to_dict(self):
        """Test conversion to dictionary."""
        project = Project()
        project.shader_path = "/path/to/shader.glsl"
        project.seed = 42.0
        project.duration = 30.0
        
        data = project.to_dict()
        
        assert data["shader_path"] == "/path/to/shader.glsl"
        assert data["seed"] == 42.0
        assert data["duration"] == 30.0
        assert "preview" in data
        assert "offline" in data
        assert "export" in data
    
    def test_from_dict(self):
        """Test creation from dictionary."""
        data = {
            "shader_path": "/path/to/shader.glsl",
            "shader_source": "",
            "duration": 30.0,
            "current_time": 5.0,
            "seed": 123.456,
            "preview": {
                "render_scale": 0.5,
                "supersampling": True,
                "target_fps": 60.0
            },
            "offline": {
                "width": 3840,
                "height": 2160,
                "fps": 60.0,
                "supersample_scale": 2,
                "accumulation_samples": 4,
                "save_png_sequence": True,
                "encode_video": True
            },
            "export": {
                "output_directory": "/output",
                "codec": "h265",
                "quality": "high"
            },
            "parameters": [
                {"name": "speed", "param_type": "float", "value": 2.0}
            ]
        }
        
        project = Project.from_dict(data)
        
        assert project.shader_path == "/path/to/shader.glsl"
        assert project.seed == 123.456
        assert project.current_time == 5.0
        assert project.preview.render_scale == 0.5
        assert project.offline.width == 3840
        assert project.export.codec == "h265"
        assert len(project.parameters) == 1
        assert project.parameters[0].name == "speed"


class TestProjectSaveLoad:
    """Tests for project save/load functionality."""
    
    def test_save_and_load_roundtrip(self):
        """Test saving and loading a project."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir) / "test_project.llp"
            
            # Create project
            project = Project()
            project.shader_path = "/path/to/shader.glsl"
            project.seed = 42.0
            project.set_parameter_value("speed", 2.5)
            
            # Save
            assert save_project(project, project_path) is True
            assert project_path.exists()
            
            # Load
            loaded = load_project(project_path)
            
            assert loaded is not None
            assert loaded.shader_path == project.shader_path
            assert loaded.seed == project.seed
            assert loaded.get_parameter_value("speed") == 2.5
    
    def test_save_creates_directory(self):
        """Test that save creates parent directories."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir) / "subdir" / "nested" / "project.llp"
            
            project = Project()
            assert save_project(project, project_path) is True
            assert project_path.exists()
    
    def test_load_nonexistent_file(self):
        """Test loading a file that doesn't exist."""
        result = load_project("/nonexistent/path/project.llp")
        assert result is None
    
    def test_save_load_preserves_settings(self):
        """Test that all settings are preserved through save/load."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir) / "test.llp"
            
            project = Project()
            project.preview.render_scale = 0.5
            project.preview.supersampling = True
            project.offline.width = 3840
            project.offline.height = 2160
            project.offline.supersample_scale = 4
            project.export.codec = "prores"
            
            save_project(project, project_path)
            loaded = load_project(project_path)
            
            assert loaded.preview.render_scale == 0.5
            assert loaded.preview.supersampling is True
            assert loaded.offline.width == 3840
            assert loaded.offline.height == 2160
            assert loaded.offline.supersample_scale == 4
            assert loaded.export.codec == "prores"


class TestProjectSchema:
    """Tests for project schema validation."""
    
    def test_validate_valid_data(self):
        """Test validation of valid project data."""
        data = get_default_project_data()
        is_valid, error = validate_project_data(data)
        assert is_valid is True
        assert error == ""
    
    def test_validate_missing_required_field(self):
        """Test validation catches missing required fields."""
        data = {"shader_path": "test.glsl"}  # Missing duration, seed
        is_valid, error = validate_project_data(data)
        assert is_valid is False
        assert "Missing required field" in error
    
    def test_validate_invalid_duration(self):
        """Test validation catches invalid duration."""
        data = get_default_project_data()
        data["duration"] = -5.0
        
        is_valid, error = validate_project_data(data)
        assert is_valid is False
        assert "duration" in error.lower()
    
    def test_validate_invalid_render_scale(self):
        """Test validation catches invalid render_scale."""
        data = get_default_project_data()
        data["preview"]["render_scale"] = 2.0  # Must be <= 1
        
        is_valid, error = validate_project_data(data)
        assert is_valid is False
        assert "render_scale" in error
    
    def test_default_project_data_structure(self):
        """Test default project data has expected structure."""
        data = get_default_project_data()
        
        assert "schema_version" in data
        assert data["schema_version"] == SCHEMA_VERSION
        assert data["duration"] == 30.0
        assert data["preview"]["target_fps"] == 30.0
        assert data["offline"]["width"] == 1920
        assert data["offline"]["height"] == 1080


class TestPreviewSettings:
    """Tests for PreviewSettings."""
    
    def test_default_values(self):
        """Test default preview settings."""
        settings = PreviewSettings()
        
        assert settings.render_scale == 1.0
        assert settings.supersampling is False
        assert settings.target_fps == 30.0


class TestOfflineSettings:
    """Tests for OfflineSettings."""
    
    def test_default_values(self):
        """Test default offline settings."""
        settings = OfflineSettings()
        
        assert settings.width == 1920
        assert settings.height == 1080
        assert settings.fps == 30.0
        assert settings.supersample_scale == 1
        assert settings.accumulation_samples == 1
        assert settings.save_png_sequence is True
        assert settings.encode_video is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
