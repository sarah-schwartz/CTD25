from typing import Tuple
from img import Img
from Command import Command
from State import State
import cv2
class Piece:
    def __init__(self, piece_id: str, cell: Tuple[int, int], img: Img):
        self.piece_id = piece_id
        self.cell = cell
        self.img = img

    def draw_on_board(self, canvas: Img, cell_W_pix: int, cell_H_pix: int):
        x = self.cell[1] * cell_W_pix
        y = self.cell[0] * cell_H_pix
        self.img.draw_on(canvas, x, y)

    def on_command(self, cmd: Command, now_ms: int):
        """Handle a command for this piece."""
        if self.is_command_possible(cmd):
            self._state = self._state.process_command(cmd)
            self._state.update(now_ms)
        pass
    def belongs_to_player_one(self) -> bool:
        return "W" in self.piece_id

    
    def reset(self, start_ms: int):
        self._state.reset()
        """Reset the piece to idle state."""
        pass

    def update(self, now_ms: int):
        """Update the piece state based on current time."""
        pass