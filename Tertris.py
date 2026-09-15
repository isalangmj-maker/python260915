import random
import sys

import pygame


CELL_SIZE = 30
BOARD_WIDTH = 10
BOARD_HEIGHT = 20
BOARD_X = 24
BOARD_Y = 24
SIDE_WIDTH = 210
WINDOW_WIDTH = BOARD_X * 2 + BOARD_WIDTH * CELL_SIZE + SIDE_WIDTH
WINDOW_HEIGHT = BOARD_Y * 2 + BOARD_HEIGHT * CELL_SIZE

DIFFICULTIES = {
    "1": {"name": "Easy", "drop_delay": 700, "multiplier": 1},
    "2": {"name": "Normal", "drop_delay": 450, "multiplier": 2},
    "3": {"name": "Hard", "drop_delay": 250, "multiplier": 3},
}

COLORS = {
    "I": (40, 195, 225),
    "J": (65, 105, 225),
    "L": (245, 145, 45),
    "O": (240, 205, 55),
    "S": (75, 195, 115),
    "T": (165, 105, 235),
    "Z": (235, 80, 95),
}

SHAPES = {
    "I": [["....", "IIII", "....", "...."], ["..I.", "..I.", "..I.", "..I."]],
    "J": [["J..", "JJJ", "..."], [".JJ", ".J.", ".J."], ["...", "JJJ", "..J"], [".J.", "J..", "J.."]],
    "L": [["..L", "LLL", "..."], ["L..", ".L.", ".L."], ["...", "LLL", "L.."], [".L.", ".L.", ".LL"]],
    "O": [["OO", "OO"]],
    "S": [[".SS", "SS.", "..."], ["S..", "SS.", ".S."]],
    "T": [[".T.", "TTT", "..."], [".T.", ".TT", ".T."], ["...", "TTT", ".T."], [".T.", "TT.", ".T."]],
    "Z": [["ZZ.", ".ZZ", "..."], [".Z.", "ZZ.", "Z.."]],
}


class TetrisGame:
    def __init__(self, difficulty_key):
        self.difficulty = DIFFICULTIES[difficulty_key]
        self.board = [[None] * BOARD_WIDTH for _ in range(BOARD_HEIGHT)]
        self.score = 0
        self.lines = 0
        self.running = True
        self.paused = False
        self.current_type = None
        self.current_rotation = 0
        self.current_x = 0
        self.current_y = 0
        self.next_type = random.choice(list(SHAPES))
        self.spawn_piece()

    def get_shape(self, rotation=None):
        rotation = self.current_rotation if rotation is None else rotation
        return SHAPES[self.current_type][rotation % len(SHAPES[self.current_type])]

    def spawn_piece(self):
        self.current_type = self.next_type
        self.current_rotation = 0
        self.next_type = random.choice(list(SHAPES))
        shape = self.get_shape()
        self.current_x = (BOARD_WIDTH - len(shape[0])) // 2
        self.current_y = 0
        if not self.is_valid(self.current_x, self.current_y, self.current_rotation):
            self.running = False

    def is_valid(self, x, y, rotation):
        shape = SHAPES[self.current_type][rotation % len(SHAPES[self.current_type])]
        for row_index, row in enumerate(shape):
            for column_index, cell in enumerate(row):
                if cell == ".":
                    continue
                board_x = x + column_index
                board_y = y + row_index
                if board_x < 0 or board_x >= BOARD_WIDTH or board_y >= BOARD_HEIGHT:
                    return False
                if board_y >= 0 and self.board[board_y][board_x] is not None:
                    return False
        return True

    def move(self, dx, dy):
        if self.is_valid(self.current_x + dx, self.current_y + dy, self.current_rotation):
            self.current_x += dx
            self.current_y += dy
            return True
        return False

    def rotate(self):
        new_rotation = self.current_rotation + 1
        for offset in (0, -1, 1, -2, 2):
            if self.is_valid(self.current_x + offset, self.current_y, new_rotation):
                self.current_x += offset
                self.current_rotation = new_rotation
                return

    def hard_drop(self):
        while self.move(0, 1):
            pass
        self.lock_piece()

    def lock_piece(self):
        for row_index, row in enumerate(self.get_shape()):
            for column_index, cell in enumerate(row):
                if cell != "." and self.current_y + row_index >= 0:
                    self.board[self.current_y + row_index][self.current_x + column_index] = self.current_type
        self.clear_lines()
        self.spawn_piece()

    def clear_lines(self):
        remaining = [row for row in self.board if any(cell is None for cell in row)]
        cleared = BOARD_HEIGHT - len(remaining)
        self.board = [[None] * BOARD_WIDTH for _ in range(cleared)] + remaining
        if cleared:
            self.lines += cleared
            self.score += [0, 100, 300, 500, 800][cleared] * self.difficulty["multiplier"]


def draw_text(screen, font, text, position, color=(235, 238, 240), center=False):
    surface = font.render(text, True, color)
    rect = surface.get_rect()
    if center:
        rect.center = position
    else:
        rect.topleft = position
    screen.blit(surface, rect)


