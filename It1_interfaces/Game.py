import inspect
import pathlib
import queue
import threading
import time
import cv2
import math
from typing import List, Dict, Tuple, Optional
from Board   import Board
from Command import Command
from Piece   import Piece
from img     import Img


class InvalidBoard(Exception):
    pass


class Game:
    def __init__(self, pieces: List[Piece], board: Board):
        """Initialize the game with pieces, board, and optional event bus."""
        self.pieces: Dict[str, Piece] = {p.piece_id: p for p in pieces}
        self.board = board
        self.user_input_queue = queue.Queue()
        self._stop_user_input_thread = False
        self._user_input_thread = None

    # ─── helpers ─────────────────────────────────────────────────────────────
    def game_time_ms(self) -> int:
        """Return the current game time in milliseconds."""
        return int(time.monotonic() * 1000)

    def clone_board(self) -> Board:
        """
        Return a **brand-new** Board wrapping a copy of the background pixels
        so we can paint sprites without touching the pristine board.
        """
        return self.board.clone()

    def start_user_input_thread(self):
        """Start the user input thread for mouse handling."""
        def user_input_loop():
            while not self._stop_user_input_thread:
                # כאן אפשר לממש קוד למעקב אחרי אירועים חיצוניים כמו לחיצות עכבר
                # לדוגמה: שימוש ב-opencv או ספרייה אחרת ללכידת אירועי עכבר
                # במקרה הזה, דוגמה להדמיה:
                # נניח שקיבלנו פקודה חדשה - דחוף אותה לתור:
                # cmd = ... (קוד ללכידת קלט)
                # self.user_input_queue.put(cmd)

                # פשוט נחכה קצת כדי למנוע צריכת CPU גבוהה
                time.sleep(0.1)

        self._stop_user_input_thread = False
        self._user_input_thread = threading.Thread(target=user_input_loop, daemon=True)
        self._user_input_thread.start()

    # ─── main public entrypoint ──────────────────────────────────────────────
    def run(self):
        """Main game loop."""
        self.start_user_input_thread()

        start_ms = self.game_time_ms()
        for p in self.pieces.values():
            p.reset(start_ms)

        while not self._is_win():
            now = self.game_time_ms()

            # (1) update physics & animations
            for p in self.pieces.values():
                p.update(now)

            # (2) handle queued Commands from mouse thread
            while not self.user_input_queue.empty():
                cmd: Command = self.user_input_queue.get()
                self._process_input(cmd)

            # (3) draw current position
            self._draw()

            # (4) show frame and handle window events
            if not self._show():
                break

            # (5) detect captures
            self._resolve_collisions()

        self._announce_win()
        cv2.destroyAllWindows()
        self._stop_user_input_thread = True
        if self._user_input_thread is not None:
            self._user_input_thread.join(timeout=1)

    # ─── drawing helpers ────────────────────────────────────────────────────
    def _process_input(self, cmd: Command):
        if cmd.piece_id in self.pieces:
            self.pieces[cmd.piece_id].on_command(cmd)
        else:
            print(f"Warning: command for unknown piece_id '{cmd.piece_id}' ignored")

    def _draw(self):
        """Draw the current game state."""
        # יוצרים עותק של הלוח לציור
        frame = self.clone_board().img

        # מציירים את כל הכלים על הלוח
        for p in self.pieces.values():
            p.draw(frame)

        # שומרים את התמונה הנוכחית כפריים להצגה
        self._current_frame = frame

    def _show(self) -> bool:
        """Show the current frame and handle window events."""
        if not hasattr(self, '_current_frame'):
            return True
        cv2.imshow("Game", self._current_frame.get_cv_image())  # מניח ש-Img מאפשרת המרה ל-cv image

        key = cv2.waitKey(1) & 0xFF
        if key == 27:  # Escape key to exit
            return False
        return True

    # ─── capture resolution ────────────────────────────────────────────────
    def _resolve_collisions(self):
        """Resolve piece collisions and captures."""
        # לדוגמה פשוטה: אם שני כלים באותה תא - מסירים את הכלי השני
        positions = {}
        to_remove = set()
        for pid, piece in self.pieces.items():
            pos = piece.get_position()
            if pos in positions:
                # מסמנים את הכלי הנוכחי להסרה (לפי הלוגיקה הרצויה)
                to_remove.add(pid)
            else:
                positions[pos] = pid

        for pid in to_remove:
            print(f"Piece {pid} captured!")
            del self.pieces[pid]

    # ─── board validation & win detection ───────────────────────────────────
    def _is_win(self) -> bool:
        """Check if the game has ended."""
        # לדוגמה: משחק נגמר אם נשאר כלי אחד בלבד
        return len(self.pieces) <= 1

    def _announce_win(self):
        """Announce the winner."""
        if len(self.pieces) == 1:
            winner = next(iter(self.pieces.values()))
            print(f"Game Over! Winner is piece '{winner.piece_id}'.")
        else:
            print("Game Over! No winner.")
