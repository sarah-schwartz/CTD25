from typing import Tuple, Optional
import numpy as np
from Command import Command
from Board import Board


class Physics:
    """
    Base class for handling simple physics behaviors,
    such as waiting or instant transitions on a board.
    """

    def __init__(
        self,
        start_cell: Tuple[int, int],
        board: Board,
        speed_m_per_s: float = 0.0,
        duration_ms: int = 0
    ):
        self.board = board
        self.cell = start_cell
        self.speed = speed_m_per_s
        self.duration_ms = duration_ms  # Duration of state in milliseconds
        self.command: Optional[Command] = None

        # Convert cell coordinates to pixel coordinates: [x, y] = [col * width, row * height]
        self.current_pos_pix = np.array([
            start_cell[1] * board.cell_W_pix,
            start_cell[0] * board.cell_H_pix
        ], dtype=float)

        self.elapsed_time_ms = 0
        self.last_update_time = None
        self.finished = False

    def copy(self) -> "Physics":
        return Physics(self.cell, self.board, self.speed, self.duration_ms)

    def reset(self, command: Optional[Command]):
        """
        Resets the state with a new command.
        """
        self.command = command
        self.elapsed_time_ms = 0
        self.finished = False
        self.last_update_time = None

        if command and command.type == "move":
            self._apply_move_command(command)

    def _apply_move_command(self, command: Command):
        """
        Moves the object instantly to the target cell (used in base class).
        """
        target_cell = tuple(command.params.get("target", self.cell))
        self.cell = target_cell
        self.current_pos_pix = np.array([
            target_cell[1] * self.board.cell_W_pix,
            target_cell[0] * self.board.cell_H_pix
        ], dtype=float)

    def update(self, now_ms: int):
        """
        Updates the time tracking logic. If enough time has passed, mark as finished.
        """
        if self.finished:
            return

        if self.last_update_time is None:
            self.last_update_time = now_ms
            if self.duration_ms == 0 and self.speed == 0:
                self.finished = True
            return

        delta = now_ms - self.last_update_time
        self.elapsed_time_ms += delta
        self.last_update_time = now_ms

        if self.duration_ms > 0 and self.elapsed_time_ms >= self.duration_ms:
            self.finished = True

    def get_pos(self) -> Tuple[int, int]:
        return self.cell

    def get_pos_pix(self) -> Tuple[float, float]:
        return tuple(self.current_pos_pix)

    def is_finished(self) -> bool:
        return self.finished


class MovePhysics(Physics):
    """
    Physics class for animated movement between two cells on a grid.
    """

    def __init__(self, start_cell: Tuple[int, int], board: Board, speed_m_per_s: float):
        super().__init__(start_cell, board, speed_m_per_s)
        self.start_pos_pix: Optional[np.ndarray] = None
        self.end_pos_pix: Optional[np.ndarray] = None
        self.total_move_duration_ms = 0

    def copy(self) -> "MovePhysics":
        return MovePhysics(self.cell, self.board, self.speed)

    def reset(self, command: Command):
        """
        Prepares movement from current cell to target cell.
        If movement is invalid or speed is zero, mark as finished.
        """
        if not command or command.type != "move":
            self.finished = True
            return

        self.command = command
        self.elapsed_time_ms = 0
        self.last_update_time = None

        start_cell = self.cell
        target_cell = tuple(command.params.get("target"))
        if start_cell == target_cell or self.speed <= 0:
            self.finished = True
            return

        self._initialize_positions(start_cell, target_cell)
        self._compute_move_duration()
        self.finished = False

    def _initialize_positions(self, start_cell: Tuple[int, int], target_cell: Tuple[int, int]):
        """
        Converts start and target cells to pixel coordinates.
        """
        self.start_pos_pix = np.array([
            start_cell[1] * self.board.cell_W_pix,
            start_cell[0] * self.board.cell_H_pix
        ], dtype=float)

        self.end_pos_pix = np.array([
            target_cell[1] * self.board.cell_W_pix,
            target_cell[0] * self.board.cell_H_pix
        ], dtype=float)

        self.current_pos_pix = self.start_pos_pix.copy()

    def _compute_move_duration(self):
        """
        Calculates the time needed to complete the movement in milliseconds.
        """
        pixel_distance = np.linalg.norm(self.end_pos_pix - self.start_pos_pix)
        pixels_per_meter = self.board.cell_W_pix / self.board.cell_W_m if self.board.cell_W_m > 0 else 1
        distance_m = pixel_distance / pixels_per_meter
        self.total_move_duration_ms = (distance_m / self.speed) * 1000 if self.speed > 0 else 0

    def update(self, now_ms: int):
        """
        Updates the current position according to elapsed time.
        """
        if self.finished:
            return

        if self.last_update_time is None:
            self.last_update_time = now_ms
            return

        delta = now_ms - self.last_update_time
        self.last_update_time = now_ms
        self.elapsed_time_ms += delta

        if self.elapsed_time_ms >= self.total_move_duration_ms:
            self._finish_movement()
        else:
            self._interpolate_position()

    def _interpolate_position(self):
        """
        Updates the current position using linear interpolation between start and end.
        """
        ratio = self.elapsed_time_ms / self.total_move_duration_ms
        self.current_pos_pix = self.start_pos_pix + ratio * (self.end_pos_pix - self.start_pos_pix)

    def _finish_movement(self):
        """
        Marks movement as completed and snaps to final position.
        """
        self.current_pos_pix = self.end_pos_pix
        self.cell = tuple(self.command.params.get("target"))
        self.finished = True

    def get_pos(self) -> Tuple[int, int]:
        """
        Returns the current logical cell. If movement is finished, returns the target.
        """
        if self.finished and self.command:
            return tuple(self.command.params.get("target", self.cell))
        return self.cell
