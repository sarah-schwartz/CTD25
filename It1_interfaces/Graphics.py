import pathlib
from typing import List, Dict
from img import Img
from Command import Command
from Board import Board


class Graphics:
    def __init__(self,
                 sprites_folder: pathlib.Path,
                 board: Board,
                 loop: bool = True,
                 fps: float = 6.0):
        """Initialize graphics with sprites folder, cell size, loop setting, and FPS."""
        self.frame_time_ms = int(1000 / fps)
        self.loop = loop
        self.board = board
        self.frames_by_state: Dict[str, List[Img]] = {}

        # Load all subfolders as states
        for state_dir in sprites_folder.iterdir():
            if state_dir.is_dir():
                frames = []
                for img_path in sorted(state_dir.glob("*.png")):
                    frames.append(Img(img_path))
                self.frames_by_state[state_dir.name] = frames

        # Default values
        self.current_state = "idle"
        self.current_frame = 0
        self.last_update_ms = None
        self.finished = False

    def copy(self):
        """Create a shallow copy of the graphics object."""
        new_gfx = Graphics.__new__(Graphics)  # Bypass __init__
        new_gfx.frame_time_ms = self.frame_time_ms
        new_gfx.loop = self.loop
        new_gfx.board = self.board
        new_gfx.frames_by_state = self.frames_by_state  # Shared reference (shallow copy)
        new_gfx.current_state = self.current_state
        new_gfx.current_frame = self.current_frame
        new_gfx.last_update_ms = self.last_update_ms
        new_gfx.finished = self.finished
        return new_gfx

    def reset(self, cmd: Command):
        """Reset the animation with a new command."""
        state = cmd.type if cmd.type in self.frames_by_state else "idle"
        self.current_state = state
        self.current_frame = 0
        self.last_update_ms = None
        self.finished = False

    def update(self, now_ms: int):
        """Advance animation frame based on game-loop time."""
        if self.finished:
            return

        if self.last_update_ms is None:
            self.last_update_ms = now_ms
            return

        elapsed = now_ms - self.last_update_ms
        if elapsed >= self.frame_time_ms:
            frames_to_advance = elapsed // self.frame_time_ms
            self.current_frame += frames_to_advance
            self.last_update_ms += frames_to_advance * self.frame_time_ms

            max_frames = len(self.frames_by_state[self.current_state])
            if self.current_frame >= max_frames:
                if self.loop:
                    self.current_frame %= max_frames
                else:
                    self.current_frame = max_frames - 1
                    self.finished = True

    def get_img(self) -> Img:
        """Get the current frame image."""
        return self.frames_by_state[self.current_state][self.current_frame]
