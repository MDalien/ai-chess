import pygame
from const import WIDTH, HEIGHT

BG = (40, 40, 40)
BUTTON = (70, 70, 70)
HOVER = (95, 95, 95)
SELECTED = (119, 154, 88)
TEXT = (240, 240, 240)
DIM = (160, 160, 160)


class Button:

    def __init__(self, text, rect, value):
        self.text = text
        self.rect = pygame.Rect(rect)
        self.value = value

    def draw(self, surface, font, selected=False, hovered=False):
        color = SELECTED if selected else HOVER if hovered else BUTTON
        pygame.draw.rect(surface, color, self.rect, border_radius=10)
        label = font.render(self.text, True, TEXT)
        surface.blit(label, label.get_rect(center=self.rect.center))

    def clicked(self, pos):
        return self.rect.collidepoint(pos)


class Menu:

    def __init__(self):
        self.title_font = pygame.font.SysFont('arial', 60, bold=True)
        self.font = pygame.font.SysFont('arial', 26)
        self.small_font = pygame.font.SysFont('arial', 20)

        # current selections
        self.mode = 'pvai'
        self.ai_color = 'black'
        self.depth = 2

        # mode buttons: value = (mode, ai_color)
        self.mode_buttons = [
            Button('Player vs Player', (90, 220, 300, 60), ('pvp', None)),
            Button('Play as White', (410, 220, 300, 60), ('pvai', 'black')),
            Button('Play as Black', (90, 295, 300, 60), ('pvai', 'white')),
            Button('AI vs AI', (410, 295, 300, 60), ('aivai', None)),
        ]

        # difficulty buttons: value = search depth
        labels = ['Easy', 'Medium', 'Hard', 'Expert']
        self.depth_buttons = [
            Button(labels[i], (50 + i * 180, 440, 160, 55), i + 1)
            for i in range(4)
        ]

        self.start_button = Button('Start Game', (250, 570, 300, 70), None)

    def draw(self, surface, mouse_pos):
        surface.fill(BG)

        title = self.title_font.render('AI Chess', True, TEXT)
        surface.blit(title, title.get_rect(center=(WIDTH // 2, 110)))

        # mode section
        label = self.font.render('Mode', True, DIM)
        surface.blit(label, label.get_rect(center=(WIDTH // 2, 185)))
        for b in self.mode_buttons:
            selected = b.value == (self.mode, self.ai_color if self.mode == 'pvai' else None)
            b.draw(surface, self.font, selected, b.clicked(mouse_pos))

        # difficulty section (hidden in pvp, since there's no AI)
        if self.mode != 'pvp':
            label = self.font.render('Difficulty', True, DIM)
            surface.blit(label, label.get_rect(center=(WIDTH // 2, 405)))
            for b in self.depth_buttons:
                b.draw(surface, self.font, b.value == self.depth, b.clicked(mouse_pos))

        self.start_button.draw(surface, self.font, False, self.start_button.clicked(mouse_pos))

        hint = self.small_font.render('In game:  R = restart   T = theme   Esc = menu', True, DIM)
        surface.blit(hint, hint.get_rect(center=(WIDTH // 2, HEIGHT - 60)))

    def handle_click(self, pos):
        '''Updates selections. Returns True if Start was clicked.'''
        for b in self.mode_buttons:
            if b.clicked(pos):
                self.mode, color = b.value
                if color:
                    self.ai_color = color

        if self.mode != 'pvp':
            for b in self.depth_buttons:
                if b.clicked(pos):
                    self.depth = b.value

        return self.start_button.clicked(pos)
