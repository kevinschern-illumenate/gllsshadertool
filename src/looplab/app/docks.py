"""Dock widgets for the LoopLab UI.

This module provides dockable panels for:
- Shader loading/reloading
- Timeline and transport controls
- Parameter editing
- Export settings
"""

import os
from pathlib import Path
from typing import Optional, List

from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtWidgets import (
    QDockWidget, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QSlider, QSpinBox, QDoubleSpinBox,
    QCheckBox, QComboBox, QLineEdit, QTextEdit, QGroupBox,
    QFormLayout, QProgressBar, QFileDialog, QScrollArea,
    QFrame
)

from ..gl.uniforms import UserParameter


class ShaderDock(QDockWidget):
    """Dock for shader file management."""
    
    load_clicked = Signal()
    reload_clicked = Signal()
    auto_reload_changed = Signal(bool)
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__("Shader", parent)
        self.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea | 
                            Qt.DockWidgetArea.RightDockWidgetArea)
        
        # Main widget
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # File section
        file_group = QGroupBox("Shader File")
        file_layout = QVBoxLayout(file_group)
        
        # Path display
        self.path_label = QLabel("No shader loaded")
        self.path_label.setWordWrap(True)
        file_layout.addWidget(self.path_label)
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        self.load_btn = QPushButton("Load...")
        self.load_btn.clicked.connect(self.load_clicked)
        btn_layout.addWidget(self.load_btn)
        
        self.reload_btn = QPushButton("Reload")
        self.reload_btn.clicked.connect(self.reload_clicked)
        btn_layout.addWidget(self.reload_btn)
        
        file_layout.addLayout(btn_layout)
        
        # Auto-reload checkbox
        self.auto_reload_cb = QCheckBox("Auto-reload on save")
        self.auto_reload_cb.setChecked(True)
        self.auto_reload_cb.toggled.connect(self.auto_reload_changed)
        file_layout.addWidget(self.auto_reload_cb)
        
        layout.addWidget(file_group)
        
        # Compile status
        status_group = QGroupBox("Compile Status")
        status_layout = QVBoxLayout(status_group)
        
        self.status_label = QLabel("Ready")
        status_layout.addWidget(self.status_label)
        
        self.error_text = QTextEdit()
        self.error_text.setReadOnly(True)
        self.error_text.setMaximumHeight(150)
        self.error_text.setStyleSheet("font-family: monospace;")
        self.error_text.hide()
        status_layout.addWidget(self.error_text)
        
        layout.addWidget(status_group)
        
        # Spacer
        layout.addStretch()
        
        self.setWidget(widget)
    
    def set_shader_path(self, path: str):
        """Update displayed shader path."""
        name = Path(path).name
        self.path_label.setText(f"<b>{name}</b><br><small>{path}</small>")
    
    def set_compile_status(self, success: bool, message: str):
        """Update compile status display."""
        if success:
            self.status_label.setText("✓ Compiled successfully")
            self.status_label.setStyleSheet("color: green;")
            self.error_text.hide()
        else:
            self.status_label.setText("✗ Compilation failed")
            self.status_label.setStyleSheet("color: red;")
            self.error_text.setText(message)
            self.error_text.show()


