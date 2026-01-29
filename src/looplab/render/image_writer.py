"""Image writing utilities for saving rendered frames."""

from pathlib import Path
from typing import Union
import numpy as np

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False


def save_frame_png(
    pixels: np.ndarray,
    path: Union[str, Path],
    flip_vertical: bool = False
) -> bool:
    """Save a frame as PNG.
    
    Args:
        pixels: RGBA pixel data as numpy array (height, width, 4)
        path: Output file path
        flip_vertical: Whether to flip the image vertically
        
    Returns:
        True if successful
    """
    if not PIL_AVAILABLE:
        raise ImportError("Pillow is required for image saving")
    
    if flip_vertical:
        pixels = np.flipud(pixels)
    
    # Ensure uint8
    if pixels.dtype != np.uint8:
        pixels = np.clip(pixels, 0, 255).astype(np.uint8)
    
    # Create image and save
    image = Image.fromarray(pixels, mode='RGBA')
    image.save(str(path), format='PNG')
    
    return True


def load_frame_png(path: Union[str, Path]) -> np.ndarray:
    """Load a PNG frame as numpy array.
    
    Args:
        path: Input file path
        
    Returns:
        RGBA pixel data as numpy array (height, width, 4)
    """
    if not PIL_AVAILABLE:
        raise ImportError("Pillow is required for image loading")
    
    image = Image.open(str(path))
    image = image.convert('RGBA')
    return np.array(image)


def create_thumbnail(
    pixels: np.ndarray,
    max_size: int = 256
) -> np.ndarray:
    """Create a thumbnail from frame data.
    
    Args:
        pixels: RGBA pixel data as numpy array
        max_size: Maximum dimension of thumbnail
        
    Returns:
        Thumbnail as numpy array
    """
    if not PIL_AVAILABLE:
        raise ImportError("Pillow is required for thumbnails")
    
    image = Image.fromarray(pixels, mode='RGBA')
    image.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
    return np.array(image)
