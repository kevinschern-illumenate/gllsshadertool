"""Offline renderer worker for deterministic frame-by-frame rendering.

This module provides a QThread-based worker that renders frames
to PNG files using a dedicated OpenGL context.
"""

import os
from pathlib import Path
from typing import Optional
import numpy as np

from PySide6.QtCore import QObject, QThread, Signal, Slot
from PySide6.QtGui import QOffscreenSurface, QSurfaceFormat, QOpenGLContext

from ..gl.shader_manager import ShaderManager
from ..gl.gl_resources import QuadMesh, RenderTarget, clear_viewport
from ..gl.uniforms import UniformManager
from .timeline import Timeline
from .image_writer import save_frame_png


class OfflineRenderWorker(QObject):
    """Worker for offline rendering in a separate thread.
    
    Signals:
        progress: Emitted with (current_frame, total_frames)
        frame_complete: Emitted when a frame is saved (frame_index, path)
        log_message: Emitted with log messages
        finished: Emitted when rendering completes (success)
        error: Emitted on error (message)
    """
    
    progress = Signal(int, int)
    frame_complete = Signal(int, str)
    log_message = Signal(str)
    finished = Signal(bool)
    error = Signal(str)
    
    def __init__(self, parent: Optional[QObject] = None):
        super().__init__(parent)
        
        # Render settings
        self.shader_source: str = ""
        self.output_dir: str = ""
        self.width: int = 1920
        self.height: int = 1080
        self.fps: float = 30.0
        self.duration: float = 30.0
        self.seed: float = 0.0
        self.supersample_scale: int = 1
        self.accumulation_samples: int = 1
        
        # Control
        self._cancelled = False
        
        # OpenGL resources (created in render thread)
        self._context: Optional[QOpenGLContext] = None
        self._surface: Optional[QOffscreenSurface] = None
        self._shader_manager: Optional[ShaderManager] = None
        self._quad: Optional[QuadMesh] = None
        self._render_target: Optional[RenderTarget] = None
    
    def configure(
        self,
        shader_source: str,
        output_dir: str,
        width: int = 1920,
        height: int = 1080,
        fps: float = 30.0,
        duration: float = 30.0,
        seed: float = 0.0,
        supersample_scale: int = 1,
        accumulation_samples: int = 1
    ):
        """Configure render settings.
        
        Args:
            shader_source: The shader source code (mainImage function)
            output_dir: Directory to save PNG frames
            width: Output width in pixels
            height: Output height in pixels
            fps: Frames per second
            duration: Loop duration in seconds
            seed: Random seed for reproducibility
            supersample_scale: Supersample factor (1, 2, or 4)
            accumulation_samples: Number of samples per frame for AA
        """
        self.shader_source = shader_source
        self.output_dir = output_dir
        self.width = width
        self.height = height
        self.fps = fps
        self.duration = duration
        self.seed = seed
        self.supersample_scale = max(1, min(4, supersample_scale))
        self.accumulation_samples = max(1, accumulation_samples)
    
    def cancel(self):
        """Cancel the render operation."""
        self._cancelled = True
    
    def _setup_gl_context(self) -> bool:
        """Set up OpenGL context and surface for offscreen rendering."""
        try:
            # Create surface format
            fmt = QSurfaceFormat()
            fmt.setVersion(3, 3)
            fmt.setProfile(QSurfaceFormat.OpenGLContextProfile.CoreProfile)
            
            # Create offscreen surface
            self._surface = QOffscreenSurface()
            self._surface.setFormat(fmt)
            self._surface.create()
            
            if not self._surface.isValid():
                self.error.emit("Failed to create offscreen surface")
                return False
            
            # Create OpenGL context
            self._context = QOpenGLContext()
            self._context.setFormat(fmt)
            
            if not self._context.create():
                self.error.emit("Failed to create OpenGL context")
                return False
            
            # Make context current
            if not self._context.makeCurrent(self._surface):
                self.error.emit("Failed to make OpenGL context current")
                return False
            
            return True
        except Exception as e:
            self.error.emit(f"OpenGL setup failed: {e}")
            return False
    
    def _setup_gl_resources(self) -> bool:
        """Set up shader, quad, and render target."""
        try:
            # Create quad mesh
            self._quad = QuadMesh()
            self._quad.create()
            
            # Calculate render resolution (with supersampling)
            render_width = self.width * self.supersample_scale
            render_height = self.height * self.supersample_scale
            
            # Create render target (FBO)
            self._render_target = RenderTarget()
            self._render_target.create(render_width, render_height)
            
            if not self._render_target.is_valid:
                self.error.emit("Failed to create render target")
                return False
            
            # Compile shader
            self._shader_manager = ShaderManager()
            program = self._shader_manager.compile_program(self.shader_source)
            
            if not program.is_valid:
                errors = "\n".join(e.message for e in program.errors)
                self.error.emit(f"Shader compilation failed:\n{errors}")
                return False
            
            self._shader_manager.current_program = program
            return True
            
        except Exception as e:
            self.error.emit(f"GL resource setup failed: {e}")
            return False
    
    def _cleanup_gl(self):
        """Clean up OpenGL resources."""
        if self._context and self._surface:
            self._context.makeCurrent(self._surface)
        
        if self._quad:
            self._quad.delete()
        
        if self._render_target:
            self._render_target.delete()
        
        if self._shader_manager and self._shader_manager.current_program:
            self._shader_manager.current_program.delete()
        
        if self._context:
            self._context.doneCurrent()
    
    def _render_frame(self, frame_info, uniform_manager: UniformManager) -> Optional[np.ndarray]:
        """Render a single frame.
        
        Args:
            frame_info: FrameInfo with time/phase data
            uniform_manager: Uniform manager with current state
            
        Returns:
            RGBA pixel data as numpy array, or None on failure
        """
        program = self._shader_manager.current_program
        if not program or not program.is_valid:
            return None
        
        render_width = self.width * self.supersample_scale
        render_height = self.height * self.supersample_scale
        
        # For accumulation AA, we'll accumulate multiple samples
        if self.accumulation_samples > 1:
            accumulator = np.zeros((render_height, render_width, 4), dtype=np.float32)
            
            for sample in range(self.accumulation_samples):
                # Apply small jitter for AA (deterministic based on frame and sample)
                # Jitter is in pixel units for the shader to use
                jitter_x = (sample % 4) / 4.0 - 0.5
                jitter_y = (sample // 4) / 4.0 - 0.5
                
                # Set jitter uniform for shader to offset pixel coordinates
                uniform_manager.set_jitter(jitter_x, jitter_y)
                
                # Render with jitter
                self._render_target.bind()
                clear_viewport(0.0, 0.0, 0.0, 1.0)
                
                # Update uniforms
                uniform_manager.set_frame_info(
                    time=frame_info.time,
                    phase=frame_info.phase,
                    frame=frame_info.frame,
                    loop_x=frame_info.loop_x,
                    loop_y=frame_info.loop_y
                )
                
                self._shader_manager.set_uniforms(program, uniform_manager.get_all_uniforms())
                self._quad.draw()
                
                # Read pixels
                pixels = self._render_target.read_pixels()
                if pixels:
                    frame_data = np.frombuffer(pixels, dtype=np.uint8).reshape(
                        render_height, render_width, 4
                    ).astype(np.float32)
                    accumulator += frame_data
            
            # Reset jitter
            uniform_manager.set_jitter(0.0, 0.0)
            
            # Average samples
            accumulator /= self.accumulation_samples
            pixels_array = accumulator.astype(np.uint8)
        else:
            # Single sample render
            self._render_target.bind()
            clear_viewport(0.0, 0.0, 0.0, 1.0)
            
            uniform_manager.set_frame_info(
                time=frame_info.time,
                phase=frame_info.phase,
                frame=frame_info.frame,
                loop_x=frame_info.loop_x,
                loop_y=frame_info.loop_y
            )
            
            self._shader_manager.set_uniforms(program, uniform_manager.get_all_uniforms())
            self._quad.draw()
            
            pixels = self._render_target.read_pixels()
            if not pixels:
                return None
            
            pixels_array = np.frombuffer(pixels, dtype=np.uint8).reshape(
                render_height, render_width, 4
            )
        
        # Flip vertically (OpenGL origin is bottom-left)
        pixels_array = np.flipud(pixels_array)
        
        # Downsample if supersampling
        if self.supersample_scale > 1:
            pixels_array = self._downsample(pixels_array)
        
        return pixels_array
    
    def _downsample(self, image: np.ndarray) -> np.ndarray:
        """Downsample image by supersample scale using box filter.
        
        Args:
            image: Input RGBA image
            
        Returns:
            Downsampled image
        """
        scale = self.supersample_scale
        h, w = image.shape[:2]
        new_h, new_w = h // scale, w // scale
        
        # Simple box filter downsampling
        result = image.reshape(new_h, scale, new_w, scale, 4).mean(axis=(1, 3))
        return result.astype(np.uint8)
    
    @Slot()
    def run(self):
        """Main render loop - call this from the worker thread."""
        self._cancelled = False
        
        self.log_message.emit(f"Starting offline render: {self.width}x{self.height} @ {self.fps}fps")
        self.log_message.emit(f"Duration: {self.duration}s, Supersample: {self.supersample_scale}x, "
                              f"Accumulation: {self.accumulation_samples} samples")
        
        # Create output directory
        output_path = Path(self.output_dir)
        try:
            output_path.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            self.error.emit(f"Failed to create output directory: {e}")
            self.finished.emit(False)
            return
        
        # Set up OpenGL
        if not self._setup_gl_context():
            self.finished.emit(False)
            return
        
        if not self._setup_gl_resources():
            self._cleanup_gl()
            self.finished.emit(False)
            return
        
        # Set up timeline and uniforms
        timeline = Timeline(duration=self.duration, fps=self.fps)
        uniform_manager = UniformManager()
        
        render_width = self.width * self.supersample_scale
        render_height = self.height * self.supersample_scale
        uniform_manager.set_resolution(float(render_width), float(render_height))
        uniform_manager.set_seed(self.seed)
        uniform_manager.standard.duration = self.duration
        
        total_frames = timeline.total_frames
        self.log_message.emit(f"Rendering {total_frames} frames...")
        
        # Render each frame
        for frame_info in timeline.iter_frames():
            if self._cancelled:
                self.log_message.emit("Render cancelled")
                break
            
            # Render frame
            pixels = self._render_frame(frame_info, uniform_manager)
            
            if pixels is None:
                self.error.emit(f"Failed to render frame {frame_info.frame}")
                continue
            
            # Save frame
            frame_path = output_path / f"frame_{frame_info.frame:06d}.png"
            try:
                save_frame_png(pixels, str(frame_path))
                self.frame_complete.emit(frame_info.frame, str(frame_path))
            except Exception as e:
                self.error.emit(f"Failed to save frame {frame_info.frame}: {e}")
            
            # Report progress
            self.progress.emit(frame_info.frame + 1, total_frames)
        
        # Cleanup
        self._cleanup_gl()
        
        success = not self._cancelled
        if success:
            self.log_message.emit(f"Render complete: {total_frames} frames saved to {self.output_dir}")
        
        self.finished.emit(success)


def create_render_thread(worker: OfflineRenderWorker) -> QThread:
    """Create a thread for the offline render worker.
    
    Args:
        worker: The worker object to move to the thread
        
    Returns:
        QThread instance (not started)
    """
    thread = QThread()
    worker.moveToThread(thread)
    thread.started.connect(worker.run)
    worker.finished.connect(thread.quit)
    return thread
