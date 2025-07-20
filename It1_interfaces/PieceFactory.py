import pathlib
from typing import Dict, Tuple
import json
from Board import Board
from GraphicsFactory import GraphicsFactory
from Moves import Moves
from PhysicsFactory import PhysicsFactory
from Piece import Piece
from State import State


class PieceFactory:
    def __init__(self, board: Board, pieces_root: pathlib.Path):
        """Initialize piece factory with board and
        generate the library of piece templates from the pieces directory."""
        self.board = board
        self.pieces_root = pieces_root

        self.physics_factory = PhysicsFactory(board)
        self.graphics_factory = GraphicsFactory(board)
        self.moves = Moves()

        # Cache of piece state machines by piece type
        self.state_machine_templates: Dict[str, State] = {}

        # Load all pieces from directory
        for piece_dir in pieces_root.iterdir():
            if piece_dir.is_dir():
                piece_type = piece_dir.name
                state_machine = self._build_state_machine(piece_dir)
                self.state_machine_templates[piece_type] = state_machine

    def _build_state_machine(self, piece_dir: pathlib.Path) -> State:
        """Build a state machine for a piece from its directory."""
        # קריאה של קובץ JSON/קונפיג של מצבים
        config_path = piece_dir / "states.json"
        with open(config_path, "r", encoding="utf-8") as f:
            state_cfg = json.load(f)

        # כלול יצירת גרפיקות והפיזיקה
        sprites_folder = piece_dir / "sprites"

        # נניח שלכל מצב בקונפיג יש הגדרות גרפיקה ופיזיקה
        # ניצור אובייקט State ראשוני על בסיס הקונפיג (אתה תצטרך לממש State לפי הקונפיג)
        initial_state = State.from_config(
            state_cfg=state_cfg,
            sprites_folder=sprites_folder,
            board=self.board,
            physics_factory=self.physics_factory,
            graphics_factory=self.graphics_factory,
            moves=self.moves
        )

        return initial_state

    def create_piece(self, p_type: str, cell: Tuple[int, int]) -> Piece:
        """Create a piece of the specified type at the given cell."""
        if p_type not in self.state_machine_templates:
            raise ValueError(f"Unknown piece type '{p_type}'")

        # צור עותק של מכונת המצבים לתוך מצב התחלתי חדש
        initial_state = self.state_machine_templates[p_type].copy()
        initial_state.set_position(cell)

        # צור אובייקט Piece עם ה-state machine
        piece = Piece(piece_id=p_type, init_state=initial_state)
        piece.reset(0)  # reset start_ms ל-0 או לפי הצורך
        return piece
