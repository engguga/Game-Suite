import pygame
from typing import Optional, Callable

class Button:
    """Professional button component with hover and click effects"""
    
    def __init__(self, x: int, y: int, width: int, height: int, text: str, 
                 callback: Optional[Callable] = None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.callback = callback
        self.hovered = False
        self.clicked = False
        self.hover_progress = 0.0
        
        # Professional color scheme
        self.normal_color = (60, 60, 100)
        self.hover_color = (80, 80, 140)
        self.click_color = (100, 100, 180)
        self.text_color = (255, 255, 255)
        self.border_color = (90, 90, 130)
        self.shadow_color = (20, 20, 40)
        
        # Font
        self.font = pygame.font.Font(None, 26)  # Slightly smaller for better fit
        
    def update(self, delta_time: float):
        """Update button animations"""
        target_progress = 1.0 if self.hovered else 0.0
        self.hover_progress += (target_progress - self.hover_progress) * 10 * delta_time
        
        # Reset clicked state after animation
        if self.clicked:
            self.clicked = False
            
    def render(self, surface: pygame.Surface):
        """Render button with professional appearance"""
        # Draw shadow for depth
        shadow_rect = self.rect.move(4, 4)
        pygame.draw.rect(surface, self.shadow_color, shadow_rect, border_radius=8)
        
        # Draw button background with current state color
        current_color = self._get_current_color()
        pygame.draw.rect(surface, current_color, self.rect, border_radius=8)
        
        # Draw subtle border
        pygame.draw.rect(surface, self.border_color, self.rect, 2, border_radius=8)
        
        # Draw text with professional typography
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)
        
        # Draw hover glow effect
        if self.hover_progress > 0:
            glow_surface = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
            glow_color = (255, 255, 255, int(30 * self.hover_progress))  # Subtle glow
            pygame.draw.rect(glow_surface, glow_color, glow_surface.get_rect(), border_radius=8)
            surface.blit(glow_surface, self.rect)
            
        # Draw click effect (brief highlight)
        if self.clicked:
            highlight_surface = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
            highlight_color = (255, 255, 255, int(80 * (1.0 - self.hover_progress)))
            pygame.draw.rect(highlight_surface, highlight_color, highlight_surface.get_rect(), border_radius=8)
            surface.blit(highlight_surface, self.rect)
            
    def _get_current_color(self):
        """Get color based on button state with smooth interpolation"""
        if self.clicked:
            return self.click_color
            
        # Smooth interpolation between normal and hover colors
        r = int(self.normal_color[0] + (self.hover_color[0] - self.normal_color[0]) * self.hover_progress)
        g = int(self.normal_color[1] + (self.hover_color[1] - self.normal_color[1]) * self.hover_progress)
        b = int(self.normal_color[2] + (self.hover_color[2] - self.normal_color[2]) * self.hover_progress)
        
        return (r, g, b)
        
    def is_clicked(self, mouse_pos) -> bool:
        """Check if button is being clicked"""
        mouse_rect = pygame.Rect(mouse_pos[0], mouse_pos[1], 1, 1)
        return self.rect.colliderect(mouse_rect)
        
    def click(self):
        """Handle button click"""
        self.clicked = True
        if self.callback:
            self.callback()
            
    def set_hovered(self, hovered: bool):
        """Set hover state"""
        self.hovered = hovered
