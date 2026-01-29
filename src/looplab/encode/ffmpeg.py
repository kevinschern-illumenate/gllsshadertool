"""FFmpeg integration for video encoding.

This module provides utilities for encoding image sequences
into video files using FFmpeg.
"""

import subprocess
import shutil
from pathlib import Path
from typing import Optional, List, Callable
from dataclasses import dataclass
from enum import Enum


class VideoCodec(Enum):
    """Supported video codecs."""
    H264 = "h264"
    H265 = "h265"
    PRORES = "prores"
    AVI = "avi"


@dataclass
class EncodingPreset:
    """Video encoding preset configuration."""
    
    name: str
    codec: VideoCodec
    extension: str
    ffmpeg_args: List[str]


# Predefined encoding presets
PRESETS = {
    "h264_high": EncodingPreset(
        name="H.264 High Quality",
        codec=VideoCodec.H264,
        extension="mp4",
        ffmpeg_args=[
            "-c:v", "libx264",
            "-preset", "slow",
            "-crf", "18",
            "-pix_fmt", "yuv420p",
        ]
    ),
    "h264_medium": EncodingPreset(
        name="H.264 Medium Quality",
        codec=VideoCodec.H264,
        extension="mp4",
        ffmpeg_args=[
            "-c:v", "libx264",
            "-preset", "medium",
            "-crf", "23",
            "-pix_fmt", "yuv420p",
        ]
    ),
    "h264_compat": EncodingPreset(
        name="H.264 Compatible",
        codec=VideoCodec.H264,
        extension="mp4",
        ffmpeg_args=[
            "-c:v", "libx264",
            "-preset", "medium",
            "-crf", "20",
            "-profile:v", "baseline",
            "-level", "3.0",
            "-pix_fmt", "yuv420p",
        ]
    ),
    "h265_high": EncodingPreset(
        name="H.265 High Quality",
        codec=VideoCodec.H265,
        extension="mp4",
        ffmpeg_args=[
            "-c:v", "libx265",
            "-preset", "slow",
            "-crf", "20",
            "-pix_fmt", "yuv420p",
        ]
    ),
    "prores_422": EncodingPreset(
        name="ProRes 422 HQ",
        codec=VideoCodec.PRORES,
        extension="mov",
        ffmpeg_args=[
            "-c:v", "prores_ks",
            "-profile:v", "3",  # HQ profile
            "-pix_fmt", "yuv422p10le",
        ]
    ),
    "prores_4444": EncodingPreset(
        name="ProRes 4444",
        codec=VideoCodec.PRORES,
        extension="mov",
        ffmpeg_args=[
            "-c:v", "prores_ks",
            "-profile:v", "4",  # 4444 profile
            "-pix_fmt", "yuva444p10le",
        ]
    ),
    "avi_mjpeg": EncodingPreset(
        name="AVI (Motion JPEG)",
        codec=VideoCodec.AVI,
        extension="avi",
        ffmpeg_args=[
            "-c:v", "mjpeg",
            "-q:v", "3",  # Quality 1-31, lower is better
            "-pix_fmt", "yuvj420p",
        ]
    ),
    "avi_uncompressed": EncodingPreset(
        name="AVI (Uncompressed)",
        codec=VideoCodec.AVI,
        extension="avi",
        ffmpeg_args=[
            "-c:v", "rawvideo",
            "-pix_fmt", "rgb24",
        ]
    ),
    "avi_huffyuv": EncodingPreset(
        name="AVI (Lossless HuffYUV)",
        codec=VideoCodec.AVI,
        extension="avi",
        ffmpeg_args=[
            "-c:v", "huffyuv",
            "-pix_fmt", "rgb24",
        ]
    ),
}


def find_ffmpeg() -> Optional[str]:
    """Find FFmpeg executable.
    
    Returns:
        Path to FFmpeg or None if not found
    """
    # First try the system PATH
    ffmpeg_path = shutil.which("ffmpeg")
    if ffmpeg_path:
        return ffmpeg_path
    
    # Check common installation locations on Windows
    import os
    common_paths = [
        # Winget installation
        os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\WinGet\Packages"),
        # Chocolatey
        r"C:\ProgramData\chocolatey\bin",
        # Scoop
        os.path.expandvars(r"%USERPROFILE%\scoop\shims"),
        # Manual install locations
        r"C:\ffmpeg\bin",
        r"C:\Program Files\ffmpeg\bin",
        r"C:\Program Files (x86)\ffmpeg\bin",
    ]
    
    for base_path in common_paths:
        if not os.path.exists(base_path):
            continue
        
        # Direct check
        direct_path = os.path.join(base_path, "ffmpeg.exe")
        if os.path.isfile(direct_path):
            return direct_path
        
        # Search in subdirectories (for winget packages)
        try:
            for root, dirs, files in os.walk(base_path):
                if "ffmpeg.exe" in files:
                    return os.path.join(root, "ffmpeg.exe")
                # Limit search depth
                if root.count(os.sep) - base_path.count(os.sep) > 4:
                    break
        except (PermissionError, OSError):
            continue
    
    return None


