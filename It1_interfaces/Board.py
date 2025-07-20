from dataclasses import dataclass
from img import Img


@dataclass
class Board:
    cell_H_pix: int     # גובה תא בפיקסלים
    cell_W_pix: int     # רוחב תא בפיקסלים
    cell_H_m: int       # גובה תא במטרים
    cell_W_m: int       # רוחב תא במטרים
    W_cells: int        # מספר תאים לרוחב
    H_cells: int        # מספר תאים לגובה
    img: Img            # תמונת הלוח

    def clone(self) -> "Board":
        """יוצר עותק של הלוח כולל עותק של התמונה כדי שלא תהיה גישה משותפת לאותה תמונה."""
        return Board(
            cell_H_pix=self.cell_H_pix,
            cell_W_pix=self.cell_W_pix,
            cell_H_m=self.cell_H_m,
            cell_W_m=self.cell_W_m,
            W_cells=self.W_cells,
            H_cells=self.H_cells,
            img=self.img.copy()  # assumes Img has a .copy() method
        )
