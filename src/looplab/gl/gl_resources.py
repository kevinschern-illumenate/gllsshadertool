"""OpenGL resource management (VAO, VBO, FBO).

This module handles low-level OpenGL resources for rendering.
"""

from dataclasses import dataclass
from typing import Optional
import ctypes

try:
    from OpenGL.GL import (
        glGenVertexArrays, glBindVertexArray, glDeleteVertexArrays,
        glGenBuffers, glBindBuffer, glBufferData, glDeleteBuffers,
        glVertexAttribPointer, glEnableVertexAttribArray,
        glGenFramebuffers, glBindFramebuffer, glDeleteFramebuffers,
        glGenTextures, glBindTexture, glDeleteTextures,
        glTexImage2D, glTexParameteri, glFramebufferTexture2D,
        glGenRenderbuffers, glBindRenderbuffer, glDeleteRenderbuffers,
        glRenderbufferStorage, glFramebufferRenderbuffer,
        glCheckFramebufferStatus, glViewport, glReadPixels,
        glDrawArrays, glClear, glClearColor,
        GL_ARRAY_BUFFER, GL_STATIC_DRAW, GL_FLOAT, GL_FALSE,
        GL_FRAMEBUFFER, GL_TEXTURE_2D, GL_RGBA, GL_RGBA8,
        GL_COLOR_ATTACHMENT0, GL_RENDERBUFFER, GL_DEPTH24_STENCIL8,
        GL_DEPTH_STENCIL_ATTACHMENT, GL_FRAMEBUFFER_COMPLETE,
        GL_UNSIGNED_BYTE, GL_TRIANGLES, GL_COLOR_BUFFER_BIT,
        GL_TEXTURE_MIN_FILTER, GL_TEXTURE_MAG_FILTER, GL_LINEAR,
        GL_TEXTURE_WRAP_S, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE,
    )
    import numpy as np
    OPENGL_AVAILABLE = True
except ImportError:
    OPENGL_AVAILABLE = False


# Fullscreen quad vertices (two triangles)
QUAD_VERTICES = [
    -1.0, -1.0,
     1.0, -1.0,
     1.0,  1.0,
    -1.0, -1.0,
     1.0,  1.0,
    -1.0,  1.0,
]


@dataclass
class QuadMesh:
    """Fullscreen quad mesh for shader rendering."""
    
    vao: int = 0
    vbo: int = 0
    is_valid: bool = False
    
    def create(self):
        """Create VAO and VBO for the quad."""
        if not OPENGL_AVAILABLE:
            return
        
        import numpy as np
        
        # Create VAO
        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)
        
        # Create VBO
        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        
        # Upload vertex data
        vertices = np.array(QUAD_VERTICES, dtype=np.float32)
        glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)
        
        # Set up vertex attribute (position)
        glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 0, None)
        glEnableVertexAttribArray(0)
        
        # Unbind
        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindVertexArray(0)
        
        self.is_valid = True
    
    def draw(self):
        """Draw the quad."""
        if not OPENGL_AVAILABLE or not self.is_valid:
            return
        
        glBindVertexArray(self.vao)
        glDrawArrays(GL_TRIANGLES, 0, 6)
        glBindVertexArray(0)
    
    def delete(self):
        """Delete VAO and VBO."""
        if not OPENGL_AVAILABLE:
            return
        
        if self.vbo:
            glDeleteBuffers(1, [self.vbo])
        if self.vao:
            glDeleteVertexArrays(1, [self.vao])
        self.is_valid = False


@dataclass
class RenderTarget:
    """Framebuffer Object (FBO) for offscreen rendering."""
    
    fbo: int = 0
    texture: int = 0
    rbo: int = 0  # Renderbuffer for depth/stencil
    width: int = 0
    height: int = 0
    is_valid: bool = False
    
    def create(self, width: int, height: int):
        """Create FBO with color texture and depth buffer.
        
        Args:
            width: Width in pixels
            height: Height in pixels
        """
        if not OPENGL_AVAILABLE:
            return
        
        self.width = width
        self.height = height
        
        # Create framebuffer
        self.fbo = glGenFramebuffers(1)
        glBindFramebuffer(GL_FRAMEBUFFER, self.fbo)
        
        # Create color texture
        self.texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.texture)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA8, width, height, 0,
                     GL_RGBA, GL_UNSIGNED_BYTE, None)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0,
                               GL_TEXTURE_2D, self.texture, 0)
        
        # Create depth/stencil renderbuffer
        self.rbo = glGenRenderbuffers(1)
        glBindRenderbuffer(GL_RENDERBUFFER, self.rbo)
        glRenderbufferStorage(GL_RENDERBUFFER, GL_DEPTH24_STENCIL8, width, height)
        glFramebufferRenderbuffer(GL_FRAMEBUFFER, GL_DEPTH_STENCIL_ATTACHMENT,
                                  GL_RENDERBUFFER, self.rbo)
        
        # Check completeness
        status = glCheckFramebufferStatus(GL_FRAMEBUFFER)
        self.is_valid = (status == GL_FRAMEBUFFER_COMPLETE)
        
        # Unbind
        glBindFramebuffer(GL_FRAMEBUFFER, 0)
        glBindTexture(GL_TEXTURE_2D, 0)
        glBindRenderbuffer(GL_RENDERBUFFER, 0)
    
    def bind(self):
        """Bind this FBO as render target."""
        if not OPENGL_AVAILABLE or not self.is_valid:
            return
        
        glBindFramebuffer(GL_FRAMEBUFFER, self.fbo)
        glViewport(0, 0, self.width, self.height)
    
    def unbind(self):
        """Unbind this FBO (render to default framebuffer)."""
        if not OPENGL_AVAILABLE:
            return
        
        glBindFramebuffer(GL_FRAMEBUFFER, 0)
    
    def read_pixels(self) -> Optional[bytes]:
        """Read pixels from the FBO.
        
        Returns:
            Raw RGBA pixel data as bytes, or None on failure
        """
        if not OPENGL_AVAILABLE or not self.is_valid:
            return None
        
        import numpy as np
        
        self.bind()
        
        # Read pixels
        pixels = glReadPixels(0, 0, self.width, self.height,
                              GL_RGBA, GL_UNSIGNED_BYTE)
        
        self.unbind()
        
        return pixels
    
    def resize(self, width: int, height: int):
        """Resize the FBO.
        
        Args:
            width: New width
            height: New height
        """
        if width == self.width and height == self.height:
            return
        
        self.delete()
        self.create(width, height)
    
    def delete(self):
        """Delete FBO and associated resources."""
        if not OPENGL_AVAILABLE:
            return
        
        if self.rbo:
            glDeleteRenderbuffers(1, [self.rbo])
        if self.texture:
            glDeleteTextures(1, [self.texture])
        if self.fbo:
            glDeleteFramebuffers(1, [self.fbo])
        
        self.fbo = 0
        self.texture = 0
        self.rbo = 0
        self.is_valid = False


def clear_viewport(r: float = 0.0, g: float = 0.0, b: float = 0.0, a: float = 1.0):
    """Clear the current viewport.
    
    Args:
        r, g, b, a: Clear color components (0-1)
    """
    if not OPENGL_AVAILABLE:
        return
    
    glClearColor(r, g, b, a)
    glClear(GL_COLOR_BUFFER_BIT)
