from typing import Tuple
from img import Img
from Command import Command
from StateManager import StateManager
from State import State
import copy
from Moves import Moves
class Piece:
    def __init__(self, piece_id: str, player_one: bool, state_manager: StateManager, moves: Moves):
        self.piece_id = piece_id
        self.player_one = player_one
        self.state_manager = state_manager
        self.moves = moves        
        self.cell: Tuple[int, int] = self.state_manager.current_state._physics.get_pos()
        self.selected = False
        self.move_count = 0

    def clone(self):
        new_sm = self.state_manager.copy()
        return Piece(self.piece_id, self.player_one, new_sm)

    def draw_on_board(self, canvas: Img):
        current_physics = self.state_manager.current_state._physics
        current_graphics = self.state_manager.current_state._graphics
        
        pos_pix = current_physics.get_pos_pix()
        current_graphics.draw_on(canvas, pos_pix[0], pos_pix[1])

    def on_command(self, cmd: Command):
        self.state_manager.process_command(cmd)

    def update(self, now_ms: int):
        self.state_manager.update(now_ms)
        self.cell = self.state_manager.current_state._physics.get_pos()