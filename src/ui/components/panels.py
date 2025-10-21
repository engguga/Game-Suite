import pygame
from typing import Tuple

class Panel:
    """Professional panel component for UI organization"""
    
    def __init__(self, x: int, y: int, width: int, height: int, 
                 color: Tuple[int, int, int] = (40, 40, 60),
                 border_color: Tuple[int, int, int] = (80, 80, 100)):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.border_color = border_color
        
    def render(self, surface: pygame.Surface):
        """Render panel with border"""
        # Draw panel background
        pygame.draw.rect(surface, self.color, self.rect, border_radius=6)
        
        # Draw border
        pygame.draw.rect(surface, self.border_color, self.rect, 2, border_radius=6)
        
    def contains_point(self, point: Tuple[int, int]) -> bool:
        """Check if point is inside panel"""
        return self.rect.collidepoint(point)
