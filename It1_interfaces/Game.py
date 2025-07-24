import queue
import time
import cv2
from typing import List, Dict, Optional, Tuple
from Board import Board
from Piece import Piece
from img import Img
from Command import Command
from PlayerInputState import PlayerInputState
from pynput import keyboard
from pynput.keyboard import Key, KeyCode

class Game:
    """Main game class handling the chess game logic and visualization."""
    
    def __init__(self, pieces: List[Piece], board: Board):
        """Initialize game with pieces and board.
        
        Args:
            pieces: List of chess pieces
            board: Game board instance
        """
        self.pieces: Dict[str, Piece] = {p.piece_id: p for p in pieces}
        self.board = board
        self.user_input_queue = queue.Queue()
        self._user_input_thread = None
        self._init_players()

    def _init_players(self):
        """Initialize player states with default positions."""
        self.player1 = PlayerInputState(is_player_one=True)
        self.player2 = PlayerInputState(is_player_one=False)
        self.player1.cursor = [4, 6]
        self.player2.cursor = [4, 1]

    @property
    def game_time_ms(self) -> int:
        """Get current game time in milliseconds."""
        return int(time.time() * 1000)

    def start_user_input_thread(self):
        """Start keyboard input listener thread."""
        def on_press(key): 
            self.user_input_queue.put(key)
        self._user_input_thread = keyboard.Listener(on_press=on_press)
        self._user_input_thread.start()

    def run(self):
        """Main game loop."""
        self.start_user_input_thread()
        try:
            self._game_loop()
        finally:
            self._cleanup()

    def _game_loop(self):
        """Core game loop handling updates and rendering."""
        while True:
            frame = self._prepare_frame()
            self._update_pieces()
            self._render_frame(frame)

            if cv2.waitKey(1) & 0xFF == 27:
                break

            if self._handle_keyboard_input(): 
                break
                
            time.sleep(0.016)  # ~60 FPS
    def _prepare_frame(self) -> Img:
        """Prepare new frame for rendering."""
        board_clone = self.board.clone()
        return board_clone.img.copy()

    def _update_pieces(self):
        """Update all pieces states."""
        now = self.game_time_ms
        for piece in self.pieces.values():
            piece.update(now)

    def _render_frame(self, frame: Img):
        """Render current game state to frame."""
        self._draw_pieces(frame)
        self._draw_cursors(frame)
        cv2.imshow("Game", frame.img)

    def _draw_pieces(self, frame: Img):
        """Draw all pieces on frame."""
        for piece in self.pieces.values():
            piece.draw_on_board(frame)

    def _draw_cursors(self, frame: Img):
        """Draw player cursors on frame."""
        self._draw_cursor(frame, self.player1, color=(0, 255, 0))
        self._draw_cursor(frame, self.player2, color=(0, 0, 255))

    def _handle_keyboard_input(self) -> bool:
        """Handle keyboard input. Returns True if game should exit."""
        try:
            key = self.user_input_queue.get_nowait()
        except queue.Empty:
            return False

        if key is None:
            return False

        if self._is_exit_key(key):
            return True

        self._process_key(key)
        return False

    def _is_exit_key(self, key) -> bool:
        """Check if key is exit command."""
        return (key == keyboard.Key.esc or 
                (cv2.waitKey(1) & 0xFF == 27))
    def _process_key(self, key):
        """Process keyboard input for movement and actions."""
        if isinstance(key, Key):
            self._handle_special_key(key)
        elif isinstance(key, KeyCode) and key.char:
            self._handle_character_key(key.char.lower())

    def _handle_special_key(self, key: Key):
        """Handle special keys (arrows, enter, etc)."""
        if key == Key.left:
            self._move_cursor(self.player1, (-1, 0))
        elif key == Key.right:
            self._move_cursor(self.player1, (1, 0))
        elif key == Key.up:
            self._move_cursor(self.player1, (0, -1))
        elif key == Key.down:
            self._move_cursor(self.player1, (0, 1))
        elif key == Key.enter:
            self._handle_select_or_move(self.player1)
        elif key == Key.space:
            self._handle_select_or_move(self.player2)


    def _handle_character_key(self, char: str):
        """Handle character keys (WASD, space)."""
        if char == 'a':
            self._move_cursor(self.player2, (-1, 0))
        elif char == 'd':
            self._move_cursor(self.player2, (1, 0))
        elif char == 'w':
            self._move_cursor(self.player2, (0, -1))
        elif char == 's':
            self._move_cursor(self.player2, (0, 1))

    def _move_cursor(self, player: PlayerInputState, delta: Tuple[int, int]):
        """Move player cursor by delta while keeping in bounds."""
        dx, dy = delta
        new_x = player.cursor[0] + dx
        new_y = player.cursor[1] + dy
        
        player.cursor[0] = max(0, min(self.board.W_cells - 1, new_x))
        player.cursor[1] = max(0, min(self.board.H_cells - 1, new_y))

    def _handle_select_or_move(self, player: PlayerInputState):
        """Handle piece selection or movement based on cursor position."""
        cursor_pos = (player.cursor[1], player.cursor[0])  # (row, col)

        if not player.has_selected_piece:
            self._try_select_piece(player, cursor_pos)
        else:
            self._try_move_piece(player, cursor_pos)

    def _try_select_piece(self, player: PlayerInputState, cursor_pos: Tuple[int, int]):
        """Try to select piece at cursor position."""
        piece = self.get_piece_at(cursor_pos[0], cursor_pos[1])
        if piece and (piece.player_one == player.is_player_one):
            player.selected_piece_id = piece.piece_id
            player.has_selected_piece = True
            piece.selected = True
            print(f"Player {'1' if player.is_player_one else '2'} selected '{piece.piece_id}'")

    def _try_move_piece(self, player: PlayerInputState, cursor_pos: Tuple[int, int]):
        """Try to move selected piece to cursor position."""
        selected_piece = self.pieces.get(player.selected_piece_id)
        if not selected_piece:
            player.reset_selection()
            return

        if self._is_valid_move(selected_piece, cursor_pos):
            self._execute_move(selected_piece, cursor_pos)
        else:
            print(f"Invalid move for {player.selected_piece_id} to {cursor_pos}")

        selected_piece.selected = False
        player.reset_selection()

    def _is_valid_move(self, piece: Piece, target_pos: Tuple[int, int]) -> bool:
        """Check if move is valid according to game rules."""
        if self.get_piece_at(target_pos[0], target_pos[1]):
            return False
            
        return piece.moves.is_valid_move(
            start_cell=piece.cell,
            end_cell=target_pos
        )

    def _execute_move(self, piece: Piece, target_pos: Tuple[int, int]):
        """Execute piece movement command."""
        print(f"Commanding '{piece.piece_id}' to move to {target_pos}")
        cmd = Command(
            piece_id=piece.piece_id,
            type="move",
            params={"target": list(target_pos)},
            timestamp_ms=self.game_time_ms
        )
        piece.on_command(cmd)

    def _draw_cursor(self, frame: Img, player: PlayerInputState, color=(0, 255, 0)):
        """Draw player cursor on frame."""
        x = player.cursor[0] * self.board.cell_W_pix
        y = player.cursor[1] * self.board.cell_H_pix
        
        # Draw outer rectangle
        cv2.rectangle(frame.img, 
                     (x, y), 
                     (x + self.board.cell_W_pix, y + self.board.cell_H_pix),
                     color, 2)
        
        # Draw inner rectangle if piece is selected
        if player.has_selected_piece:
            cv2.rectangle(frame.img,
                         (x+3, y+3),
                         (x + self.board.cell_W_pix-3, y + self.board.cell_H_pix-3),
                         color, 2)

    def _cleanup(self):
        """Clean up resources before exit."""
        if self._user_input_thread is not None:
            self._user_input_thread.stop()
        cv2.destroyAllWindows()

    def get_piece_at(self, row: int, col: int) -> Optional[Piece]:
        """Get piece at specified board position."""
        for piece in self.pieces.values():
            if piece.cell == (row, col):
                return piece
        return None