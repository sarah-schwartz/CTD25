from Board import Board
import pathlib
from Graphics import Graphics

class GraphicsFactory:
    def __init__(self, board: Board):
        self.board = board

    def create(self, sprites_folder: pathlib.Path, cfg: dict) -> Graphics:
        fps = cfg.get("frames_per_sec", 6.0)
        loop = cfg.get("is_loop", True)
        return Graphics(
            sprites_folder=sprites_folder,
            board=self.board,
            loop=loop,
            fps=fps
        )