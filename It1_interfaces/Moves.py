import pathlib
from typing import List, Tuple


class Moves:
    def __init__(self, txt_path: pathlib.Path, dims: Tuple[int, int]):
        """Initialize moves with rules from a text file and board dimensions."""
        self.rules: List[Tuple[int, int]] = []
        self.rows, self.cols = dims

        # Load move rules from file
        with open(txt_path, "r") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                try:
                    # תמיכה בפורמט: dr,dc או dr,dc:type
                    if ":" in line:
                        move_part, move_type = line.split(":", 1)
                        dr, dc = map(int, move_part.split(","))
                    else:
                        dr, dc = map(int, line.split(","))
                    self.rules.append((dr, dc))
                except ValueError:
                    raise ValueError(f"Invalid line in moves file: {line}")

    def get_moves(self, r: int, c: int) -> List[Tuple[int, int]]:
        """Get all possible moves from a given position (r, c)."""
        moves = []
        for dr, dc in self.rules:
            nr, nc = r + dr, c + dc
            if 0 <= nr < self.rows and 0 <= nc < self.cols:
                moves.append((nr, nc))
        return moves

    def is_valid_move(self, start_cell: Tuple[int, int], end_cell: Tuple[int, int]) -> bool:
        """Check if a move from start_cell to end_cell is valid."""
        r1, c1 = start_cell
        r2, c2 = end_cell
        dr, dc = r2 - r1, c2 - c1
        return (dr, dc) in self.rules