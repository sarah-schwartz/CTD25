from typing import Tuple, Dict
from Command import Command
from Board import Board
from Physics import Physics, IdlePhysics, MovePhysics

class PhysicsFactory:
    def __init__(self, board: Board):
        self.board = board

    def create(self, start_cell: Tuple[int, int], cmd: Command, cfg: Dict) -> Physics:
        """Create a Physics instance (Idle or Move) based on command type."""
        speed = cfg.get("speed_m_s", 1.0)

        if cmd.type == "move":
            return MovePhysics(start_cell, self.board, speed)
        else:
            return IdlePhysics(start_cell, self.board, speed)
