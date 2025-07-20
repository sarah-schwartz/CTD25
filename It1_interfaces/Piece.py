from Board import Board
from Command import Command
from State import State
import cv2  # לפי ההערה שלך, אם צריך להשתמש

class Piece:
    def __init__(self, piece_id: str, init_state: State):  # תוקן: __init__ במקום **init**
        """Initialize a piece with ID and initial state."""
        self.piece_id = piece_id
        self._state = init_state

    def on_command(self, cmd: Command, now_ms: int):
        """Handle a command for this piece."""
        if self.is_command_possible(cmd):
            self._state = self._state.process_command(cmd)
            self._state.update(now_ms)

    def is_command_possible(self, cmd: Command) -> bool:
        # תוכל לממש לפי הלוגיקה שלך, למשל לבדוק במצב הנוכחי
        return self._state.is_command_possible(cmd)

    def reset(self, start_ms: int):
        """Reset the piece to idle state."""
        self._state.reset()
        self._state.update(start_ms)

    def update(self, now_ms: int):
        """Update the piece state based on current time."""
        self._state.update(now_ms)

    def draw_on_board(self, board: Board, now_ms: int):
        """Draw the piece on the board with cooldown overlay."""
        # מדמה ציור של ה-state הנוכחי על הלוח
        img = self._state.get_img()
        pos = self._state.get_pos()
        # לדוגמא, אם יש לך פונקציית ציור בלוח:
        board.draw_img(img, pos)
        # אם יש צורך לצייר overlay של cooldown:
        # cooldown_pct = self._state.get_cooldown_percentage()
        # board.draw_cooldown_overlay(pos, cooldown_pct)