class TimelineDock(QDockWidget):
    """Dock for timeline and transport controls."""
    
    play_clicked = Signal()
    time_changed = Signal(float)
    fps_changed = Signal(float)
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__("Timeline", parent)
        self.setAllowedAreas(Qt.DockWidgetArea.TopDockWidgetArea | 
                            Qt.DockWidgetArea.BottomDockWidgetArea)
        
        # Main widget
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Timeline slider
        slider_layout = QHBoxLayout()
        
        self.time_label = QLabel("0.00s")
        self.time_label.setMinimumWidth(60)
        slider_layout.addWidget(self.time_label)
        
        self.timeline_slider = QSlider(Qt.Orientation.Horizontal)
        self.timeline_slider.setMinimum(0)
        self.timeline_slider.setMaximum(30000)  # milliseconds
        self.timeline_slider.valueChanged.connect(self._on_slider_changed)
        slider_layout.addWidget(self.timeline_slider)
        
        self.duration_label = QLabel("30.00s")
        self.duration_label.setMinimumWidth(60)
        slider_layout.addWidget(self.duration_label)
        
        layout.addLayout(slider_layout)
        
        # Transport controls
        transport_layout = QHBoxLayout()
        
        self.play_btn = QPushButton("▶ Play")
        self.play_btn.setCheckable(True)
        self.play_btn.clicked.connect(self._on_play_clicked)
        transport_layout.addWidget(self.play_btn)
        
        transport_layout.addStretch()
        
        # Frame counter
        frame_label = QLabel("Frame:")
        transport_layout.addWidget(frame_label)
        
        self.frame_spin = QSpinBox()
        self.frame_spin.setMinimum(0)
        self.frame_spin.setMaximum(899)
        self.frame_spin.valueChanged.connect(self._on_frame_changed)
        transport_layout.addWidget(self.frame_spin)
        
        transport_layout.addStretch()
        
        # FPS control
        fps_label = QLabel("FPS:")
        transport_layout.addWidget(fps_label)
        
        self.fps_combo = QComboBox()
        self.fps_combo.addItems(["24", "25", "30", "50", "60"])
        self.fps_combo.setCurrentText("30")
        self.fps_combo.currentTextChanged.connect(self._on_fps_combo_changed)
        transport_layout.addWidget(self.fps_combo)
        
        layout.addLayout(transport_layout)
        
        self.setWidget(widget)
        
        # State
        self._duration = 30.0
        self._fps = 30.0
    
    def _on_slider_changed(self, value: int):
        """Handle timeline slider change."""
        time = value / 1000.0
        self.time_label.setText(f"{time:.2f}s")
        self.time_changed.emit(time)
        
        # Update frame spinbox
        frame = int(time * self._fps)
        self.frame_spin.blockSignals(True)
        self.frame_spin.setValue(frame)
        self.frame_spin.blockSignals(False)
    
    def _on_frame_changed(self, frame: int):
        """Handle frame spinbox change."""
        time = frame / self._fps
        self.timeline_slider.blockSignals(True)
        self.timeline_slider.setValue(int(time * 1000))
        self.timeline_slider.blockSignals(False)
        self.time_label.setText(f"{time:.2f}s")
        self.time_changed.emit(time)
    
    def _on_play_clicked(self):
        """Handle play button click."""
        self.play_clicked.emit()
    
    def _on_fps_combo_changed(self, text: str):
        """Handle FPS combo change."""
        try:
            fps = float(text)
            self._fps = fps
            self.frame_spin.setMaximum(int(self._duration * fps) - 1)
            self.fps_changed.emit(fps)
        except ValueError:
            pass
    
    def set_playing(self, playing: bool):
        """Update play button state."""
        self.play_btn.setChecked(playing)
        self.play_btn.setText("⏸ Pause" if playing else "▶ Play")
    
    def set_time(self, time: float):
        """Set current time position."""
        self.timeline_slider.blockSignals(True)
        self.timeline_slider.setValue(int(time * 1000))
        self.timeline_slider.blockSignals(False)
        self.time_label.setText(f"{time:.2f}s")


