import sys
import os
import pytest
from unittest.mock import MagicMock, patch

# מוסיף את תקיית It1_interfaces לנתיב החיפוש
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../It1_interfaces')))
from Game import Game
from Command import Command
from Piece import Piece
from Board import Board
from img import Img

@pytest.fixture
def mock_piece():
    p = MagicMock(spec=Piece)
    p.piece_id = "p1"
    p.reset = MagicMock()
    p.update = MagicMock()
    p.on_command = MagicMock()
    p.draw = MagicMock()
    p.get_position = MagicMock(return_value=(0, 0))
    return p

@pytest.fixture
def mock_board():
    b = MagicMock(spec=Board)
    b.clone = MagicMock(return_value=b)  # מחזיר את עצמו כ'עותק'
    b.img = MagicMock(spec=Img)
    b.img.get_cv_image = MagicMock(return_value="cv_image")
    return b

def test_game_init_and_clone_board(mock_piece, mock_board):
    game = Game(pieces=[mock_piece], board=mock_board)
    cloned_board = game.clone_board()
    mock_board.clone.assert_called_once()
    assert cloned_board == mock_board  # כי ב-Mock clone מחזיר את עצמו

def test_game_run_basic_flow(monkeypatch, mock_piece, mock_board):
    game = Game(pieces=[mock_piece], board=mock_board)
    
    # מחליפים את המתודות שדורשות אינטראקציה עם ממשק משתמש ו-OpenCV
    monkeypatch.setattr(game, "start_user_input_thread", lambda: None)
    monkeypatch.setattr(game, "_show", lambda: False)  # נפסיק אחרי הצגת פריים ראשון
    monkeypatch.setattr(game, "_is_win", lambda: True)  # נניח שהמשחק כבר נגמר
    monkeypatch.setattr(game, "_draw", lambda: None)
    monkeypatch.setattr(game, "_resolve_collisions", lambda: None)
    monkeypatch.setattr(game, "_announce_win", lambda: None)
    
    game.user_input_queue = MagicMock()
    game.user_input_queue.empty = MagicMock(return_value=True)
    
    # מפעילים את הלולאה - אמורה לעצור מיד כי _is_win מחזיר True
    game.run()
    
    # מוודאים שפונקציות ה-reset נקראו עם זמן התחלה
    mock_piece.reset.assert_called_once()
    mock_piece.update.assert_not_called()  # כי הלולאה הפסיקה מיד

def test_process_input_calls_piece_on_command(mock_piece, mock_board):
    game = Game(pieces=[mock_piece], board=mock_board)
    cmd = MagicMock(spec=Command)
    cmd.piece_id = mock_piece.piece_id
    
    game._process_input(cmd)
    
    mock_piece.on_command.assert_called_once_with(cmd)

def test_process_input_with_unknown_piece(mock_board, capsys):
    game = Game(pieces=[], board=mock_board)  # אין כלים במשחק
    cmd = MagicMock(spec=Command)
    cmd.piece_id = "unknown"
    
    game._process_input(cmd)
    
    captured = capsys.readouterr()
    assert "Warning: command for unknown piece_id 'unknown' ignored" in captured.out

def test_resolve_collisions_removes_pieces(monkeypatch, mock_board):
    # יצירת mock pieces עם get_position מוגדר בבירור
    piece1 = MagicMock()
    piece1.piece_id = "p1"
    piece1.get_position = MagicMock(return_value=(0, 0))
    
    piece2 = MagicMock()
    piece2.piece_id = "p2"
    piece2.get_position = MagicMock(return_value=(0, 0))  # אותם מיקום -> תפיסה
    
    game = Game(pieces=[piece1, piece2], board=mock_board)
    
    # להריץ את פונקציית הפתרון קונפליקטים
    game._resolve_collisions()
    
    # מצפה שכלי אחד יוסר - לפי הלוגיקה בקוד הוא מסיר את השני
    assert "p2" not in game.pieces
    assert "p1" in game.pieces

def test_is_win_and_announce_win(monkeypatch, mock_board):
    piece = MagicMock()
    piece.piece_id = "winner"
    game = Game(pieces=[piece], board=mock_board)
    
    # כשכלי אחד נשאר - משחק נגמר
    assert game._is_win() is True
    
    # לכסות את ההדפסה של המנצח
    monkeypatch.setattr('builtins.print', lambda *a, **k: None)
    game._announce_win()
    
    # כשהכלים 0 - המשחק נגמר אבל ללא מנצח
    game = Game(pieces=[], board=mock_board)
    assert game._is_win() is True
    monkeypatch.setattr('builtins.print', lambda *a, **k: None)
    game._announce_win()