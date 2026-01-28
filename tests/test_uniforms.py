"""Tests for uniform parsing."""

import pytest

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from looplab.gl.uniforms import (
    StandardUniforms, UserParameter, UniformManager,
    parse_param_comment, parse_params_from_source
)


class TestStandardUniforms:
    """Tests for StandardUniforms class."""
    
    def test_default_values(self):
        """Test default uniform values."""
        uniforms = StandardUniforms()
        
        assert uniforms.resolution == (1920.0, 1080.0)
        assert uniforms.time == 0.0
        assert uniforms.phase == 0.0
        assert uniforms.frame == 0
        assert uniforms.duration == 30.0
        assert uniforms.seed == 0.0
        assert uniforms.loop == (1.0, 0.0)
    
    def test_to_dict(self):
        """Test conversion to dictionary."""
        uniforms = StandardUniforms()
        uniforms.time = 5.0
        uniforms.phase = 1.047
        
        d = uniforms.to_dict()
        
        assert d["u_time"] == 5.0
        assert d["u_phase"] == 1.047
        assert d["u_resolution"] == (1920.0, 1080.0)


class TestUniformManager:
    """Tests for UniformManager class."""
    
    def test_set_resolution(self):
        """Test setting resolution."""
        manager = UniformManager()
        manager.set_resolution(1280.0, 720.0)
        
        assert manager.standard.resolution == (1280.0, 720.0)
    
    def test_set_frame_info(self):
        """Test setting frame information."""
        manager = UniformManager()
        manager.set_frame_info(
            time=10.0,
            phase=2.094,
            frame=300,
            loop_x=-0.5,
            loop_y=0.866
        )
        
        assert manager.standard.time == 10.0
        assert manager.standard.phase == 2.094
        assert manager.standard.frame == 300
        assert manager.standard.loop == (-0.5, 0.866)
    
    def test_add_user_param(self):
        """Test adding user parameters."""
        manager = UniformManager()
        param = UserParameter(
            name="speed",
            param_type="float",
            min_value=0.0,
            max_value=10.0,
            default_value=1.0
        )
        
        manager.add_user_param(param)
        
        assert "speed" in manager.user_params
        assert manager.get_user_param_value("speed") == 1.0
    
    def test_set_user_param_value(self):
        """Test setting user parameter values."""
        manager = UniformManager()
        param = UserParameter(
            name="speed",
            param_type="float",
            default_value=1.0
        )
        manager.add_user_param(param)
        
        manager.set_user_param_value("speed", 5.0)
        
        assert manager.get_user_param_value("speed") == 5.0
    
    def test_get_all_uniforms(self):
        """Test getting all uniforms combined."""
        manager = UniformManager()
        manager.set_seed(42.0)
        
        param = UserParameter(
            name="speed",
            param_type="float",
            default_value=2.0
        )
        manager.add_user_param(param)
        
        all_uniforms = manager.get_all_uniforms()
        
        assert all_uniforms["u_seed"] == 42.0
        assert all_uniforms["u_speed"] == 2.0
    
    def test_clear_user_params(self):
        """Test clearing user parameters."""
        manager = UniformManager()
        param = UserParameter(name="speed", param_type="float", default_value=1.0)
        manager.add_user_param(param)
        
        manager.clear_user_params()
        
        assert len(manager.user_params) == 0


class TestParseParamComment:
    """Tests for parsing @param comments."""
    
    def test_parse_float_param(self):
        """Test parsing float parameter."""
        line = "// @param speed float 0.0 10.0 1.0"
        param = parse_param_comment(line)
        
        assert param is not None
        assert param.name == "speed"
        assert param.param_type == "float"
        assert param.min_value == 0.0
        assert param.max_value == 10.0
        assert param.default_value == 1.0
    
    def test_parse_float_simple(self):
        """Test parsing simple float with just default."""
        line = "// @param intensity float 0.5"
        param = parse_param_comment(line)
        
        assert param is not None
        assert param.name == "intensity"
        assert param.param_type == "float"
        assert param.default_value == 0.5
    
    def test_parse_color_param(self):
        """Test parsing color parameter."""
        line = "// @param tint color 1.0 0.5 0.0"
        param = parse_param_comment(line)
        
        assert param is not None
        assert param.name == "tint"
        assert param.param_type == "color"
        assert param.default_value == (1.0, 0.5, 0.0)
    
    def test_parse_vec3_param(self):
        """Test parsing vec3 parameter."""
        line = "// @param offset vec3 0.5 0.5 0.5"
        param = parse_param_comment(line)
        
        assert param is not None
        assert param.name == "offset"
        assert param.param_type == "vec3"
        assert param.default_value == (0.5, 0.5, 0.5)
    
    def test_parse_invalid_line(self):
        """Test parsing non-param line."""
        line = "// This is just a comment"
        param = parse_param_comment(line)
        assert param is None
    
    def test_parse_empty_line(self):
        """Test parsing empty line."""
        line = ""
        param = parse_param_comment(line)
        assert param is None
    
    def test_parse_incomplete_param(self):
        """Test parsing incomplete param (missing values)."""
        line = "// @param speed"
        param = parse_param_comment(line)
        assert param is None


class TestParseParamsFromSource:
    """Tests for parsing multiple params from source."""
    
    def test_parse_multiple_params(self):
        """Test parsing multiple parameters."""
        source = """
// Shader with parameters
// @param speed float 0.0 10.0 1.0
// @param complexity float 1.0 5.0 3.0
// @param color color 1.0 0.5 0.0

void mainImage(out vec4 fragColor, in vec2 fragCoord) {
    // shader code
}
"""
        params = parse_params_from_source(source)
        
        assert len(params) == 3
        assert params[0].name == "speed"
        assert params[1].name == "complexity"
        assert params[2].name == "color"
    
    def test_parse_no_params(self):
        """Test parsing source with no params."""
        source = """
// Simple shader
void mainImage(out vec4 fragColor, in vec2 fragCoord) {
    fragColor = vec4(1.0);
}
"""
        params = parse_params_from_source(source)
        assert len(params) == 0
    
    def test_parse_mixed_comments(self):
        """Test that only @param comments are parsed."""
        source = """
// Regular comment
// @param speed float 1.0
// Another comment
// @param size float 2.0
"""
        params = parse_params_from_source(source)
        
        assert len(params) == 2
        assert params[0].name == "speed"
        assert params[1].name == "size"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