class ParametersDock(QDockWidget):
    """Dock for shader parameter controls."""
    
    seed_changed = Signal(float)
    randomize_seed_clicked = Signal()
    parameter_changed = Signal(str, object)  # name, value
    
    # Library compatibility signals
    complexity_changed = Signal(int)
    force_changed = Signal(float)
    force2_changed = Signal(float)
    base_hue_changed = Signal(float)
    color_mode_changed = Signal(int)
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__("Parameters", parent)
        self.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea | 
                            Qt.DockWidgetArea.RightDockWidgetArea)
        
        # Main widget with scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        widget = QWidget()
        self.layout = QVBoxLayout(widget)
        
        # Seed control
        seed_group = QGroupBox("Random Seed")
        seed_layout = QHBoxLayout(seed_group)
        
        self.seed_spin = QDoubleSpinBox()
        self.seed_spin.setRange(0, 10000)
        self.seed_spin.setDecimals(4)
        self.seed_spin.valueChanged.connect(self.seed_changed)
        seed_layout.addWidget(self.seed_spin)
        
        self.randomize_btn = QPushButton("🎲")
        self.randomize_btn.setMaximumWidth(40)
        self.randomize_btn.clicked.connect(self.randomize_seed_clicked)
        seed_layout.addWidget(self.randomize_btn)
        
        self.layout.addWidget(seed_group)
        
        # Library compatibility controls
        lib_group = QGroupBox("Shader Controls")
        lib_layout = QFormLayout(lib_group)
        
        # Complexity (iComplexity) - 1 to 10
        self.complexity_spin = QSpinBox()
        self.complexity_spin.setRange(1, 10)
        self.complexity_spin.setValue(5)
        self.complexity_spin.setToolTip("Detail/quality level (iComplexity)")
        self.complexity_spin.valueChanged.connect(self.complexity_changed)
        lib_layout.addRow("Complexity:", self.complexity_spin)
        
        # Force (iForce) - 0 to 10
        self.force_spin = QDoubleSpinBox()
        self.force_spin.setRange(0.0, 10.0)
        self.force_spin.setValue(5.0)
        self.force_spin.setDecimals(2)
        self.force_spin.setSingleStep(0.1)
        self.force_spin.setToolTip("Primary intensity (iForce)")
        self.force_spin.valueChanged.connect(self.force_changed)
        lib_layout.addRow("Force:", self.force_spin)
        
        # Force2 (iForce2) - 0 to 10
        self.force2_spin = QDoubleSpinBox()
        self.force2_spin.setRange(0.0, 10.0)
        self.force2_spin.setValue(5.0)
        self.force2_spin.setDecimals(2)
        self.force2_spin.setSingleStep(0.1)
        self.force2_spin.setToolTip("Secondary intensity (iForce2)")
        self.force2_spin.valueChanged.connect(self.force2_changed)
        lib_layout.addRow("Force 2:", self.force2_spin)
        
        # Base Hue (iBaseHueRad) - 0 to 6.28 (TAU)
        self.hue_spin = QDoubleSpinBox()
        self.hue_spin.setRange(0.0, 6.28)
        self.hue_spin.setValue(0.0)
        self.hue_spin.setDecimals(2)
        self.hue_spin.setSingleStep(0.1)
        self.hue_spin.setToolTip("Base hue in radians (iBaseHueRad)")
        self.hue_spin.valueChanged.connect(self.base_hue_changed)
        lib_layout.addRow("Base Hue:", self.hue_spin)
        
        # Color Mode (mColorMode) - 0 or 1
        self.color_mode_combo = QComboBox()
        self.color_mode_combo.addItems(["Mode 0", "Mode 1"])
        self.color_mode_combo.setToolTip("Color mode toggle (mColorMode)")
        self.color_mode_combo.currentIndexChanged.connect(self.color_mode_changed)
        lib_layout.addRow("Color Mode:", self.color_mode_combo)
        
        self.layout.addWidget(lib_group)
        
        # Parameters container (for @param style parameters)
        self.params_group = QGroupBox("Shader Parameters")
        self.params_layout = QFormLayout(self.params_group)
        self.layout.addWidget(self.params_group)
        
        # Spacer
        self.layout.addStretch()
        
        scroll.setWidget(widget)
        self.setWidget(scroll)
        
        # Store parameter widgets
        self._param_widgets = {}
    
    def set_seed(self, seed: float):
        """Set seed value."""
        self.seed_spin.blockSignals(True)
        self.seed_spin.setValue(seed)
        self.seed_spin.blockSignals(False)
    
    def update_parameters(self, params: List[UserParameter]):
        """Update parameter controls from shader.
        
        Args:
            params: List of parsed UserParameter objects
        """
        # Clear existing
        while self.params_layout.count():
            item = self.params_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self._param_widgets.clear()
        
        # Add new controls
        for param in params:
            widget = self._create_param_widget(param)
            if widget:
                self.params_layout.addRow(param.name, widget)
                self._param_widgets[param.name] = widget
        
        # Show/hide group
        self.params_group.setVisible(len(params) > 0)
    
    def _create_param_widget(self, param: UserParameter) -> Optional[QWidget]:
        """Create appropriate widget for parameter type."""
        if param.param_type == "float":
            spin = QDoubleSpinBox()
            spin.setRange(param.min_value or 0.0, param.max_value or 1.0)
            spin.setDecimals(3)
            spin.setSingleStep(0.01)
            if param.default_value is not None:
                spin.setValue(param.default_value)
            spin.valueChanged.connect(
                lambda v, n=param.name: self.parameter_changed.emit(n, v)
            )
            return spin
        
        elif param.param_type == "color":
            # Simple color as 3 spinboxes (would use QColorDialog in full version)
            container = QWidget()
            layout = QHBoxLayout(container)
            layout.setContentsMargins(0, 0, 0, 0)
            
            for i, channel in enumerate(['R', 'G', 'B']):
                spin = QDoubleSpinBox()
                spin.setRange(0.0, 1.0)
                spin.setDecimals(2)
                spin.setSingleStep(0.05)
                if param.default_value:
                    spin.setValue(param.default_value[i])
                layout.addWidget(spin)
            
            return container
        
        return None


