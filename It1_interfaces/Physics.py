# Physics.py (הגרסה המעודכנת)

from typing import Tuple, Optional
from Command import Command
from Board import Board
import numpy as np

class Physics:
    """מחלקה בסיסית לפיזיקה. תומכת עכשיו גם במצבי המתנה מוגדרים בזמן."""
    def __init__(self, start_cell: Tuple[int, int], board: Board, speed_m_s: float = 0.0, duration_ms: int = 0):
        self.board = board
        self.cell = start_cell
        self.speed = speed_m_s
        self.duration_ms = duration_ms # <<< משך המצב באלפיות השנייה
        self.cmd: Optional[Command] = None
        self.current_pos_pix = np.array([start_cell[1] * self.board.cell_W_pix, start_cell[0] * self.board.cell_H_pix], dtype=float)
        self.elapsed_time_ms = 0 # <<< כמה זמן עבר מתחילת המצב
        self.last_update = None
        self.finished = False

    def copy(self):
        return Physics(self.cell, self.board, self.speed, self.duration_ms)

    def reset(self, cmd: Optional[Command]):
        self.cmd = cmd
        self.last_update = None
        self.finished = False
        self.elapsed_time_ms = 0  
        if cmd and cmd.type == "move":
            target_cell = tuple(cmd.params.get("target", self.cell))
            self.cell = target_cell
            self.current_pos_pix = np.array([target_cell[1] * self.board.cell_W_pix, target_cell[0] * self.board.cell_H_pix], dtype=float)


    def update(self, now_ms: int):
        if self.finished:
            return

        if self.last_update is None:
            self.last_update = now_ms
            if self.duration_ms == 0 and self.speed == 0:
                self.finished = True
            return

        delta_ms = now_ms - self.last_update
        self.last_update = now_ms
        self.elapsed_time_ms += delta_ms
        if self.duration_ms > 0 and self.elapsed_time_ms >= self.duration_ms:
            self.finished = True

    def get_pos(self) -> Tuple[int, int]:
        return self.cell

    def get_pos_pix(self) -> Tuple[float, float]:
        return self.current_pos_pix

    def is_finished(self) -> bool:
        return self.finished

class MovePhysics(Physics):
    def __init__(self, start_cell: Tuple[int, int], board: Board, speed_m_s: float):
        super().__init__(start_cell, board, speed_m_s=speed_m_s)
        self.start_pos_pix = None
        self.end_pos_pix = None
        self.total_move_time_ms = 0
        
    def copy(self):
        return MovePhysics(self.cell, self.board, self.speed)

    def reset(self, cmd: Command):
        super().reset(cmd) 
        if not cmd or cmd.type != "move":
            self.finished = True
            return

        start_cell = self.cell 
        target_cell = tuple(cmd.params.get("target"))

        if start_cell == target_cell or self.speed <= 0:
            self.finished = True
            return

        self.start_pos_pix = np.array([start_cell[1] * self.board.cell_W_pix, start_cell[0] * self.board.cell_H_pix], dtype=float)
        self.end_pos_pix = np.array([target_cell[1] * self.board.cell_W_pix, target_cell[0] * self.board.cell_H_pix], dtype=float)
        self.current_pos_pix = self.start_pos_pix.copy()

        distance_pix = np.linalg.norm(self.end_pos_pix - self.start_pos_pix)
        pixels_per_meter = self.board.cell_W_pix / self.board.cell_W_m if self.board.cell_W_m > 0 else 1
        distance_m = distance_pix / pixels_per_meter

        self.total_move_time_ms = (distance_m / self.speed) * 1000 if self.speed > 0 else 0
        self.elapsed_time_ms = 0
        self.finished = False


    def update(self, now_ms: int):
        if self.finished:
            return

        if self.last_update is None:
            self.last_update = now_ms
            return

        delta_ms = now_ms - self.last_update
        self.last_update = now_ms
        self.elapsed_time_ms += delta_ms

        if self.total_move_time_ms == 0 or self.elapsed_time_ms >= self.total_move_time_ms:
            self.current_pos_pix = self.end_pos_pix
            self.cell = tuple(self.cmd.params.get("target"))
            self.finished = True
        else:
            ratio = self.elapsed_time_ms / self.total_move_time_ms
            self.current_pos_pix = self.start_pos_pix + ratio * (self.end_pos_pix - self.start_pos_pix)


    def get_pos(self) -> Tuple[int, int]:
        if self.finished and self.cmd:
            return tuple(self.cmd.params.get("target", self.cell))
        return self.cell