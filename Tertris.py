import random
import tkinter as tk


CELL_SIZE = 30
BOARD_WIDTH = 10
BOARD_HEIGHT = 20
DROP_DELAY = 500

COLORS = {
    "I": "#35c9e8",
    "J": "#4169e1",
    "L": "#f39c35",
    "O": "#f1d34b",
    "S": "#55c878",
    "T": "#a66cff",
    "Z": "#ef5b67",
}

SHAPES = {
    "I": [
        ["....", "IIII", "....", "...."],
        ["..I.", "..I.", "..I.", "..I."],
    ],
    "J": [
        ["J..", "JJJ", "..."],
        [".JJ", ".J.", ".J."],
        ["...", "JJJ", "..J"],
        [".J.", "J..", "J.."],
    ],
    "L": [
        ["..L", "LLL", "..."],
        ["L..", ".L.", ".L."],
        ["...", "LLL", "L.."],
        [".L.", ".L.", ".LL"],
    ],
    "O": [["OO", "OO"]],
    "S": [
        [".SS", "SS.", "..."],
        ["S..", "SS.", ".S."],
    ],
    "T": [
        [".T.", "TTT", "..."],
        [".T.", ".TT", ".T."],
        ["...", "TTT", ".T."],
        [".T.", "TT.", ".T."],
    ],
    "Z": [
        ["ZZ.", ".ZZ", "..."],
        [".Z.", "ZZ.", "Z.."],
    ],
}


class TetrisGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Tetris")
        self.root.resizable(False, False)
        self.root.configure(bg="#202124")
        self.running = False
        self.paused = False
        self.after_id = None

        self.canvas = tk.Canvas(
            root,
            width=BOARD_WIDTH * CELL_SIZE,
            height=BOARD_HEIGHT * CELL_SIZE,
            bg="#111315",
            highlightthickness=0,
        )
        self.canvas.grid(row=0, column=0, rowspan=2, padx=(12, 8), pady=12)

        side = tk.Frame(root, bg="#202124", width=150)
        side.grid(row=0, column=1, sticky="n", padx=(8, 12), pady=12)
        side.grid_propagate(False)

        tk.Label(
            side, text="TETRIS", font=("Segoe UI", 18, "bold"),
            fg="#ffffff", bg="#202124"
        ).pack(anchor="w")
        self.score_label = tk.Label(
            side, text="Score: 0", font=("Segoe UI", 12),
            fg="#f1f3f4", bg="#202124"
        )
        self.score_label.pack(anchor="w", pady=(12, 8))
        tk.Label(
            side, text="NEXT", font=("Segoe UI", 9, "bold"),
            fg="#9aa0a6", bg="#202124"
        ).pack(anchor="w")
        self.next_canvas = tk.Canvas(
            side, width=120, height=100, bg="#111315", highlightthickness=0
        )
        self.next_canvas.pack(pady=(4, 16))
        self.status_label = tk.Label(
            side, text="Press Enter to start", font=("Segoe UI", 10),
            fg="#9aa0a6", bg="#202124", wraplength=140, justify="left"
        )
        self.status_label.pack(anchor="w", pady=(0, 12))
        tk.Label(
            side, text="Arrows: move / rotate\nSpace: hard drop\nP: pause\nR: restart",
            font=("Segoe UI", 9), fg="#9aa0a6", bg="#202124", justify="left"
        ).pack(anchor="w")

        self.root.bind("<Key>", self.handle_key)
        self.reset()

    def reset(self):
        if self.after_id is not None:
            self.root.after_cancel(self.after_id)
            self.after_id = None
        self.board = [[None for _ in range(BOARD_WIDTH)] for _ in range(BOARD_HEIGHT)]
        self.score = 0
        self.current_type = None
        self.current_rotation = 0
        self.current_x = 0
        self.current_y = 0
        self.next_type = random.choice(list(SHAPES))
        self.running = False
        self.paused = False
        self.score_label.config(text="Score: 0")
        self.status_label.config(text="Press Enter to start")
        self.draw()

    def start(self):
        self.reset()
        self.running = True
        self.spawn_piece()
        self.status_label.config(text="Playing")
        self.tick()

    def spawn_piece(self):
        self.current_type = self.next_type
        self.current_rotation = 0
        self.next_type = random.choice(list(SHAPES))
        shape = self.get_shape()
        self.current_x = (BOARD_WIDTH - len(shape[0])) // 2
        self.current_y = 0
        if not self.is_valid(self.current_x, self.current_y, self.current_rotation):
            self.game_over()

    def get_shape(self, piece_type=None, rotation=None):
        piece_type = piece_type or self.current_type
        rotation = self.current_rotation if rotation is None else rotation
        return SHAPES[piece_type][rotation % len(SHAPES[piece_type])]

    def is_valid(self, x, y, rotation):
        for row_index, row in enumerate(self.get_shape(rotation=rotation)):
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
        if not self.running or self.paused:
            return False
        if self.is_valid(self.current_x + dx, self.current_y + dy, self.current_rotation):
            self.current_x += dx
            self.current_y += dy
            self.draw()
            return True
        return False

    def rotate(self):
        if not self.running or self.paused:
            return
        new_rotation = self.current_rotation + 1
        for offset in (0, -1, 1, -2, 2):
            if self.is_valid(self.current_x + offset, self.current_y, new_rotation):
                self.current_x += offset
                self.current_rotation = new_rotation
                self.draw()
                return

    def hard_drop(self):
        if not self.running or self.paused:
            return
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
        self.draw()

    def clear_lines(self):
        remaining = [row for row in self.board if any(cell is None for cell in row)]
        cleared = BOARD_HEIGHT - len(remaining)
        self.board = [[None] * BOARD_WIDTH for _ in range(cleared)] + remaining
        if cleared:
            self.score += [0, 100, 300, 500, 800][cleared]
            self.score_label.config(text=f"Score: {self.score}")

    def tick(self):
        if not self.running:
            return
        if not self.paused:
            if not self.move(0, 1):
                self.lock_piece()
            self.after_id = self.root.after(DROP_DELAY, self.tick)

    def toggle_pause(self):
        if not self.running:
            return
        self.paused = not self.paused
        self.status_label.config(text="Paused" if self.paused else "Playing")
        self.draw()

    def game_over(self):
        self.running = False
        self.status_label.config(text="Game over\nPress R to restart")
        self.draw()

    def draw_cell(self, canvas, x, y, color, size=CELL_SIZE, origin=(0, 0)):
        origin_x, origin_y = origin
        left = origin_x + x * size
        top = origin_y + y * size
        canvas.create_rectangle(left + 1, top + 1, left + size - 1, top + size - 1, fill=color, outline="#202124")

    def draw(self):
        self.canvas.delete("all")
        for y, row in enumerate(self.board):
            for x, cell in enumerate(row):
                if cell:
                    self.draw_cell(self.canvas, x, y, COLORS[cell])
        if self.current_type and self.running:
            for row_index, row in enumerate(self.get_shape()):
                for column_index, cell in enumerate(row):
                    if cell != ".":
                        self.draw_cell(
                            self.canvas,
                            self.current_x + column_index,
                            self.current_y + row_index,
                            COLORS[self.current_type],
                        )
        self.next_canvas.delete("all")
        shape = SHAPES[self.next_type][0]
        offset_x = (4 - len(shape[0])) * 15
        offset_y = (4 - len(shape)) * 12
        for y, row in enumerate(shape):
            for x, cell in enumerate(row):
                if cell != ".":
                    self.draw_cell(
                        self.next_canvas, x, y, COLORS[self.next_type], size=24,
                        origin=(offset_x, offset_y)
                    )

    def handle_key(self, event):
        key = event.keysym.lower()
        if key in ("return", "kp_enter") and not self.running:
            self.start()
        elif key == "r":
            self.start()
        elif key == "p":
            self.toggle_pause()
        elif key == "left":
            self.move(-1, 0)
        elif key == "right":
            self.move(1, 0)
        elif key == "down":
            if not self.move(0, 1) and self.running and not self.paused:
                self.lock_piece()
        elif key == "up":
            self.rotate()
        elif key == "space":
            self.hard_drop()


if __name__ == "__main__":
    window = tk.Tk()
    game = TetrisGame(window)
    window.mainloop()