from typing import Tuple, Optional
from Command import Command
from Board import Board

class Physics:
    def __init__(self, start_cell: Tuple[int, int],
                 board: Board, speed_m_s: float = 1.0):
        self.board = board
        self.cell = start_cell
        self.speed = speed_m_s
        self.last_update = None
        self.finished = False
        self.cmd: Optional[Command] = None

    def reset(self, cmd: Command):
        self.cmd = cmd
        self.last_update = None
        self.finished = False

    def update(self, now_ms: int) -> Command:
        self.last_update = now_ms
        return self.cmd

    def can_be_captured(self) -> bool:
        return True

    def can_capture(self) -> bool:
        return False

    def get_pos(self) -> Tuple[int, int]:
        # נחזיר את התא כמו שהוא (במטרים), תוכל להרחיב בהמשך עם חישוב מיקום מדויק
        return self.cell

class IdlePhysics(Physics):
    def update(self, now_ms: int) -> Command:
        self.last_update = now_ms
        return self.cmd or Command("idle")

class MovePhysics(Physics):
    def update(self, now_ms: int) -> Command:
        # כאן תוכל לממש מעבר תא בהתאם לזמן ומהירות
        self.last_update = now_ms
        # סימולציה בסיסית להשלמת מעבר
        self.finished = True
        return self.cmd or Command("move")

    def can_capture(self) -> bool:
        return True

    def can_be_captured(self) -> bool:
        return False
