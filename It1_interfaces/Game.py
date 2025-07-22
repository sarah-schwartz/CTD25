import queue
import time
import cv2
from typing import List, Dict
from Board import Board
from Piece import Piece
from img import Img
from Command import Command
from PlayerInputState import PlayerInputState
from pynput import keyboard
from pynput.keyboard import Key, KeyCode

class Game:
    def __init__(self, pieces: List[Piece], board: Board):
        self.pieces: Dict[str, Piece] = {}
        for idx, p in enumerate(pieces):
            self.pieces[f"{p.piece_id}_{idx}"] = p
        self.board = board
        self.user_input_queue = queue.Queue()
        self._user_input_thread = None
        self.player1 = PlayerInputState(is_player_one=True)
        self.player2 = PlayerInputState(is_player_one=False)
        # התחלת סמן: [col, row]
        self.player1.cursor = [4, 6]
        self.player2.cursor = [4, 1]

    def game_time_ms(self) -> int:
        return int(time.time() * 1000)

    def clone_board(self) -> Board:
        return self.board.clone()

    def start_user_input_thread(self):
        def on_press(key):
            self.user_input_queue.put(key)
        listener = keyboard.Listener(on_press=on_press)
        listener.start()
        self._user_input_thread = listener

    def run(self):
        self.start_user_input_thread()

        while True:
            board_clone = self.clone_board()
            frame = board_clone.img.copy()
            cell_W_pix = board_clone.cell_W_pix
            cell_H_pix = board_clone.cell_H_pix

            # ציור כל החיילים
            for p in self.pieces.values():
                p.draw_on_board(frame, cell_W_pix, cell_H_pix)

            # סמן עכבר
            self._draw_cursor(frame, self.player1, color=(0, 255, 0))
            self._draw_cursor(frame, self.player2, color=(0, 0, 255))

            cv2.imshow("Game", frame.img)

            key = None
            try:
                key = self.user_input_queue.get_nowait()
            except queue.Empty:
                pass

            if key is not None:
                if key == keyboard.Key.esc:
                    break
                self._handle_input(key)

            if cv2.waitKey(1) & 0xFF == 27:
                break

            time.sleep(0.016)

        if self._user_input_thread is not None:
            self._user_input_thread.stop()
        cv2.destroyAllWindows()

    def _process_input(self, cmd: Command):
        piece = self.pieces.get(cmd.piece_id)
        if piece:
            print(f"Moving piece '{cmd.piece_id}' from {piece.cell} to {cmd.params.get('target')}")
            piece.on_command(cmd, self.game_time_ms())
        else:
            print(f"Piece '{cmd.piece_id}' not found!")

    def _handle_input(self, key):
        # שחקן 1 (ירוק) - חיצים (cursor = [col, row])
        if key == Key.left:
            self.player1.cursor[0] = max(0, self.player1.cursor[0] - 1)
        elif key == Key.up:
            self.player1.cursor[1] = max(0, self.player1.cursor[1] - 1)
        elif key == Key.right:
            self.player1.cursor[0] = min(self.board.H_cells - 1, self.player1.cursor[0] + 1)
        elif key == Key.down:
            self.player1.cursor[1] = min(self.board.W_cells - 1, self.player1.cursor[1] + 1)
        elif key == Key.enter:
            piece = self.get_piece_at(self.player1.cursor[1], self.player1.cursor[0])  # הפוך סדר ל-(row, col)
            if piece:
                print(f"Player 1 pressed ENTER at cursor {self.player1.cursor} - Found piece '{piece.piece_id}'")
            else:
                print(f"Player 1 pressed ENTER at cursor {self.player1.cursor} - No piece found")
            self._handle_select_or_move(self.player1)

        # שחקן 2 (אדום) - WASD
        elif isinstance(key, KeyCode):
            char = key.char
            if char is None:
                return
            char = char.lower()
            if char == 'a' or char == 'ש':
                self.player2.cursor[0] = max(0, self.player2.cursor[0] - 1)
            elif char == 'w' or char == 'ו':
                self.player2.cursor[1] = max(0, self.player2.cursor[1] - 1)
            elif char == 'd' or char == 'ג':
                self.player2.cursor[0] = min(self.board.H_cells - 1, self.player2.cursor[0] + 1)
            elif char == 's' or char == 'ד':
                self.player2.cursor[1] = min(self.board.W_cells - 1, self.player2.cursor[1] + 1)

        elif key == Key.space:
            piece = self.get_piece_at(self.player2.cursor[1], self.player2.cursor[0])  # הפוך סדר ל-(row, col)
            if piece:
                print(f"Player 2 pressed SPACE at cursor {self.player2.cursor} - Found piece '{piece.piece_id}'")
            else:
                print(f"Player 2 pressed SPACE at cursor {self.player2.cursor} - No piece found")
            self._handle_select_or_move(self.player2)

    def _handle_select_or_move(self, player: PlayerInputState):
        row, col = player.cursor[1], player.cursor[0]  # הפוך סדר
        piece = self.get_piece_at(row, col)
        if not player.has_selected_piece:
            if piece and (piece.belongs_to_player_one() == player.is_player_one):
                player.selected_piece_id = piece.piece_id
                player.has_selected_piece = True
                # עדכן בחייל עצמו שהוא מסומן
                piece.selected = True
                print(f"Player {'1' if player.is_player_one else '2'} selected piece '{piece.piece_id}' at {(row, col)}")
        else:
            selected_piece = self.pieces.get(player.selected_piece_id)
            if selected_piece:
                print(f"Player {'1' if player.is_player_one else '2'} moving piece '{selected_piece.piece_id}' from {selected_piece.cell} to {(row, col)}")
                # לפני ההזזה נסיר סימון מהחייל הישן
                selected_piece.selected = False
            else:
                print(f"Selected piece id '{player.selected_piece_id}' not found!")
            cmd = Command(
                piece_id=player.selected_piece_id,
                type="move",
                params={"target": [row, col]},
                timestamp_ms=self.game_time_ms()
            )
            self._process_input(cmd)
            player.reset_selection()

    def _draw_selected_piece(self, frame: Img, player: PlayerInputState, cell_W_pix: int, cell_H_pix: int, color=(0, 255, 0)):
        # בפועל, הסימון מתבצע בתוך Piece (selected=True)
        # אפשר להסיר או להשאיר פה רק לציור מסגרת נוספת
        pass

    def _draw_cursor(self, frame: Img, player: PlayerInputState, color=(0, 255, 0)):
        x = player.cursor[0] * self.board.cell_W_pix
        y = player.cursor[1] * self.board.cell_H_pix
        cv2.rectangle(frame.img, (x, y), (x + self.board.cell_W_pix, y + self.board.cell_H_pix), color, 2)

    def get_piece_at(self, row: int, col: int) -> Piece | None:
        for p in self.pieces.values():
            if p.cell == (row, col):
                return p
        return None

    # פונקציות ריקות שלא שונו
    def _draw(self): pass
    def _show(self) -> bool: pass
    def _resolve_collisions(self): pass
    def _is_win(self) -> bool: pass
    def _announce_win(self): pass