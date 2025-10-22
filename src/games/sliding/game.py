import pygame
import random
import time
import os
from typing import List, Tuple, Optional, Dict
from ..base_game import BaseGame

class SlidingPuzzleGame(BaseGame):
    def __init__(self, engine):
        super().__init__(engine, "sliding")
        self.levels = {
            "Facil": 3,
            "Medio": 4, 
            "Dificil": 5
        }
        self.current_level = "Facil"
        self.grid_size = self.levels[self.current_level]
        self.cell_size = 500 // self.grid_size
        self.grid = []
        self.solved_grid = []
        self.empty_pos = (0, 0)
        self.moves = 0
        self.game_started = False
        self.game_complete = False
        self.start_time = 0
        self.elapsed_time = 0
        self.animations = []
        self.show_numbers = True
        
        self.colors = {
            'background': (25, 25, 40),
            'grid_bg': (50, 50, 70),
            'tile_bg': (70, 70, 90),
            'tile_border': (90, 90, 120),
            'text_light': (220, 220, 220),
            'panel_bg': (60, 60, 80, 200),
            'panel_border': (90, 90, 120),
            'complete': (100, 255, 100)
        }
        
        self._create_geometric_image()
        self.initialize()

    def _create_geometric_image(self):
        size = 800
        self.current_image = pygame.Surface((size, size))
        colors = [(70, 130, 180), (100, 150, 200), (130, 170, 220), (160, 190, 240)]
        
        for i in range(4):
            radius = size // 2 - i * 80
            color = colors[i]
            pygame.draw.circle(self.current_image, color, (size // 2, size // 2), radius)
            
        self.image_loaded = True

    def initialize(self):
        self.grid_size = self.levels[self.current_level]
        self.cell_size = 500 // self.grid_size
        
        self.solved_grid = []
        value = 1
        for i in range(self.grid_size):
            row = []
            for j in range(self.grid_size):
                if i == self.grid_size - 1 and j == self.grid_size - 1:
                    row.append(0)
                else:
                    row.append(value)
                    value += 1
            self.solved_grid.append(row)
        
        self.grid = [row[:] for row in self.solved_grid]
        self.empty_pos = (self.grid_size - 1, self.grid_size - 1)
        self._shuffle_puzzle()
        
        self.moves = 0
        self.game_started = False
        self.game_complete = False
        self.start_time = time.time()
        self.elapsed_time = 0
        self.animations = []

    def _shuffle_puzzle(self):
        for _ in range(100 * self.grid_size * self.grid_size):
            possible_moves = self._get_possible_moves()
            if possible_moves:
                move = random.choice(possible_moves)
                self._slide_tile(move)
                
    def _get_possible_moves(self):
        empty_i, empty_j = self.empty_pos
        moves = []
        
        for di, dj in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            new_i, new_j = empty_i + di, empty_j + dj
            if 0 <= new_i < self.grid_size and 0 <= new_j < self.grid_size:
                moves.append((new_i, new_j))
                
        return moves
        
    def _slide_tile(self, tile_pos):
        tile_i, tile_j = tile_pos
        empty_i, empty_j = self.empty_pos
        
        self.grid[empty_i][empty_j] = self.grid[tile_i][tile_j]
        self.grid[tile_i][tile_j] = 0
        self.empty_pos = (tile_i, tile_j)
        
    def update(self, delta_time):
        if self.game_started and not self.game_complete:
            self.elapsed_time = time.time() - self.start_time
            
        for animation in self.animations[:]:
            animation['progress'] += delta_time * 6
            if animation['progress'] >= 1.0:
                self.animations.remove(animation)
                
        if not self.game_complete and self.grid == self.solved_grid:
            self.game_complete = True
            
    def render(self, surface):
        surface.fill(self.colors['background'])
        self._draw_puzzle(surface)
        self._draw_ui(surface)
        self._draw_developer_credit(surface)
        
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if not self.game_complete:
                self._handle_click(pygame.mouse.get_pos())
                
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                self.initialize()
            elif event.key == pygame.K_n:
                self._switch_level()
            elif event.key == pygame.K_h:
                self.show_numbers = not self.show_numbers
            elif event.key == pygame.K_ESCAPE:
                self.engine._return_to_menu()
                
    def _switch_level(self):
        levels_list = list(self.levels.keys())
        current_index = levels_list.index(self.current_level)
        self.current_level = levels_list[(current_index + 1) % len(levels_list)]
        self.initialize()
                
    def _handle_click(self, mouse_pos):
        board_x, board_y = self._get_board_position()
        mouse_x, mouse_y = mouse_pos
        grid_x = (mouse_x - board_x) // self.cell_size
        grid_y = (mouse_y - board_y) // self.cell_size
        
        if 0 <= grid_x < self.grid_size and 0 <= grid_y < self.grid_size:
            clicked_pos = (grid_y, grid_x)
            
            if clicked_pos in self._get_possible_moves():
                if not self.game_started:
                    self.game_started = True
                    self.start_time = time.time()
                    
                empty_i, empty_j = self.empty_pos
                self.animations.append({
                    'type': 'slide',
                    'from_pos': clicked_pos,
                    'to_pos': self.empty_pos,
                    'progress': 0.0
                })
                
                self._slide_tile(clicked_pos)
                self.moves += 1
                
    def _draw_puzzle(self, surface):
        board_x, board_y = self._get_board_position()
        
        board_rect = pygame.Rect(
            board_x - 10, board_y - 10,
            self.grid_size * self.cell_size + 20,
            self.grid_size * self.cell_size + 20
        )
        pygame.draw.rect(surface, self.colors['grid_bg'], board_rect, border_radius=8)
        
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                value = self.grid[i][j]
                if value != 0:
                    self._draw_tile(surface, board_x, board_y, i, j, value)
                    
        for animation in self.animations:
            if animation['type'] == 'slide':
                self._draw_sliding_tile(surface, board_x, board_y, animation)
        
    def _draw_tile(self, surface, board_x, board_y, i, j, value):
        tile_rect = pygame.Rect(
            board_x + j * self.cell_size + 2,
            board_y + i * self.cell_size + 2,
            self.cell_size - 4,
            self.cell_size - 4
        )
        
        pygame.draw.rect(surface, self.colors['tile_bg'], tile_rect, border_radius=6)
        
        if self.image_loaded and self.current_image:
            img_cell_size = self.current_image.get_width() // self.grid_size
            src_rect = pygame.Rect(
                j * img_cell_size,
                i * img_cell_size, 
                img_cell_size,
                img_cell_size
            )
            
            segment = self.current_image.subsurface(src_rect)
            segment = pygame.transform.smoothscale(segment, (self.cell_size - 4, self.cell_size - 4))
            surface.blit(segment, tile_rect)
        
        if self.show_numbers:
            font_size = max(20, self.cell_size // 4)
            font = pygame.font.Font(None, font_size)
            text = font.render(str(value), True, self.colors['text_light'])
            text_rect = text.get_rect(center=tile_rect.center)
            surface.blit(text, text_rect)
            
        pygame.draw.rect(surface, self.colors['tile_border'], tile_rect, 2, border_radius=6)
        
    def _draw_sliding_tile(self, surface, board_x, board_y, animation):
        from_i, from_j = animation['from_pos']
        to_i, to_j = animation['to_pos']
        progress = animation['progress']
        
        current_x = from_j + (to_j - from_j) * progress
        current_y = from_i + (to_i - from_i) * progress
        
        tile_rect = pygame.Rect(
            board_x + current_x * self.cell_size + 2,
            board_y + current_y * self.cell_size + 2,
            self.cell_size - 4,
            self.cell_size - 4
        )
        
        pygame.draw.rect(surface, (80, 80, 110), tile_rect, border_radius=6)
        
        if self.image_loaded and self.current_image:
            img_cell_size = self.current_image.get_width() // self.grid_size
            src_rect = pygame.Rect(
                from_j * img_cell_size,
                from_i * img_cell_size,
                img_cell_size,
                img_cell_size
            )
            segment = self.current_image.subsurface(src_rect)
            segment = pygame.transform.smoothscale(segment, (self.cell_size - 4, self.cell_size - 4))
            surface.blit(segment, tile_rect)
        
        if self.show_numbers:
            value = self.grid[to_i][to_j]
            font_size = max(20, self.cell_size // 4)
            font = pygame.font.Font(None, font_size)
            text = font.render(str(value), True, self.colors['text_light'])
            text_rect = text.get_rect(center=tile_rect.center)
            surface.blit(text, text_rect)
            
        pygame.draw.rect(surface, (120, 120, 160), tile_rect, 2, border_radius=6)
        
    def _draw_ui(self, surface):
        board_x, board_y = self._get_board_position()
        
        stats_panel = pygame.Rect(20, 20, 280, 140)
        self._draw_glass_panel(surface, stats_panel)
        
        title_font = pygame.font.Font(None, 24)
        stats_font = pygame.font.Font(None, 28)
        small_font = pygame.font.Font(None, 20)
        
        level_text = title_font.render(f"Nivel: {self.current_level}", True, self.colors['text_light'])
        size_text = title_font.render(f"Grid: {self.grid_size}x{self.grid_size}", True, self.colors['text_light'])
        moves_text = stats_font.render(f"Movimentos: {self.moves}", True, self.colors['text_light'])
        time_text = stats_font.render(f"Tempo: {int(self.elapsed_time)}s", True, self.colors['text_light'])
        
        surface.blit(level_text, (35, 30))
        surface.blit(size_text, (35, 55))
        surface.blit(moves_text, (35, 85))
        surface.blit(time_text, (35, 115))
        
        controls_text = small_font.render("N: Proximo Nivel | H: Mostrar/Ocultar Numeros | R: Reiniciar", True, (150, 200, 150))
        surface.blit(controls_text, (35, 150))
        
        if self.game_complete:
            overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            surface.blit(overlay, (0, 0))
            
            complete_font = pygame.font.Font(None, 48)
            complete_text = complete_font.render("Puzzle Resolvido!", True, self.colors['complete'])
            surface.blit(complete_text, 
                        (surface.get_width() // 2 - complete_text.get_width() // 2, 
                         surface.get_height() // 2 - 60))
            
            stats_font = pygame.font.Font(None, 32)
            stats_text = stats_font.render(f"Resolvido em {self.moves} movimentos, {int(self.elapsed_time)} segundos", True, (200, 200, 200))
            surface.blit(stats_text,
                        (surface.get_width() // 2 - stats_text.get_width() // 2,
                         surface.get_height() // 2))
            
            restart_font = pygame.font.Font(None, 24)
            restart_text = restart_font.render("Pressione R para jogar novamente ou ESC para menu", True, (150, 150, 150))
            surface.blit(restart_text,
                        (surface.get_width() // 2 - restart_text.get_width() // 2,
                         surface.get_height() // 2 + 50))
        else:
            instruction_font = pygame.font.Font(None, 20)
            instructions = [
                "Clique nas pecas para move-las para o espaco vazio",
                "Organize os numeros em ordem crescente para resolver",
                "ESC: Retornar ao menu"
            ]
            
            for i, instruction in enumerate(instructions):
                text = instruction_font.render(instruction, True, (180, 180, 180))
                surface.blit(text, (25, surface.get_height() - 80 + i * 22))
                
    def _draw_glass_panel(self, surface, rect):
        panel_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        panel_surface.fill(self.colors['panel_bg'])
        surface.blit(panel_surface, rect)
        pygame.draw.rect(surface, self.colors['panel_border'], rect, 2, border_radius=6)
                
    def _draw_developer_credit(self, surface):
        credit_font = pygame.font.Font(None, 16)
        credit_text = "Developed by Gustavo Viana"
        text_surface = credit_font.render(credit_text, True, (200, 200, 200))
        text_surface.set_alpha(150)
        text_rect = text_surface.get_rect()
        text_rect.bottomright = (surface.get_width() - 15, surface.get_height() - 15)
        surface.blit(text_surface, text_rect)
        
    def _get_board_position(self):
        board_width = self.grid_size * self.cell_size
        board_height = self.grid_size * self.cell_size
        board_x = (self.engine.screen.get_width() - board_width) // 2
        board_y = (self.engine.screen.get_height() - board_height) // 2
        return board_x, board_y
