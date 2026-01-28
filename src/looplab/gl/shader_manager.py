"""Shader manager for loading, compiling, and managing GLSL shaders.

This module handles:
- Loading shader source from files
- Injecting standard headers and helpers
- Compiling and linking shader programs
- Error mapping for user-friendly messages
"""

import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

# Import OpenGL - will be used when Qt context is active
try:
    from OpenGL.GL import (
        glCreateShader, glShaderSource, glCompileShader,
        glGetShaderiv, glGetShaderInfoLog, glDeleteShader,
        glCreateProgram, glAttachShader, glLinkProgram,
        glGetProgramiv, glGetProgramInfoLog, glUseProgram,
        glDeleteProgram, glGetUniformLocation, glUniform1f,
        glUniform1i, glUniform2f, glUniform3f, glUniform4f,
        GL_VERTEX_SHADER, GL_FRAGMENT_SHADER,
        GL_COMPILE_STATUS, GL_LINK_STATUS, GL_TRUE
    )
    OPENGL_AVAILABLE = True
except ImportError:
    OPENGL_AVAILABLE = False


@dataclass
class ShaderCompileError:
    """Information about a shader compilation error."""
    
    line: int
    message: str
    original_line: int = 0  # Line in user's file after header adjustment


@dataclass
class ShaderProgram:
    """A compiled and linked shader program."""
    
    program_id: int = 0
    vertex_shader_id: int = 0
    fragment_shader_id: int = 0
    is_valid: bool = False
    errors: list[ShaderCompileError] = field(default_factory=list)
    uniform_locations: dict[str, int] = field(default_factory=dict)
    
    def use(self):
        """Activate this shader program."""
        if self.is_valid and OPENGL_AVAILABLE:
            glUseProgram(self.program_id)
    
    def delete(self):
        """Delete this shader program and its shaders."""
        if not OPENGL_AVAILABLE:
            return
        if self.vertex_shader_id:
            glDeleteShader(self.vertex_shader_id)
        if self.fragment_shader_id:
            glDeleteShader(self.fragment_shader_id)
        if self.program_id:
            glDeleteProgram(self.program_id)
        self.is_valid = False


def get_shader_templates_path() -> Path:
    """Get the path to shader templates directory."""
    return Path(__file__).parent.parent / "shaders" / "templates"


def get_injected_header() -> str:
    """Load the injected header that provides standard uniforms."""
    header_path = get_shader_templates_path() / "injected_header.glsl"
    if header_path.exists():
        return header_path.read_text()
    
    # Fallback default header
    return """// LoopLab Injected Header
#version 330 core

// Standard uniforms
uniform vec2 u_resolution;
uniform float u_time;
uniform float u_phase;
uniform int u_frame;
uniform float u_duration;
uniform float u_seed;
uniform vec2 u_loop;
uniform vec2 u_jitter;

// Output
out vec4 fragColor;

// Constants
#define PI 3.14159265359
#define TAU 6.28318530718
"""


def get_loop_helpers() -> str:
    """Load the loop helper functions."""
    helpers_path = get_shader_templates_path() / "loop_helpers.glsl"
    if helpers_path.exists():
        return helpers_path.read_text()
    
    # Fallback default helpers
    return """// Loop Helpers
vec2 loopVec(float phase) {
    return vec2(cos(phase), sin(phase));
}

float loopSin(float phase) {
    return sin(phase);
}

float loopCos(float phase) {
    return cos(phase);
}
"""


def get_main_wrapper() -> str:
    """Get the main() wrapper for Shadertoy-style shaders."""
    return """
// Main wrapper - applies jitter for accumulation AA
void main() {
    vec4 col;
    // Apply subpixel jitter for anti-aliasing
    vec2 jitteredCoord = gl_FragCoord.xy + u_jitter;
    mainImage(col, jitteredCoord);
    fragColor = col;
}
"""


def get_vertex_shader() -> str:
    """Get the standard vertex shader for fullscreen quad."""
    return """#version 330 core

layout(location = 0) in vec2 a_position;

void main() {
    gl_Position = vec4(a_position, 0.0, 1.0);
}
"""