class ExportDock(QDockWidget):
    """Dock for export settings and render control."""
    
    render_clicked = Signal()
    cancel_clicked = Signal()
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__("Export", parent)
        self.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea | 
                            Qt.DockWidgetArea.RightDockWidgetArea)
        
        # Main widget
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Output settings
        output_group = QGroupBox("Output Settings")
        output_layout = QFormLayout(output_group)
        
        # Output directory
        dir_container = QWidget()
        dir_layout = QHBoxLayout(dir_container)
        dir_layout.setContentsMargins(0, 0, 0, 0)
        
        self.dir_edit = QLineEdit()
        self.dir_edit.setPlaceholderText("Select output directory...")
        dir_layout.addWidget(self.dir_edit)
        
        browse_btn = QPushButton("...")
        browse_btn.setMaximumWidth(30)
        browse_btn.clicked.connect(self._browse_output)
        dir_layout.addWidget(browse_btn)
        
        output_layout.addRow("Directory:", dir_container)
        
        # Resolution
        res_container = QWidget()
        res_layout = QHBoxLayout(res_container)
        res_layout.setContentsMargins(0, 0, 0, 0)
        
        self.width_spin = QSpinBox()
        self.width_spin.setRange(64, 8192)
        self.width_spin.setValue(1920)
        res_layout.addWidget(self.width_spin)
        
        res_layout.addWidget(QLabel("×"))
        
        self.height_spin = QSpinBox()
        self.height_spin.setRange(64, 8192)
        self.height_spin.setValue(1080)
        res_layout.addWidget(self.height_spin)
        
        output_layout.addRow("Resolution:", res_container)
        
        # FPS
        self.fps_spin = QDoubleSpinBox()
        self.fps_spin.setRange(1, 120)
        self.fps_spin.setValue(30)
        output_layout.addRow("FPS:", self.fps_spin)
        
        layout.addWidget(output_group)
        
        # Quality settings
        quality_group = QGroupBox("Quality")
        quality_layout = QFormLayout(quality_group)
        
        self.supersample_combo = QComboBox()
        self.supersample_combo.addItems(["1x", "2x", "4x"])
        quality_layout.addRow("Supersample:", self.supersample_combo)
        
        self.accumulation_spin = QSpinBox()
        self.accumulation_spin.setRange(1, 64)
        self.accumulation_spin.setValue(1)
        quality_layout.addRow("Accumulation:", self.accumulation_spin)
        
        layout.addWidget(quality_group)
        
        # Export options
        options_group = QGroupBox("Options")
        options_layout = QVBoxLayout(options_group)
        
        self.save_png_cb = QCheckBox("Save PNG sequence")
        self.save_png_cb.setChecked(True)
        self.save_png_cb.setEnabled(False)  # Always on for now
        options_layout.addWidget(self.save_png_cb)
        
        self.encode_video_cb = QCheckBox("Encode video")
        self.encode_video_cb.setChecked(True)
        options_layout.addWidget(self.encode_video_cb)
        
        # Codec
        codec_layout = QHBoxLayout()
        codec_layout.addWidget(QLabel("Codec:"))
        
        self.codec_combo = QComboBox()
        self.codec_combo.addItems([
            "h264_high", "h264_medium", "h264_compat",
            "h265_high", "prores_422", "prores_4444",
            "avi_mjpeg", "avi_uncompressed", "avi_huffyuv"
        ])
        codec_layout.addWidget(self.codec_combo)
        options_layout.addLayout(codec_layout)
        
        layout.addWidget(options_group)
        
        # Progress
        progress_group = QGroupBox("Progress")
        progress_layout = QVBoxLayout(progress_group)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        progress_layout.addWidget(self.progress_bar)
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(100)
        self.log_text.setStyleSheet("font-family: monospace; font-size: 10px;")
        progress_layout.addWidget(self.log_text)
        
        layout.addWidget(progress_group)
        
        # Render button
        self.render_btn = QPushButton("🎬 Start Render")
        self.render_btn.clicked.connect(self._on_render_clicked)
        layout.addWidget(self.render_btn)
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.cancel_clicked)
        self.cancel_btn.hide()
        layout.addWidget(self.cancel_btn)
        
        # Spacer
        layout.addStretch()
        
        self.setWidget(widget)
        
        self._rendering = False
    
    def _browse_output(self):
        """Browse for output directory."""
        dir_path = QFileDialog.getExistingDirectory(
            self,
            "Select Output Directory"
        )
        if dir_path:
            self.dir_edit.setText(dir_path)
    
    def _on_render_clicked(self):
        """Handle render button click."""
        self.render_clicked.emit()
    
    def get_settings(self) -> dict:
        """Get current export settings."""
        ss_map = {"1x": 1, "2x": 2, "4x": 4}
        return {
            "output_dir": self.dir_edit.text(),
            "width": self.width_spin.value(),
            "height": self.height_spin.value(),
            "fps": self.fps_spin.value(),
            "supersample_scale": ss_map.get(self.supersample_combo.currentText(), 1),
            "accumulation_samples": self.accumulation_spin.value(),
            "save_png": self.save_png_cb.isChecked(),
            "encode_video": self.encode_video_cb.isChecked(),
            "codec": self.codec_combo.currentText(),
        }
    
    def set_rendering(self, rendering: bool):
        """Update UI for render state."""
        self._rendering = rendering
        self.render_btn.setVisible(not rendering)
        self.cancel_btn.setVisible(rendering)
        
        # Disable settings during render
        self.dir_edit.setEnabled(not rendering)
        self.width_spin.setEnabled(not rendering)
        self.height_spin.setEnabled(not rendering)
        self.fps_spin.setEnabled(not rendering)
        self.supersample_combo.setEnabled(not rendering)
        self.accumulation_spin.setEnabled(not rendering)
    
    def update_progress(self, current: int, total: int):
        """Update progress bar."""
        self.progress_bar.setMaximum(total)
        self.progress_bar.setValue(current)
    
    def add_log(self, message: str):
        """Add message to log."""
        self.log_text.append(message)
        # Scroll to bottom
        scrollbar = self.log_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
