import pathlib
from typing import List, Optional
from img import Img
from Board import Board

class Graphics:
    def __init__(self,
                 sprites_folder: pathlib.Path,
                 board: Board,
                 loop: bool = True,
                 fps: float = 6.0):
        
        png_files = sorted(list(sprites_folder.glob("*.png")))
        
        cell_w = board.cell_W_pix
        cell_h = board.cell_H_pix

        self.frames: List[Img] = []
        for p in png_files:
            img = Img()
            img.read(str(p), size=(cell_w, cell_h))
            self.frames.append(img)
       

        self.frame_time_ms = int(1000 / fps) if fps > 0 else float('inf')
        self.loop = loop
        self.board = board
        self.current_frame = 0
        self.last_update_ms = None
        self.finished = not self.frames
    def copy(self):
        new_gfx = Graphics.__new__(Graphics)
        new_gfx.__dict__.update(self.__dict__)
        new_gfx.reset()
        return new_gfx

    def reset(self):
        self.current_frame = 0
        self.last_update_ms = None
        self.finished = not self.frames

    def is_finished(self) -> bool:
        return self.finished
        
    def update(self, now_ms: int):
        if self.finished or not self.frames:
            return

        if self.last_update_ms is None:
            self.last_update_ms = now_ms
            return

        elapsed = now_ms - self.last_update_ms
        if elapsed >= self.frame_time_ms:
            frames_to_advance = elapsed // self.frame_time_ms
            self.current_frame += frames_to_advance
            self.last_update_ms += frames_to_advance * self.frame_time_ms

            if self.current_frame >= len(self.frames):
                if self.loop:
                    self.current_frame %= len(self.frames)
                else:
                    self.current_frame = len(self.frames) - 1
                    self.finished = True

    def draw_on(self, canvas: Img, x: int, y: int):
        if self.frames and self.current_frame < len(self.frames):
            self.frames[self.current_frame].draw_on(canvas, int(x), int(y))

