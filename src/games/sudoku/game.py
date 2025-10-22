import pygame
import random
import time
from typing import List, Tuple, Optional, Dict
from ..base_game import BaseGame

class SudokuGame(BaseGame):
    def __init__(self, engine):
        super().__init__(engine, "sudoku")
        self.levels = {
            "Facil": 35,
            "Medio": 45,
            "Dificil": 55
        }
        self.current_level = "Facil"
        self.cells_to_remove = self.levels[self.current_level]
        self.grid_size = 9
        self.cell_size = 50
        self.board = []
        self.solution = []
        self.user_board = []
        self.selected_cell = None
        self.mistakes = 0
        self.max_mistakes = 3
        self.game_complete = False
        self.start_time = 0
        self.elapsed_time = 0
        self.hints_used = 0
        self.max_hints = 3
        
        self.colors = {
            'background': (25, 25, 40),
            'grid_bg': (50, 50, 70),
            'cell_bg': (60, 60, 80),
            'cell_selected': (80, 80, 110),
            'cell_hover': (70, 70, 95),
            'text_light': (220, 220, 220),
            'text_dark': (150, 150, 170),
            'text_user': (100, 200, 255),
            'text_error': (255, 100, 100),
            'text_hint': (100, 255, 100),
            'panel_bg': (60, 60, 80, 200),
            'panel_border': (90, 90, 120),
            'complete': (100, 255, 100)
        }
        
        self.initialize()

    def _generate_solution(self):
        base = 3
        side = base * base
        def pattern(r, c): return (base * (r % base) + r // base + c) % side
        def shuffle(s): return random.sample(s, len(s))
        
        rBase = range(base)
        rows = [g * base + r for g in shuffle(rBase) for r in shuffle(rBase)]
        cols = [g * base + c for g in shuffle(rBase) for c in shuffle(rBase)]
        nums = shuffle(range(1, base * base + 1))
        
        board = [[nums[pattern(r, c)] for c in cols] for r in rows]
        return board

    def _remove_numbers(self, board, cells_to_remove):
        puzzle = [row[:] for row in board]
        cells = [(i, j) for i in range(9) for j in range(9)]
        random.shuffle(cells)
        
        for i, j in cells[:cells_to_remove]:
            puzzle[i][j] = 0
        return puzzle

    def _is_valid(self, board, row, col, num):
        for x in range(9):
            if board[row][x] == num or board[x][col] == num:
                return False
        
        start_row, start_col = 3 * (row // 3), 3 * (col // 3)
        for i in range(3):
            for j in range(3):
                if board[i + start_row][j + start_col] == num:
                    return False
        return True

    def initialize(self):
        self.solution = self._generate_solution()
        self.board = self._remove_numbers(self.solution, self.cells_to_remove)
        self.user_board = [row[:] for row in self.board]
        self.selected_cell = None
        self.mistakes = 0
        self.game_complete = False
        self.start_time = time.time()
        self.elapsed_time = 0
        self.hints_used = 0

    def update(self, delta_time):
        if not self.game_complete:
            self.elapsed_time = time.time() - self.start_time
            
        if not self.game_complete and self.user_board == self.solution:
            self.game_complete = True

    def render(self, surface):
        surface.fill(self.colors['background'])
        self._draw_grid(surface)
        self._draw_numbers(surface)
        self._draw_ui(surface)
        self._draw_developer_credit(surface)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self._handle_click(pygame.mouse.get_pos())
                
        elif event.type == pygame.KEYDOWN:
            if not self.game_complete and self.selected_cell:
                row, col = self.selected_cell
                if self.board[row][col] == 0:
                    if event.key in [pygame.K_1, pygame.K_KP1]:
                        self._place_number(1)
                    elif event.key in [pygame.K_2, pygame.K_KP2]:
                        self._place_number(2)
                    elif event.key in [pygame.K_3, pygame.K_KP3]:
                        self._place_number(3)
                    elif event.key in [pygame.K_4, pygame.K_KP4]:
                        self._place_number(4)
                    elif event.key in [pygame.K_5, pygame.K_KP5]:
                        self._place_number(5)
                    elif event.key in [pygame.K_6, pygame.K_KP6]:
                        self._place_number(6)
                    elif event.key in [pygame.K_7, pygame.K_KP7]:
                        self._place_number(7)
                    elif event.key in [pygame.K_8, pygame.K_KP8]:
                        self._place_number(8)
                    elif event.key in [pygame.K_9, pygame.K_KP9]:
                        self._place_number(9)
                    elif event.key == pygame.K_BACKSPACE or event.key == pygame.K_DELETE:
                        self._place_number(0)
                    elif event.key == pygame.K_h and self.hints_used < self.max_hints:
                        self._use_hint()
            
            if event.key == pygame.K_r:
                self.initialize()
            elif event.key == pygame.K_n:
                self._switch_level()
            elif event.key == pygame.K_ESCAPE:
                self.engine._return_to_menu()

    def _switch_level(self):
        levels_list = list(self.levels.keys())
        current_index = levels_list.index(self.current_level)
        self.current_level = levels_list[(current_index + 1) % len(levels_list)]
        self.cells_to_remove = self.levels[self.current_level]
        self.initialize()

    def _handle_click(self, mouse_pos):
        board_x, board_y = self._get_board_position()
        mouse_x, mouse_y = mouse_pos
        
        if (board_x <= mouse_x < board_x + self.grid_size * self.cell_size and
            board_y <= mouse_y < board_y + self.grid_size * self.cell_size):
            
            col = (mouse_x - board_x) // self.cell_size
            row = (mouse_y - board_y) // self.cell_size
            
            if 0 <= row < self.grid_size and 0 <= col < self.grid_size:
                self.selected_cell = (row, col)

    def _place_number(self, number):
        if not self.selected_cell:
            return
            
        row, col = self.selected_cell
        if self.board[row][col] != 0:
            return
            
        if number == 0:
            self.user_board[row][col] = 0
            return
            
        if self.solution[row][col] == number:
            self.user_board[row][col] = number
        else:
            self.mistakes += 1
            if self.mistakes >= self.max_mistakes:
                self.game_complete = True

    def _use_hint(self):
        if not self.selected_cell or self.hints_used >= self.max_hints:
            return
            
        row, col = self.selected_cell
        if self.board[row][col] == 0 and self.user_board[row][col] == 0:
            self.user_board[row][col] = self.solution[row][col]
            self.hints_used += 1

    def _draw_grid(self, surface):
        board_x, board_y = self._get_board_position()
        
        board_rect = pygame.Rect(
            board_x - 10, board_y - 10,
            self.grid_size * self.cell_size + 20,
            self.grid_size * self.cell_size + 20
        )
        pygame.draw.rect(surface, self.colors['grid_bg'], board_rect, border_radius=8)
        
        for i in range(self.grid_size + 1):
            line_width = 3 if i % 3 == 0 else 1
            pygame.draw.line(
                surface, self.colors['text_light'],
                (board_x, board_y + i * self.cell_size),
                (board_x + self.grid_size * self.cell_size, board_y + i * self.cell_size),
                line_width
            )
            pygame.draw.line(
                surface, self.colors['text_light'],
                (board_x + i * self.cell_size, board_y),
                (board_x + i * self.cell_size, board_y + self.grid_size * self.cell_size),
                line_width
            )
        
        if self.selected_cell:
            row, col = self.selected_cell
            selected_rect = pygame.Rect(
                board_x + col * self.cell_size,
                board_y + row * self.cell_size,
                self.cell_size, self.cell_size
            )
            pygame.draw.rect(surface, self.colors['cell_selected'], selected_rect)

    def _draw_numbers(self, surface):
        board_x, board_y = self._get_board_position()
        
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                cell_value = self.user_board[row][col]
                if cell_value == 0:
                    continue
                    
                cell_rect = pygame.Rect(
                    board_x + col * self.cell_size,
                    board_y + row * self.cell_size,
                    self.cell_size, self.cell_size
                )
                
                if self.board[row][col] != 0:
                    color = self.colors['text_light']
                else:
                    if cell_value == self.solution[row][col]:
                        color = self.colors['text_user']
                    else:
                        color = self.colors['text_error']
                
                font = pygame.font.Font(None, 36)
                text = font.render(str(cell_value), True, color)
                text_rect = text.get_rect(center=cell_rect.center)
                surface.blit(text, text_rect)

    def _draw_ui(self, surface):
        board_x, board_y = self._get_board_position()
        
        stats_panel = pygame.Rect(20, 20, 300, 160)
        self._draw_glass_panel(surface, stats_panel)
        
        title_font = pygame.font.Font(None, 24)
        stats_font = pygame.font.Font(None, 28)
        small_font = pygame.font.Font(None, 20)
        
        level_text = title_font.render(f"Nivel: {self.current_level}", True, self.colors['text_light'])
        time_text = stats_font.render(f"Tempo: {int(self.elapsed_time)}s", True, self.colors['text_light'])
        mistakes_text = stats_font.render(f"Erros: {self.mistakes}/{self.max_mistakes}", True, self.colors['text_light'])
        hints_text = stats_font.render(f"Dicas: {self.hints_used}/{self.max_hints}", True, self.colors['text_light'])
        
        surface.blit(level_text, (35, 30))
        surface.blit(time_text, (35, 60))
        surface.blit(mistakes_text, (35, 95))
        surface.blit(hints_text, (35, 125))
        
        controls_text = small_font.render("N: Proximo Nivel | R: Reiniciar | H: Dica | ESC: Menu", True, (150, 200, 150))
        surface.blit(controls_text, (35, 160))
        
        if self.game_complete:
            overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            surface.blit(overlay, (0, 0))
            
            complete_font = pygame.font.Font(None, 48)
            if self.mistakes >= self.max_mistakes:
                complete_text = complete_font.render("Game Over!", True, self.colors['text_error'])
            else:
                complete_text = complete_font.render("Sudoku Concluido!", True, self.colors['complete'])
            
            surface.blit(complete_text, 
                        (surface.get_width() // 2 - complete_text.get_width() // 2, 
                         surface.get_height() // 2 - 60))
            
            stats_font = pygame.font.Font(None, 32)
            if self.mistakes < self.max_mistakes:
                stats_text = stats_font.render(f"Resolvido em {int(self.elapsed_time)} segundos", True, (200, 200, 200))
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
                "Clique em uma celula e digite um numero (1-9)",
                "Backspace/Del: Limpar celula",
                "Preencha o tabuleiro sem repetir numeros nas linhas, colunas ou quadrantes 3x3"
            ]
            
            for i, instruction in enumerate(instructions):
                text = instruction_font.render(instruction, True, (180, 180, 180))
                surface.blit(text, (25, surface.get_height() - 90 + i * 22))

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
