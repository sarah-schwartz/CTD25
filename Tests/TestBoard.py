# TestBoard.py

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../It1_interfaces')))

from Board import Board
from mock_img import MockImg

def test_board_with_mock():
    MockImg.reset()
    b = Board(
        cell_H_pix=10,
        cell_W_pix=10,
        cell_H_m=1,
        cell_W_m=1,
        W_cells=5,
        H_cells=5,
        img=MockImg()
    )
    b.img.draw_on(None, 10, 20)
    b.img.put_text("Hello", 5, 5, 12)

    assert MockImg.traj == [(10, 20)]
    assert MockImg.txt_traj == [((5, 5), "Hello")]