def draw_cell(screen, x, y, color, size=CELL_SIZE, origin=(BOARD_X, BOARD_Y)):
    left = origin[0] + x * size
    top = origin[1] + y * size
    pygame.draw.rect(screen, color, (left + 1, top + 1, size - 2, size - 2), border_radius=3)
    highlight = tuple(min(255, value + 35) for value in color)
    pygame.draw.line(screen, highlight, (left + 3, top + 3), (left + size - 4, top + 3), 2)


def draw_game(screen, fonts, game):
    screen.fill((22, 25, 29))
    board_rect = pygame.Rect(BOARD_X, BOARD_Y, BOARD_WIDTH * CELL_SIZE, BOARD_HEIGHT * CELL_SIZE)
    pygame.draw.rect(screen, (13, 15, 18), board_rect)
    for y, row in enumerate(game.board):
        for x, cell in enumerate(row):
            if cell:
                draw_cell(screen, x, y, COLORS[cell])
    if game.running:
        for row_index, row in enumerate(game.get_shape()):
            for column_index, cell in enumerate(row):
                if cell != ".":
                    draw_cell(screen, game.current_x + column_index, game.current_y + row_index, COLORS[game.current_type])
    pygame.draw.rect(screen, (55, 61, 68), board_rect, 2)

    panel_x = BOARD_X + BOARD_WIDTH * CELL_SIZE + 30
    draw_text(screen, fonts["title"], "TETRIS", (panel_x, 30))
    draw_text(screen, fonts["body"], game.difficulty["name"], (panel_x, 72), (255, 205, 75))
    draw_text(screen, fonts["body"], f"Score  {game.score}", (panel_x, 120))
    draw_text(screen, fonts["body"], f"Lines  {game.lines}", (panel_x, 150))
    draw_text(screen, fonts["small"], "NEXT", (panel_x, 205), (155, 165, 175))
    preview = pygame.Rect(panel_x, 230, 150, 100)
    pygame.draw.rect(screen, (13, 15, 18), preview, border_radius=4)
    shape = SHAPES[game.next_type][0]
    origin_x = panel_x + (150 - len(shape[0]) * 24) // 2
    origin_y = 230 + (100 - len(shape) * 24) // 2
    for y, row in enumerate(shape):
        for x, cell in enumerate(row):
            if cell != ".":
                draw_cell(screen, x, y, COLORS[game.next_type], 24, (origin_x, origin_y))
    draw_text(screen, fonts["small"], "Arrows: move / rotate", (panel_x, 370), (155, 165, 175))
    draw_text(screen, fonts["small"], "Space: hard drop", (panel_x, 395), (155, 165, 175))
    draw_text(screen, fonts["small"], "P: pause   ESC: menu", (panel_x, 420), (155, 165, 175))
    if game.paused:
        draw_text(screen, fonts["title"], "PAUSED", (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2), (255, 205, 75), True)
    elif not game.running:
        draw_text(screen, fonts["title"], "GAME OVER", (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2), (255, 105, 105), True)


def choose_difficulty(screen, fonts):
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key in (pygame.K_1, pygame.K_2, pygame.K_3):
                return chr(event.key)
        screen.fill((22, 25, 29))
        draw_text(screen, fonts["title"], "TETRIS", (WINDOW_WIDTH // 2, 110), center=True)
        draw_text(screen, fonts["body"], "Choose difficulty", (WINDOW_WIDTH // 2, 170), (155, 165, 175), True)
        draw_text(screen, fonts["body"], "1  Easy", (WINDOW_WIDTH // 2, 230), (120, 220, 145), True)
        draw_text(screen, fonts["body"], "2  Normal", (WINDOW_WIDTH // 2, 280), (255, 205, 75), True)
        draw_text(screen, fonts["body"], "3  Hard", (WINDOW_WIDTH // 2, 330), (255, 115, 115), True)
        draw_text(screen, fonts["small"], "Press 1, 2, or 3", (WINDOW_WIDTH // 2, 410), (155, 165, 175), True)
        pygame.display.flip()


def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Tetris")
    fonts = {
        "title": pygame.font.Font(None, 42),
        "body": pygame.font.Font(None, 28),
        "small": pygame.font.Font(None, 22),
    }
    clock = pygame.time.Clock()
    difficulty_key = choose_difficulty(screen, fonts)
    game = TetrisGame(difficulty_key)
    last_drop = pygame.time.get_ticks()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    difficulty_key = choose_difficulty(screen, fonts)
                    game = TetrisGame(difficulty_key)
                    last_drop = pygame.time.get_ticks()
                elif event.key == pygame.K_p and game.running:
                    game.paused = not game.paused
                elif event.key == pygame.K_r and not game.running:
                    game = TetrisGame(difficulty_key)
                    last_drop = pygame.time.get_ticks()
                elif game.running and not game.paused:
                    if event.key == pygame.K_LEFT:
                        game.move(-1, 0)
                    elif event.key == pygame.K_RIGHT:
                        game.move(1, 0)
                    elif event.key == pygame.K_DOWN:
                        game.move(0, 1)
                    elif event.key == pygame.K_UP:
                        game.rotate()
                    elif event.key == pygame.K_SPACE:
                        game.hard_drop()
        now = pygame.time.get_ticks()
        if game.running and not game.paused and now - last_drop >= game.difficulty["drop_delay"]:
            if not game.move(0, 1):
                game.lock_piece()
            last_drop = now
        draw_game(screen, fonts, game)
        pygame.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    main()
