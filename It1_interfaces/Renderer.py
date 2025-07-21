import pathlib
from typing import Tuple
from Board import Board
from StateMachine import StateMachine

class Renderer:
    def __init__(self, board: Board, state_machine: StateMachine):
        self.board = board
        self.state_machine = state_machine

    def render(self):
        """
        Render the current frame of the current state at the piece's cell.
        This should be called once per frame by the game loop.
        """
        current_state = self.state_machine.current_state
        current_frame = current_state.get_current_frame()

        cell = current_state.cell
        x_pix = cell[1] * self.board.cell_W_pix
        y_pix = cell[0] * self.board.cell_H_pix

        self.board.img.paste(current_frame, (x_pix, y_pix))
