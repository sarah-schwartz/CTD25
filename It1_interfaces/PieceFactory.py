from typing import Tuple, Dict
from Piece import Piece
from img import Img
import cv2
import pathlib

class PieceFactory:
    def __init__(self, board, pieces_root: pathlib.Path):
        self.board = board
        self.pieces_root = pieces_root

    def create_piece(self, piece_id, cell, config):
        sprite_path = self.pieces_root / config["sprite"]
        size = (self.board.cell_W_pix, self.board.cell_H_pix)

        piece_img = Img().read(
            str(sprite_path),
            size=size,
            keep_aspect=False,
            interpolation=cv2.INTER_AREA
        )

        return Piece(piece_id, cell, piece_img)