class ShaderManager:
    """Manages shader loading, compilation, and hot-reloading."""
    
    def __init__(self):
        self.current_program: Optional[ShaderProgram] = None
        self.source_path: Optional[Path] = None
        self.header_line_count: int = 0
    
    def load_shader_source(self, path: str | Path) -> str:
        """Load shader source from file.
        
        Args:
            path: Path to the shader file
            
        Returns:
            Shader source code
        """
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"Shader file not found: {path}")
        
        self.source_path = path
        return path.read_text()
    
    def build_fragment_shader(self, user_source: str) -> str:
        """Build complete fragment shader with headers and helpers.
        
        Args:
            user_source: User's shader code (mainImage function)
            
        Returns:
            Complete shader source ready for compilation
        """
        header = get_injected_header()
        helpers = get_loop_helpers()
        wrapper = get_main_wrapper()
        
        # Count header lines for error mapping
        self.header_line_count = header.count('\n') + helpers.count('\n')
        
        return f"{header}\n{helpers}\n{user_source}\n{wrapper}"
    
    def _compile_shader(self, source: str, shader_type: int) -> tuple[int, list[ShaderCompileError]]:
        """Compile a shader and return its ID and any errors.
        
        Args:
            source: Shader source code
            shader_type: GL_VERTEX_SHADER or GL_FRAGMENT_SHADER
            
        Returns:
            Tuple of (shader_id, errors)
        """
        if not OPENGL_AVAILABLE:
            return 0, [ShaderCompileError(0, "OpenGL not available")]
        
        shader_id = glCreateShader(shader_type)
        glShaderSource(shader_id, source)
        glCompileShader(shader_id)
        
        # Check for errors
        status = glGetShaderiv(shader_id, GL_COMPILE_STATUS)
        errors = []
        
        if status != GL_TRUE:
            info_log = glGetShaderInfoLog(shader_id)
            if info_log:
                if isinstance(info_log, bytes):
                    info_log = info_log.decode('utf-8')
                errors = self._parse_compile_errors(info_log)
            glDeleteShader(shader_id)
            return 0, errors
        
        return shader_id, errors
    
    def _parse_compile_errors(self, log: str) -> list[ShaderCompileError]:
        """Parse shader compilation error log.
        
        Args:
            log: Raw error log from OpenGL
            
        Returns:
            List of parsed errors with adjusted line numbers
        """
        errors = []
        # Common error formats: "0(line): error" or "ERROR: 0:line:"
        patterns = [
            r'0\((\d+)\)\s*:\s*(.+)',
            r'ERROR:\s*\d+:(\d+):\s*(.+)',
            r'(\d+):(\d+).*?:\s*(.+)',
        ]
        
        for line in log.strip().split('\n'):
            if not line.strip():
                continue
            
            matched = False
            for pattern in patterns:
                match = re.search(pattern, line)
                if match:
                    groups = match.groups()
                    line_num = int(groups[0])
                    message = groups[-1]
                    
                    # Adjust line number for injected header
                    original_line = max(1, line_num - self.header_line_count)
                    
                    errors.append(ShaderCompileError(
                        line=line_num,
                        message=message.strip(),
                        original_line=original_line
                    ))
                    matched = True
                    break
            
            if not matched and line.strip():
                errors.append(ShaderCompileError(
                    line=0,
                    message=line.strip(),
                    original_line=0
                ))
        
        return errors
    
    def compile_program(self, user_fragment_source: str) -> ShaderProgram:
        """Compile a complete shader program.
        
        Args:
            user_fragment_source: User's fragment shader (mainImage function)
            
        Returns:
            ShaderProgram with compilation status and any errors
        """
        program = ShaderProgram()
        
        if not OPENGL_AVAILABLE:
            program.errors = [ShaderCompileError(0, "OpenGL not available")]
            return program
        
        # Build complete fragment shader
        fragment_source = self.build_fragment_shader(user_fragment_source)
        vertex_source = get_vertex_shader()
        
        # Compile vertex shader
        program.vertex_shader_id, vertex_errors = self._compile_shader(
            vertex_source, GL_VERTEX_SHADER
        )
        if vertex_errors:
            program.errors = vertex_errors
            return program
        
        # Compile fragment shader
        program.fragment_shader_id, fragment_errors = self._compile_shader(
            fragment_source, GL_FRAGMENT_SHADER
        )
        if fragment_errors:
            program.errors = fragment_errors
            if program.vertex_shader_id:
                glDeleteShader(program.vertex_shader_id)
            return program
        
        # Link program
        program.program_id = glCreateProgram()
        glAttachShader(program.program_id, program.vertex_shader_id)
        glAttachShader(program.program_id, program.fragment_shader_id)
        glLinkProgram(program.program_id)
        
        # Check link status
        status = glGetProgramiv(program.program_id, GL_LINK_STATUS)
        if status != GL_TRUE:
            info_log = glGetProgramInfoLog(program.program_id)
            if isinstance(info_log, bytes):
                info_log = info_log.decode('utf-8')
            program.errors = [ShaderCompileError(0, f"Link error: {info_log}")]
            program.delete()
            return program
        
        program.is_valid = True
        
        # Cache standard uniform locations
        self._cache_uniform_locations(program)
        
        return program
    
    def _cache_uniform_locations(self, program: ShaderProgram):
        """Cache locations of standard uniforms."""
        if not OPENGL_AVAILABLE or not program.is_valid:
            return
        
        standard_uniforms = [
            "u_resolution", "u_time", "u_phase", "u_frame",
            "u_duration", "u_seed", "u_loop", "u_jitter"
        ]
        
        for name in standard_uniforms:
            loc = glGetUniformLocation(program.program_id, name)
            if loc >= 0:
                program.uniform_locations[name] = loc
    
    def set_uniforms(self, program: ShaderProgram, uniforms: dict):
        """Set uniform values on the shader program.
        
        Args:
            program: The shader program to modify
            uniforms: Dictionary of uniform names to values
        """
        if not OPENGL_AVAILABLE or not program.is_valid:
            return
        
        program.use()
        
        for name, value in uniforms.items():
            loc = program.uniform_locations.get(name)
            if loc is None:
                loc = glGetUniformLocation(program.program_id, name)
                if loc >= 0:
                    program.uniform_locations[name] = loc
            
            if loc is None or loc < 0:
                continue
            
            # Set uniform based on type
            if isinstance(value, int):
                glUniform1i(loc, value)
            elif isinstance(value, float):
                glUniform1f(loc, value)
            elif isinstance(value, tuple):
                if len(value) == 2:
                    glUniform2f(loc, *value)
                elif len(value) == 3:
                    glUniform3f(loc, *value)
                elif len(value) == 4:
                    glUniform4f(loc, *value)
    
    def reload(self) -> ShaderProgram:
        """Reload shader from the previously loaded path.
        
        Returns:
            New ShaderProgram (caller should delete old one)
        """
        if not self.source_path:
            return ShaderProgram(errors=[
                ShaderCompileError(0, "No shader file loaded")
            ])
        
        source = self.load_shader_source(self.source_path)
        new_program = self.compile_program(source)
        
        # If successful, replace current program
        if new_program.is_valid:
            if self.current_program:
                self.current_program.delete()
            self.current_program = new_program
        
        return new_program
