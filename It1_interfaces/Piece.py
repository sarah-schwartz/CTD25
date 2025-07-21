from typing import Tuple
from img import Img

class Piece:
    def __init__(self, piece_id: str, cell: Tuple[int, int], img: Img):
        self.piece_id = piece_id
        self.cell = cell
        self.img = img

    def draw(self, canvas: Img, cell_W_pix: int, cell_H_pix: int):
        x = self.cell[1] * cell_W_pix
        y = self.cell[0] * cell_H_pix
        self.img.draw_on(canvas, x, y)

    def get_position(self):
        return self.cell
