import queue
import threading
import time
import cv2
from typing import List, Dict
from Board import Board
from Piece import Piece
from img import Img

class Game:
    def __init__(self, pieces: List[Piece], board: Board):
        self.pieces: Dict[str, Piece] = {}
        for idx, p in enumerate(pieces):
            # כדי למנוע התנגשות מפתחות, נותנים id ייחודי לכל כלי
            self.pieces[f"{p.piece_id}_{idx}"] = p
        self.board = board
        self.user_input_queue = queue.Queue()
        self._stop_user_input_thread = False
        self._user_input_thread = None

    def clone_board(self) -> Board:
        return self.board.clone()

    def start_user_input_thread(self):
        def user_input_loop():
            while not self._stop_user_input_thread:
                time.sleep(0.1)  # לדוגמה, אין כאן ממש קלט

        self._stop_user_input_thread = False
        self._user_input_thread = threading.Thread(target=user_input_loop, daemon=True)
        self._user_input_thread.start()

    def run(self):
        self.start_user_input_thread()
        while True:
            board_clone = self.clone_board()  # Board חדש עם תמונה ומידות
            frame = board_clone.img           # Img - תמונת הלוח

            cell_W_pix = board_clone.cell_W_pix
            cell_H_pix = board_clone.cell_H_pix

            for p in self.pieces.values():
                p.draw(frame, cell_W_pix, cell_H_pix)

            cv2.imshow("Game", frame.img)


            key = cv2.waitKey(1) & 0xFF
            if key == 27:  # ESC - יציאה
                break

        self._stop_user_input_thread = True
        if self._user_input_thread is not None:
            self._user_input_thread.join(timeout=1)
        cv2.destroyAllWindows()
