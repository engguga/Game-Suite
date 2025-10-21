import pygame
from typing import Tuple, Optional

class TextElement:
    """Professional text rendering component"""
    
    def __init__(self, x: int, y: int, text: str, 
                 font_size: int = 24, 
                 color: Tuple[int, int, int] = (255, 255, 255),
                 centered: bool = False):
        self.x = x
        self.y = y
        self.text = text
        self.font_size = font_size
        self.color = color
        self.centered = centered
        
        self.font = pygame.font.Font(None, font_size)
        self._update_surface()
        
    def _update_surface(self):
        """Update text surface"""
        self.surface = self.font.render(self.text, True, self.color)
        self.rect = self.surface.get_rect()
        
        if self.centered:
            self.rect.center = (self.x, self.y)
        else:
            self.rect.topleft = (self.x, self.y)
            
    def set_text(self, text: str):
        """Update text content"""
        self.text = text
        self._update_surface()
        
    def set_color(self, color: Tuple[int, int, int]):
        """Update text color"""
        self.color = color
        self._update_surface()
        
    def render(self, surface: pygame.Surface):
        """Render text to surface"""
        surface.blit(self.surface, self.rect)
