"""Main window for LoopLab application.

This module provides the main application window with dockable panels
for shader editing, preview, timeline, parameters, and export.
"""

import os
from pathlib import Path
from typing import Optional

from PySide6.QtCore import Qt, Slot, QFileSystemWatcher
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QDockWidget, QStatusBar, QMenuBar, QMenu,
    QFileDialog, QMessageBox, QLabel
)
from PySide6.QtGui import QAction, QKeySequence

from ..gl.preview_widget import PreviewGLWidget
from ..gl.uniforms import parse_params_from_source
from .docks import (
    ShaderDock, TimelineDock, ParametersDock, ExportDock
)
from .models import Project, save_project, load_project


class MainWindow(QMainWindow):
    """Main application window."""
    
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("LoopLab - GLSL Loop Shader Tool")
        self.resize(1600, 900)
        
        # Current project
        self.project = Project()
        self.project_path: Optional[Path] = None
        
        # File watcher for auto-reload
        self.file_watcher = QFileSystemWatcher(self)
        self.file_watcher.fileChanged.connect(self._on_shader_file_changed)
        self.auto_reload = True
        
        # Set up UI
        self._setup_menu()
        self._setup_central_widget()
        self._setup_docks()
        self._setup_status_bar()
        
        # Connect signals
        self._connect_signals()
        
        # Load default shader
        self._load_default_shader()
    
    def _setup_menu(self):
        """Set up the menu bar."""
        menu_bar = QMenuBar(self)
        self.setMenuBar(menu_bar)
        
        # File menu
        file_menu = QMenu("&File", self)
        menu_bar.addMenu(file_menu)
        
        new_action = QAction("&New Project", self)
        new_action.setShortcut(QKeySequence.StandardKey.New)
        new_action.triggered.connect(self._new_project)
        file_menu.addAction(new_action)
        
        open_action = QAction("&Open Project...", self)
        open_action.setShortcut(QKeySequence.StandardKey.Open)
        open_action.triggered.connect(self._open_project)
        file_menu.addAction(open_action)
        
        save_action = QAction("&Save Project", self)
        save_action.setShortcut(QKeySequence.StandardKey.Save)
        save_action.triggered.connect(self._save_project)
        file_menu.addAction(save_action)
        
        save_as_action = QAction("Save Project &As...", self)
        save_as_action.setShortcut(QKeySequence("Ctrl+Shift+S"))
        save_as_action.triggered.connect(self._save_project_as)
        file_menu.addAction(save_as_action)
        
        file_menu.addSeparator()
        
        load_shader_action = QAction("&Load Shader...", self)
        load_shader_action.setShortcut(QKeySequence("Ctrl+L"))
        load_shader_action.triggered.connect(self._load_shader_dialog)
        file_menu.addAction(load_shader_action)
        
        file_menu.addSeparator()
        
        quit_action = QAction("&Quit", self)
        quit_action.setShortcut(QKeySequence.StandardKey.Quit)
        quit_action.triggered.connect(self.close)
        file_menu.addAction(quit_action)
        
        # Edit menu
        edit_menu = QMenu("&Edit", self)
        menu_bar.addMenu(edit_menu)
        
        reload_shader_action = QAction("&Reload Shader", self)
        reload_shader_action.setShortcut(QKeySequence("F5"))
        reload_shader_action.triggered.connect(self._reload_shader)
        edit_menu.addAction(reload_shader_action)
        
        # View menu
        view_menu = QMenu("&View", self)
        menu_bar.addMenu(view_menu)
        
        # Will add dock visibility toggles here
        
        # Help menu
        help_menu = QMenu("&Help", self)
        menu_bar.addMenu(help_menu)
        
        about_action = QAction("&About LoopLab", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)
    
    def _setup_central_widget(self):
        """Set up the central preview widget."""
        # Create container for preview
        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Preview widget
        self.preview_widget = PreviewGLWidget()
        layout.addWidget(self.preview_widget)
        
        self.setCentralWidget(central_widget)
    
    def _setup_docks(self):
        """Set up dockable panels."""
        # Shader dock (left)
        self.shader_dock = ShaderDock(self)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.shader_dock)
        
        # Timeline dock (bottom)
        self.timeline_dock = TimelineDock(self)
        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, self.timeline_dock)
        
        # Parameters dock (right)
        self.parameters_dock = ParametersDock(self)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.parameters_dock)
        
        # Export dock (right, tabbed with parameters)
        self.export_dock = ExportDock(self)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.export_dock)
        self.tabifyDockWidget(self.parameters_dock, self.export_dock)
        self.parameters_dock.raise_()
    
    def _setup_status_bar(self):
        """Set up the status bar."""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # FPS label
        self.fps_label = QLabel("FPS: --")
        self.status_bar.addPermanentWidget(self.fps_label)
        
        # Frame info label
        self.frame_label = QLabel("Frame: 0 / 900")
        self.status_bar.addPermanentWidget(self.frame_label)
    
    def _connect_signals(self):
        """Connect signals between components."""
        # Preview signals
        self.preview_widget.shader_compiled.connect(self._on_shader_compiled)
        self.preview_widget.fps_updated.connect(self._on_fps_updated)
        
        # Shader dock signals
        self.shader_dock.load_clicked.connect(self._load_shader_dialog)
        self.shader_dock.reload_clicked.connect(self._reload_shader)
        self.shader_dock.auto_reload_changed.connect(self._on_auto_reload_changed)
        
        # Timeline dock signals
        self.timeline_dock.play_clicked.connect(self._toggle_playback)
        self.timeline_dock.time_changed.connect(self._on_time_changed)
        self.timeline_dock.fps_changed.connect(self._on_fps_changed)
        
        # Parameters dock signals
        self.parameters_dock.seed_changed.connect(self._on_seed_changed)
        self.parameters_dock.randomize_seed_clicked.connect(self._randomize_seed)
        
        # Export dock signals
        self.export_dock.render_clicked.connect(self._start_render)
    
    def _load_default_shader(self):
        """Load the default example shader."""
        examples_path = Path(__file__).parent.parent / "shaders" / "examples"
        plasma_path = examples_path / "plasma_loop.glsl"
        
        if plasma_path.exists():
            self._load_shader(str(plasma_path))
    
    def _load_shader(self, path: str):
        """Load a shader from file.
        
        Args:
            path: Path to shader file
        """
        # Remove old file from watcher
        watched = self.file_watcher.files()
        if watched:
            self.file_watcher.removePaths(watched)
        
        # Load shader
        if self.preview_widget.load_shader(path):
            self.project.shader_path = path
            
            # Add to file watcher
            self.file_watcher.addPath(path)
            
            # Update shader dock
            self.shader_dock.set_shader_path(path)
            
            # Parse and update parameters
            self._update_parameters_from_shader(path)
            
            self.status_bar.showMessage(f"Loaded: {path}", 3000)
    
    def _update_parameters_from_shader(self, path: str):
        """Parse shader source and update parameter controls.
        
        Args:
            path: Path to shader file
        """
        try:
            with open(path, 'r') as f:
                source = f.read()
            
            params = parse_params_from_source(source)
            self.parameters_dock.update_parameters(params)
            
            # Update uniform manager
            self.preview_widget.uniform_manager.clear_user_params()
            for param in params:
                self.preview_widget.uniform_manager.add_user_param(param)
                
        except Exception as e:
            self.status_bar.showMessage(f"Error parsing parameters: {e}", 3000)
    
    @Slot()
    def _load_shader_dialog(self):
        """Show dialog to load a shader file."""
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Load Shader",
            str(Path(__file__).parent.parent / "shaders" / "examples"),
            "GLSL Files (*.glsl *.frag);;All Files (*)"
        )
        if path:
            self._load_shader(path)
    
    @Slot()
    def _reload_shader(self):
        """Reload the current shader."""
        if self.preview_widget.reload_shader():
            self.status_bar.showMessage("Shader reloaded", 2000)
            
            # Re-parse parameters
            if self.project.shader_path:
                self._update_parameters_from_shader(self.project.shader_path)
    
    @Slot(str)
    def _on_shader_file_changed(self, path: str):
        """Handle shader file change from file watcher."""
        if self.auto_reload:
            self._reload_shader()
            # Re-add to watcher (some editors replace the file)
            if path and os.path.exists(path):
                self.file_watcher.addPath(path)
    
    @Slot(bool)
    def _on_auto_reload_changed(self, enabled: bool):
        """Handle auto-reload toggle."""
        self.auto_reload = enabled
    
    @Slot(bool, str)
    def _on_shader_compiled(self, success: bool, message: str):
        """Handle shader compilation result."""
        self.shader_dock.set_compile_status(success, message)
        if success:
            self.status_bar.showMessage("Shader compiled successfully", 2000)
        else:
            self.status_bar.showMessage("Shader compilation failed", 3000)
    
    @Slot(float)
    def _on_fps_updated(self, fps: float):
        """Update FPS display."""
        self.fps_label.setText(f"FPS: {fps:.1f}")
    
    @Slot()
    def _toggle_playback(self):
        """Toggle play/pause."""
        self.preview_widget.toggle_playback()
        self.timeline_dock.set_playing(self.preview_widget.playing)
    
    @Slot(float)
    def _on_time_changed(self, time: float):
        """Handle timeline scrub."""
        self.preview_widget.seek_time(time)
        frame = self.preview_widget.current_frame
        total = self.preview_widget.timeline.total_frames
        self.frame_label.setText(f"Frame: {frame} / {total}")
    
    @Slot(float)
    def _on_fps_changed(self, fps: float):
        """Handle FPS change."""
        self.preview_widget.set_fps(fps)
        self.project.preview.target_fps = fps
        total = self.preview_widget.timeline.total_frames
        self.frame_label.setText(f"Frame: {self.preview_widget.current_frame} / {total}")
    
    @Slot(float)
    def _on_seed_changed(self, seed: float):
        """Handle seed change."""
        self.preview_widget.set_seed(seed)
        self.project.seed = seed
    
    @Slot()
    def _randomize_seed(self):
        """Generate new random seed."""
        import random
        seed = random.random() * 1000.0
        self.preview_widget.set_seed(seed)
        self.project.seed = seed
        self.parameters_dock.set_seed(seed)
    
    @Slot()
    def _start_render(self):
        """Start offline rendering."""
        # Get settings from export dock
        settings = self.export_dock.get_settings()
        
        if not settings.get("output_dir"):
            QMessageBox.warning(
                self,
                "No Output Directory",
                "Please select an output directory for the render."
            )
            return
        
        # Get shader source
        if not self.project.shader_path:
            QMessageBox.warning(
                self,
                "No Shader",
                "Please load a shader before rendering."
            )
            return
        
        try:
            with open(self.project.shader_path, 'r') as f:
                shader_source = f.read()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to read shader: {e}")
            return
        
        # Import here to avoid circular imports
        from ..render.offline_worker import OfflineRenderWorker, create_render_thread
        
        # Create worker and thread
        self.render_worker = OfflineRenderWorker()
        self.render_worker.configure(
            shader_source=shader_source,
            output_dir=settings["output_dir"],
            width=settings.get("width", 1920),
            height=settings.get("height", 1080),
            fps=settings.get("fps", 30.0),
            duration=self.project.duration,
            seed=self.project.seed,
            supersample_scale=settings.get("supersample_scale", 1),
            accumulation_samples=settings.get("accumulation_samples", 1)
        )
        
        # Connect worker signals
        self.render_worker.progress.connect(self.export_dock.update_progress)
        self.render_worker.log_message.connect(self.export_dock.add_log)
        self.render_worker.finished.connect(self._on_render_finished)
        self.render_worker.error.connect(self._on_render_error)
        
        # Create and start thread
        self.render_thread = create_render_thread(self.render_worker)
        self.render_thread.start()
        
        self.export_dock.set_rendering(True)
        self.status_bar.showMessage("Rendering started...", 2000)
    
    @Slot(bool)
    def _on_render_finished(self, success: bool):
        """Handle render completion."""
        self.export_dock.set_rendering(False)
        
        if success:
            # Check if we should encode video
            settings = self.export_dock.get_settings()
            if settings.get("encode_video"):
                self._encode_video(settings)
            else:
                self.status_bar.showMessage("Render complete!", 3000)
                QMessageBox.information(
                    self,
                    "Render Complete",
                    f"Frames saved to: {settings['output_dir']}"
                )
    
    @Slot(str)
    def _on_render_error(self, message: str):
        """Handle render error."""
        self.status_bar.showMessage(f"Render error: {message}", 5000)
        QMessageBox.critical(self, "Render Error", message)
    
    def _encode_video(self, settings: dict):
        """Encode rendered frames to video.
        
        Args:
            settings: Export settings dictionary
        """
        from ..encode.ffmpeg import encode_frames
        
        output_dir = settings["output_dir"]
        fps = settings.get("fps", 30.0)
        codec = settings.get("codec", "h264_high")
        
        video_path = os.path.join(output_dir, "output.mp4")
        
        self.export_dock.add_log("Starting video encoding...")
        
        success = encode_frames(
            frames_dir=output_dir,
            output_path=video_path,
            fps=fps,
            preset=codec,
            log_callback=self.export_dock.add_log
        )
        
        if success:
            self.status_bar.showMessage("Video encoded successfully!", 3000)
            QMessageBox.information(
                self,
                "Encoding Complete",
                f"Video saved to: {video_path}"
            )
        else:
            self.status_bar.showMessage("Video encoding failed", 3000)
    
    @Slot()
    def _new_project(self):
        """Create a new project."""
        self.project = Project()
        self.project_path = None
        self.setWindowTitle("LoopLab - GLSL Loop Shader Tool")
        self._load_default_shader()
    
    @Slot()
    def _open_project(self):
        """Open a project file."""
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Project",
            "",
            "LoopLab Project (*.llp);;All Files (*)"
        )
        if path:
            project = load_project(path)
            if project:
                self.project = project
                self.project_path = Path(path)
                self.setWindowTitle(f"LoopLab - {self.project_path.name}")
                
                # Load shader
                if self.project.shader_path:
                    self._load_shader(self.project.shader_path)
                
                # Apply settings
                self.preview_widget.set_seed(self.project.seed)
                self.parameters_dock.set_seed(self.project.seed)
                
                self.status_bar.showMessage(f"Opened: {path}", 3000)
            else:
                QMessageBox.critical(self, "Error", "Failed to open project")
    
    @Slot()
    def _save_project(self):
        """Save the current project."""
        if self.project_path:
            if save_project(self.project, self.project_path):
                self.status_bar.showMessage(f"Saved: {self.project_path}", 2000)
            else:
                QMessageBox.critical(self, "Error", "Failed to save project")
        else:
            self._save_project_as()
    
    @Slot()
    def _save_project_as(self):
        """Save the project with a new name."""
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Project",
            "",
            "LoopLab Project (*.llp);;All Files (*)"
        )
        if path:
            if not path.endswith('.llp'):
                path += '.llp'
            
            if save_project(self.project, path):
                self.project_path = Path(path)
                self.setWindowTitle(f"LoopLab - {self.project_path.name}")
                self.status_bar.showMessage(f"Saved: {path}", 2000)
            else:
                QMessageBox.critical(self, "Error", "Failed to save project")
    
    @Slot()
    def _show_about(self):
        """Show about dialog."""
        QMessageBox.about(
            self,
            "About LoopLab",
            "LoopLab v0.1.0\n\n"
            "AI-assisted GLSL loop shader tool with preview, "
            "offline render, and FFmpeg encode.\n\n"
            "Create mathematically guaranteed 30-second loops."
        )
    
    def closeEvent(self, event):
        """Handle window close."""
        # Clean up preview widget
        self.preview_widget.cleanup()
        
        # Stop any running render
        if hasattr(self, 'render_worker'):
            self.render_worker.cancel()
        
        event.accept()
