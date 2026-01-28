"""Timeline module for frame/time/phase calculations.

This module provides the core time mapping that guarantees perfect loops.
Duration is fixed at 30.0 seconds by default, and all motion is based on
the phase value (0 to 2π) rather than wall-clock time.
"""

import math
from dataclasses import dataclass
from typing import NamedTuple


class FrameInfo(NamedTuple):
    """Information for a single frame in the timeline."""
    
    frame: int
    time: float
    phase: float
    loop_x: float  # cos(phase)
    loop_y: float  # sin(phase)


@dataclass
class Timeline:
    """Timeline for loop-based animation.
    
    Attributes:
        duration: Loop duration in seconds (default: 30.0)
        fps: Frames per second
    """
    
    duration: float = 30.0
    fps: float = 30.0
    
    @property
    def total_frames(self) -> int:
        """Total number of frames in the loop."""
        return int(self.fps * self.duration)
    
    def get_frame_info(self, frame: int) -> FrameInfo:
        """Get time/phase information for a specific frame.
        
        Args:
            frame: Frame index (0 to total_frames - 1)
            
        Returns:
            FrameInfo with time, phase, and loop vector components
        """
        # Clamp frame to valid range
        frame = max(0, min(frame, self.total_frames - 1))
        
        # Time in seconds
        time = frame / self.fps
        
        # Phase wraps exactly at duration (0 to 2π)
        phase = 2.0 * math.pi * (time / self.duration)
        
        # Loop vector components
        loop_x = math.cos(phase)
        loop_y = math.sin(phase)
        
        return FrameInfo(
            frame=frame,
            time=time,
            phase=phase,
            loop_x=loop_x,
            loop_y=loop_y
        )
    
    def get_frame_from_time(self, time: float) -> int:
        """Get the frame index for a given time.
        
        Args:
            time: Time in seconds (clamped to [0, duration))
            
        Returns:
            Frame index
        """
        # Clamp time to valid range
        time = max(0.0, min(time, self.duration - (1.0 / self.fps)))
        return int(time * self.fps)
    
    def get_frame_from_phase(self, phase: float) -> int:
        """Get the frame index for a given phase.
        
        Args:
            phase: Phase in radians (0 to 2π)
            
        Returns:
            Frame index
        """
        # Convert phase to time
        time = (phase / (2.0 * math.pi)) * self.duration
        return self.get_frame_from_time(time)
    
    def validate_fps(self) -> bool:
        """Check if fps produces an integer number of frames.
        
        Returns:
            True if fps * duration is an integer
        """
        frames = self.fps * self.duration
        return abs(frames - round(frames)) < 1e-9
    
    def iter_frames(self):
        """Iterate over all frames in the timeline.
        
        Yields:
            FrameInfo for each frame
        """
        for frame in range(self.total_frames):
            yield self.get_frame_info(frame)
