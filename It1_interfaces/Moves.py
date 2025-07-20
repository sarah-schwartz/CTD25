import pathlib
from typing import List, Tuple


class Moves:
    def __init__(self, txt_path: pathlib.Path, dims: Tuple[int, int]):
        """Initialize moves with rules from text file and board dimensions."""
        self.rules: List[Tuple[int, int]] = []
        self.rows, self.cols = dims

        # טוען חוקי תנועה מהקובץ
        with open(txt_path, "r") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                try:
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