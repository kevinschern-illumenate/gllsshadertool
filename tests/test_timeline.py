"""Tests for timeline module."""

import math
import pytest

# Import the module under test
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from looplab.render.timeline import Timeline, FrameInfo


class TestTimeline:
    """Tests for Timeline class."""
    
    def test_default_values(self):
        """Test default timeline values."""
        timeline = Timeline()
        assert timeline.duration == 30.0
        assert timeline.fps == 30.0
    
    def test_total_frames(self):
        """Test total frame calculation."""
        timeline = Timeline(duration=30.0, fps=30.0)
        assert timeline.total_frames == 900
        
        timeline = Timeline(duration=30.0, fps=60.0)
        assert timeline.total_frames == 1800
        
        timeline = Timeline(duration=10.0, fps=24.0)
        assert timeline.total_frames == 240
    
    def test_frame_info_first_frame(self):
        """Test frame info for first frame."""
        timeline = Timeline(duration=30.0, fps=30.0)
        info = timeline.get_frame_info(0)
        
        assert info.frame == 0
        assert info.time == 0.0
        assert info.phase == 0.0
        assert info.loop_x == pytest.approx(1.0)  # cos(0)
        assert info.loop_y == pytest.approx(0.0)  # sin(0)
    
    def test_frame_info_middle_frame(self):
        """Test frame info for middle frame (half loop)."""
        timeline = Timeline(duration=30.0, fps=30.0)
        # Frame 450 = 15 seconds = half way
        info = timeline.get_frame_info(450)
        
        assert info.frame == 450
        assert info.time == pytest.approx(15.0)
        assert info.phase == pytest.approx(math.pi)
        assert info.loop_x == pytest.approx(-1.0)  # cos(π)
        assert info.loop_y == pytest.approx(0.0, abs=1e-10)  # sin(π)
    
    def test_frame_info_last_frame(self):
        """Test frame info for last frame (near loop point)."""
        timeline = Timeline(duration=30.0, fps=30.0)
        info = timeline.get_frame_info(899)
        
        assert info.frame == 899
        assert info.time == pytest.approx(899 / 30.0)
        
        # Phase should be close to 2π but not quite
        expected_phase = 2.0 * math.pi * (899 / 30.0 / 30.0)
        assert info.phase == pytest.approx(expected_phase)
    
    def test_loop_continuity(self):
        """Test that first and last+1 frames would be continuous."""
        timeline = Timeline(duration=30.0, fps=30.0)
        
        first = timeline.get_frame_info(0)
        last = timeline.get_frame_info(899)
        
        # The difference in phase should be exactly 1 frame worth
        frame_phase = 2.0 * math.pi / 900.0
        expected_diff = 2.0 * math.pi - frame_phase
        
        assert last.phase == pytest.approx(expected_diff, abs=1e-10)
    
    def test_get_frame_from_time(self):
        """Test time to frame conversion."""
        timeline = Timeline(duration=30.0, fps=30.0)
        
        assert timeline.get_frame_from_time(0.0) == 0
        assert timeline.get_frame_from_time(15.0) == 450
        assert timeline.get_frame_from_time(29.9) == 897
    
    def test_get_frame_from_phase(self):
        """Test phase to frame conversion."""
        timeline = Timeline(duration=30.0, fps=30.0)
        
        assert timeline.get_frame_from_phase(0.0) == 0
        assert timeline.get_frame_from_phase(math.pi) == 450
    
    def test_validate_fps(self):
        """Test FPS validation for integer frame counts."""
        # Valid FPS values
        timeline = Timeline(duration=30.0, fps=30.0)
        assert timeline.validate_fps() is True
        
        timeline = Timeline(duration=30.0, fps=60.0)
        assert timeline.validate_fps() is True
        
        timeline = Timeline(duration=30.0, fps=24.0)
        assert timeline.validate_fps() is True
        
        # Invalid FPS (would produce non-integer frames)
        timeline = Timeline(duration=30.0, fps=29.97)
        # 29.97 * 30 = 899.1, not an integer
        assert timeline.validate_fps() is False
    
    def test_iter_frames(self):
        """Test iteration over all frames."""
        timeline = Timeline(duration=30.0, fps=30.0)
        
        frames = list(timeline.iter_frames())
        
        assert len(frames) == 900
        assert frames[0].frame == 0
        assert frames[899].frame == 899
        
        # Check all frames are unique
        frame_numbers = [f.frame for f in frames]
        assert len(set(frame_numbers)) == 900
    
    def test_clamp_frame(self):
        """Test that out-of-range frames are clamped."""
        timeline = Timeline(duration=30.0, fps=30.0)
        
        # Negative frame
        info = timeline.get_frame_info(-10)
        assert info.frame == 0
        
        # Beyond last frame
        info = timeline.get_frame_info(1000)
        assert info.frame == 899


class TestFrameInfo:
    """Tests for FrameInfo named tuple."""
    
    def test_frame_info_creation(self):
        """Test FrameInfo creation."""
        info = FrameInfo(
            frame=100,
            time=3.333,
            phase=0.698,
            loop_x=0.766,
            loop_y=0.643
        )
        
        assert info.frame == 100
        assert info.time == 3.333
        assert info.phase == 0.698
        assert info.loop_x == 0.766
        assert info.loop_y == 0.643
    
    def test_frame_info_immutable(self):
        """Test that FrameInfo is immutable."""
        info = FrameInfo(0, 0.0, 0.0, 1.0, 0.0)
        
        with pytest.raises(AttributeError):
            info.frame = 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
