"""Preview OpenGL widget for real-time shader rendering.

This module provides the QOpenGLWidget subclass that renders
shaders in real-time for preview purposes.
"""

from typing import Optional
import math

from PySide6.QtCore import QTimer, Signal, QElapsedTimer
from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QSurfaceFormat
from PySide6.QtOpenGLWidgets import QOpenGLWidget

from .shader_manager import ShaderManager, ShaderProgram
from .gl_resources import QuadMesh, clear_viewport
from .uniforms import UniformManager
from ..render.timeline import Timeline


class PreviewGLWidget(QOpenGLWidget):
    """OpenGL widget for real-time shader preview.
    
    Signals:
        shader_compiled: Emitted when shader compilation completes (success, errors_str)
        fps_updated: Emitted with current measured FPS
    """
    
    shader_compiled = Signal(bool, str)
    fps_updated = Signal(float)
    
    def __init__(self, parent: Optional[QWidget] = None):
        # Set up OpenGL format
        fmt = QSurfaceFormat()
        fmt.setVersion(3, 3)
        fmt.setProfile(QSurfaceFormat.OpenGLContextProfile.CoreProfile)
        fmt.setSwapBehavior(QSurfaceFormat.SwapBehavior.DoubleBuffer)
        fmt.setSamples(4)  # Multisampling
        QSurfaceFormat.setDefaultFormat(fmt)
        
        super().__init__(parent)
        
        # Rendering components
        self.shader_manager = ShaderManager()
        self.quad: Optional[QuadMesh] = None
        self.uniform_manager = UniformManager()
        
        # Timeline for animation
        self.timeline = Timeline()
        self.current_frame = 0
        self.playing = False
        
        # Render timing
        self.elapsed_timer = QElapsedTimer()
        self.frame_count = 0
        self.last_fps_time = 0
        
        # Animation timer
        self.anim_timer = QTimer(self)
        self.anim_timer.timeout.connect(self._on_animation_tick)
        self.target_fps = 30.0
        
        # Render scale (for performance)
        self.render_scale = 1.0
    
    def initializeGL(self):
        """Initialize OpenGL resources."""
        # Create quad mesh
        self.quad = QuadMesh()
        self.quad.create()
        
        # Start FPS timer
        self.elapsed_timer.start()
        self.last_fps_time = 0
    
    def resizeGL(self, width: int, height: int):
        """Handle widget resize."""
        # Update uniform resolution
        scaled_width = int(width * self.render_scale)
        scaled_height = int(height * self.render_scale)
        self.uniform_manager.set_resolution(float(scaled_width), float(scaled_height))
    
    def paintGL(self):
        """Render the current frame."""
        # Clear viewport
        clear_viewport(0.0, 0.0, 0.0, 1.0)
        
        # Get current program
        program = self.shader_manager.current_program
        if not program or not program.is_valid:
            return
        
        # Get frame info from timeline
        frame_info = self.timeline.get_frame_info(self.current_frame)
        
        # Update uniforms
        self.uniform_manager.set_frame_info(
            time=frame_info.time,
            phase=frame_info.phase,
            frame=frame_info.frame,
            loop_x=frame_info.loop_x,
            loop_y=frame_info.loop_y
        )
        
        # Bind uniforms and draw
        self.shader_manager.set_uniforms(program, self.uniform_manager.get_all_uniforms())
        self.quad.draw()
        
        # Update FPS counter
        self._update_fps()
    
    def _update_fps(self):
        """Calculate and emit FPS."""
        self.frame_count += 1
        elapsed = self.elapsed_timer.elapsed()
        
        # Update FPS every second
        if elapsed - self.last_fps_time >= 1000:
            fps = self.frame_count / ((elapsed - self.last_fps_time) / 1000.0)
            self.fps_updated.emit(fps)
            self.last_fps_time = elapsed
            self.frame_count = 0
    
    def _on_animation_tick(self):
        """Called by animation timer to advance frame."""
        if self.playing:
            self.current_frame = (self.current_frame + 1) % self.timeline.total_frames
            self.update()
    
    def load_shader(self, path: str) -> bool:
        """Load and compile a shader from file.
        
        Args:
            path: Path to shader file
            
        Returns:
            True if successful
        """
        try:
            source = self.shader_manager.load_shader_source(path)
            return self.compile_shader(source)
        except FileNotFoundError as e:
            self.shader_compiled.emit(False, str(e))
            return False
    
    def compile_shader(self, source: str) -> bool:
        """Compile shader from source.
        
        Args:
            source: Shader source code (mainImage function)
            
        Returns:
            True if successful
        """
        self.makeCurrent()
        
        program = self.shader_manager.compile_program(source)
        
        if program.is_valid:
            # Replace current program
            if self.shader_manager.current_program:
                self.shader_manager.current_program.delete()
            self.shader_manager.current_program = program
            self.shader_compiled.emit(True, "Compiled successfully")
            self.update()
            return True
        else:
            # Report errors
            errors = "\n".join(
                f"Line {e.original_line}: {e.message}" for e in program.errors
            )
            self.shader_compiled.emit(False, errors)
            return False
    
    def reload_shader(self) -> bool:
        """Reload the current shader from disk.
        
        Returns:
            True if successful
        """
        self.makeCurrent()
        program = self.shader_manager.reload()
        
        if program.is_valid:
            self.shader_compiled.emit(True, "Reloaded successfully")
            self.update()
            return True
        else:
            errors = "\n".join(
                f"Line {e.original_line}: {e.message}" for e in program.errors
            )
            self.shader_compiled.emit(False, errors)
            return False
    
    def play(self):
        """Start animation playback."""
        self.playing = True
        interval = int(1000.0 / self.target_fps)
        self.anim_timer.start(interval)
    
    def pause(self):
        """Pause animation playback."""
        self.playing = False
        self.anim_timer.stop()
    
    def toggle_playback(self):
        """Toggle play/pause."""
        if self.playing:
            self.pause()
        else:
            self.play()
    
    def seek_frame(self, frame: int):
        """Jump to a specific frame.
        
        Args:
            frame: Frame index to seek to
        """
        self.current_frame = max(0, min(frame, self.timeline.total_frames - 1))
        self.update()
    
    def seek_time(self, time: float):
        """Jump to a specific time.
        
        Args:
            time: Time in seconds
        """
        frame = self.timeline.get_frame_from_time(time)
        self.seek_frame(frame)
    
    def set_duration(self, duration: float):
        """Set the loop duration.
        
        Args:
            duration: Duration in seconds
        """
        self.timeline.duration = duration
        self.uniform_manager.standard.duration = duration
        self.current_frame = min(self.current_frame, self.timeline.total_frames - 1)
    
    def set_fps(self, fps: float):
        """Set the timeline FPS.
        
        Args:
            fps: Frames per second
        """
        self.timeline.fps = fps
        self.target_fps = fps
        if self.playing:
            self.anim_timer.setInterval(int(1000.0 / fps))
    
    def set_render_scale(self, scale: float):
        """Set render scale for performance.
        
        Args:
            scale: Scale factor (0.25 to 1.0)
        """
        self.render_scale = max(0.25, min(1.0, scale))
        self.resizeGL(self.width(), self.height())
    
    def set_seed(self, seed: float):
        """Set the random seed.
        
        Args:
            seed: Seed value
        """
        self.uniform_manager.set_seed(seed)
        self.update()
    
    def cleanup(self):
        """Clean up OpenGL resources."""
        self.makeCurrent()
        
        if self.quad:
            self.quad.delete()
        
        if self.shader_manager.current_program:
            self.shader_manager.current_program.delete()