def get_ffmpeg_version() -> Optional[str]:
    """Get FFmpeg version string.
    
    Returns:
        Version string or None if FFmpeg not available
    """
    ffmpeg = find_ffmpeg()
    if not ffmpeg:
        return None
    
    try:
        result = subprocess.run(
            [ffmpeg, "-version"],
            capture_output=True,
            text=True,
            timeout=10
        )
        # Extract first line (version info)
        lines = result.stdout.strip().split('\n')
        if lines:
            return lines[0]
    except (subprocess.TimeoutExpired, subprocess.SubprocessError):
        pass
    
    return None


class FFmpegEncoder:
    """FFmpeg-based video encoder."""
    
    def __init__(self, ffmpeg_path: Optional[str] = None):
        """Initialize encoder.
        
        Args:
            ffmpeg_path: Path to FFmpeg, or None to auto-detect
        """
        self.ffmpeg_path = ffmpeg_path or find_ffmpeg()
        self.process: Optional[subprocess.Popen] = None
    
    def is_available(self) -> bool:
        """Check if FFmpeg is available."""
        return self.ffmpeg_path is not None
    
    def encode_sequence(
        self,
        input_pattern: str,
        output_path: str,
        fps: float,
        preset: str = "h264_high",
        progress_callback: Optional[Callable[[int, int], None]] = None,
        log_callback: Optional[Callable[[str], None]] = None
    ) -> bool:
        """Encode an image sequence to video.
        
        Args:
            input_pattern: Input file pattern (e.g., "frames/frame_%06d.png")
            output_path: Output video file path
            fps: Frame rate
            preset: Encoding preset name
            progress_callback: Called with (current_frame, total_frames)
            log_callback: Called with log messages
            
        Returns:
            True if encoding succeeded
        """
        if not self.is_available():
            if log_callback:
                log_callback("FFmpeg not available")
            return False
        
        if preset not in PRESETS:
            if log_callback:
                log_callback(f"Unknown preset: {preset}")
            return False
        
        encoding = PRESETS[preset]
        
        # Build FFmpeg command
        cmd = [
            self.ffmpeg_path,
            "-y",  # Overwrite output
            "-framerate", str(fps),
            "-i", input_pattern,
            *encoding.ffmpeg_args,
            output_path
        ]
        
        if log_callback:
            log_callback(f"Running: {' '.join(cmd)}")
        
        try:
            # Run FFmpeg
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Wait for completion
            stdout, stderr = self.process.communicate()
            
            if self.process.returncode != 0:
                if log_callback:
                    log_callback(f"FFmpeg error: {stderr}")
                return False
            
            if log_callback:
                log_callback(f"Encoding complete: {output_path}")
            
            return True
            
        except subprocess.SubprocessError as e:
            if log_callback:
                log_callback(f"Encoding failed: {e}")
            return False
        finally:
            self.process = None
    
    def cancel(self):
        """Cancel ongoing encoding."""
        if self.process:
            self.process.terminate()
            self.process = None


def encode_frames(
    frames_dir: str,
    output_path: str,
    fps: float,
    preset: str = "h264_high",
    frame_pattern: str = "frame_%06d.png",
    log_callback: Optional[Callable[[str], None]] = None
) -> bool:
    """Convenience function to encode frames from a directory.
    
    Args:
        frames_dir: Directory containing frame images
        output_path: Output video file path
        fps: Frame rate
        preset: Encoding preset name
        frame_pattern: Frame filename pattern
        log_callback: Called with log messages
        
    Returns:
        True if encoding succeeded
    """
    encoder = FFmpegEncoder()
    
    if not encoder.is_available():
        if log_callback:
            log_callback("FFmpeg not found. Please install FFmpeg.")
        return False
    
    input_pattern = str(Path(frames_dir) / frame_pattern)
    
    # Ensure output has correct extension
    encoding = PRESETS.get(preset)
    if encoding:
        output_path_obj = Path(output_path)
        if output_path_obj.suffix.lower() != f".{encoding.extension}":
            output_path = str(output_path_obj.with_suffix(f".{encoding.extension}"))
    
    return encoder.encode_sequence(
        input_pattern=input_pattern,
        output_path=output_path,
        fps=fps,
        preset=preset,
        log_callback=log_callback
    )
