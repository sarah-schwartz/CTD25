from typing import Tuple, Dict
from Piece import Piece
import pathlib
import numpy as np
from State import StateManager
from PhysicsFactory import PhysicsFactory
from GraphicsFactory import GraphicsFactory
from Board import Board
from Moves import Moves

class PieceFactory:
    def __init__(self, board: Board, pieces_root: pathlib.Path):
        self.board = board
        self.pieces_root = pieces_root
        self.physics_factory = PhysicsFactory(self.board)
        self.graphics_factory = GraphicsFactory(self.board)
        self.state_manager_templates: Dict[str, StateManager] = {}
        self.moves_templates: Dict[str, Moves] = {}

    def create_piece(self, piece_id: str, start_cell: Tuple[int, int]) -> Piece:
        unique_piece_id = f"{piece_id}_{start_cell[0]}_{start_cell[1]}"
        print(f"Creating piece with id {unique_piece_id} and type {piece_id}")
        piece_type = piece_id.split("_")[0]
        piece_type_folder = self.pieces_root / piece_type


        # Check if the piece type already exists in the templates dictionary
        if piece_type not in self.state_manager_templates:
            print(f"Loading state manager template for piece type {piece_type}")
            sm_template = StateManager.from_config(
                piece_folder=piece_type_folder,
                board=self.board,
                physics_factory=self.physics_factory,
                graphics_factory=self.graphics_factory
            )
            self.state_manager_templates[piece_type] = sm_template



        # תמיד יוצרים עותק חדש של ה־StateManager (עמוק!)
        new_sm = self.state_manager_templates[piece_type].copy()

        # קביעת המיקום ההתחלתי במצב ההתחלתי
        initial_state = new_sm.states[new_sm.current_state.name]
        initial_state._physics.cell = start_cell
        initial_state._physics.current_pos_pix = np.array(
            [start_cell[1] * self.board.cell_W_pix, start_cell[0] * self.board.cell_H_pix],
            dtype=float
        )

        # טעינת Moves מה-cached או יצירה חדשה
        if piece_type not in self.moves_templates:
            moves_config_path = piece_type_folder / "moves.txt"
            self.moves_templates[piece_type] = Moves(moves_config_path, (self.board.H_cells, self.board.W_cells))

        moves = self.moves_templates[piece_type]
        is_player_one = "W" in piece_id

        return Piece(piece_id, is_player_one, new_sm, moves)
