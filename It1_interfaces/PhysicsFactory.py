from typing import Dict
from Board import Board
from Physics import Physics, MovePhysics

class PhysicsFactory:
    def __init__(self, board: Board):
        self.board = board

    def create(self, cfg: Dict, start_cell=(0,0)) -> Physics:
        speed = cfg.get("speed_m_per_sec", 0.0)
        duration = cfg.get("duration_ms", 0)

        if speed > 0:
            return MovePhysics(start_cell, self.board, speed_m_per_s=speed)
        return Physics(start_cell, self.board, speed_m_per_s=speed, duration_ms=duration)
