import queue
import time
import cv2
from typing import List, Dict, Optional 
from Board import Board
from Piece import Piece
from img import Img
from Command import Command
from PlayerInputState import PlayerInputState
from pynput import keyboard
from pynput.keyboard import Key, KeyCode

class Game:
    def __init__(self, pieces: List[Piece], board: Board):
        self.pieces: Dict[str, Piece] = {p.piece_id: p for p in pieces}
        self.board = board
        self.user_input_queue = queue.Queue()
        self._user_input_thread = None
        self.player1 = PlayerInputState(is_player_one=True)
        self.player2 = PlayerInputState(is_player_one=False)
        self.player1.cursor = [4, 6]
        self.player2.cursor = [4, 1]

    def game_time_ms(self) -> int:
        return int(time.time() * 1000)

    def start_user_input_thread(self):
        def on_press(key):
            self.user_input_queue.put(key)
        listener = keyboard.Listener(on_press=on_press)
        listener.start()
        self._user_input_thread = listener

    def run(self):
        self.start_user_input_thread()

        while True:
            board_clone = self.board.clone()
            frame = board_clone.img.copy()

            now_ms = self.game_time_ms()
            for p in self.pieces.values():
                p.update(now_ms)

            for p in self.pieces.values():
                p.draw_on_board(frame)

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

    def _handle_input(self, key):
        if key == Key.left: self.player1.cursor[0] = max(0, self.player1.cursor[0] - 1)
        elif key == Key.up: self.player1.cursor[1] = max(0, self.player1.cursor[1] - 1)
        elif key == Key.right: self.player1.cursor[0] = min(self.board.W_cells - 1, self.player1.cursor[0] + 1)
        elif key == Key.down: self.player1.cursor[1] = min(self.board.H_cells - 1, self.player1.cursor[1] + 1)
        elif isinstance(key, KeyCode):
            char = key.char.lower() if key.char else ''
            if char == 'a': self.player2.cursor[0] = max(0, self.player2.cursor[0] - 1)
            elif char == 'w': self.player2.cursor[1] = max(0, self.player2.cursor[1] - 1)
            elif char == 'd': self.player2.cursor[0] = min(self.board.W_cells - 1, self.player2.cursor[0] + 1)
            elif char == 's': self.player2.cursor[1] = min(self.board.H_cells - 1, self.player2.cursor[1] + 1)

        if key == Key.enter:
            self._handle_select_or_move(self.player1)
        elif key == Key.space:
            self._handle_select_or_move(self.player2)
            
    def _handle_select_or_move(self, player: PlayerInputState):
        cursor_pos = (player.cursor[1], player.cursor[0]) # (row, col)

        if not player.has_selected_piece:
            piece = self.get_piece_at(cursor_pos[0], cursor_pos[1])
            if piece and (piece.player_one == player.is_player_one):
                player.selected_piece_id = piece.piece_id
                player.has_selected_piece = True
                piece.selected = True
                print(f"Player {'1' if player.is_player_one else '2'} selected '{piece.piece_id}'")
        
        else:
            selected_piece = self.pieces.get(player.selected_piece_id)
            if not selected_piece:
                player.reset_selection()
                return
            is_valid = selected_piece.moves.is_valid_move(
                start_cell=selected_piece.cell,
                end_cell=cursor_pos
            )

            target_piece = self.get_piece_at(cursor_pos[0], cursor_pos[1])
            if target_piece is not None:
                is_valid = False 

            if is_valid:
                print(f"Commanding '{player.selected_piece_id}' to move to {cursor_pos}")
                cmd = Command(
                    piece_id=player.selected_piece_id,
                    type="move",
                    params={"target": list(cursor_pos)},
                    timestamp_ms=self.game_time_ms()
                )
                selected_piece.on_command(cmd)
            else:
                print(f"Invalid move for {player.selected_piece_id} to {cursor_pos}")
            selected_piece.selected = False
            player.reset_selection()

    def _draw_cursor(self, frame: Img, player: PlayerInputState, color=(0, 255, 0)):
        x = player.cursor[0] * self.board.cell_W_pix
        y = player.cursor[1] * self.board.cell_H_pix
        cv2.rectangle(frame.img, (x, y), (x + self.board.cell_W_pix, y + self.board.cell_H_pix), color, 2)
        if player.has_selected_piece:
             cv2.rectangle(frame.img, (x+3, y+3), (x + self.board.cell_W_pix-3, y + self.board.cell_H_pix-3), color, 2)


    def get_piece_at(self, row: int, col: int) -> Optional[Piece]:
        for p in self.pieces.values():
            if p.cell == (row, col):
                return p
        return None