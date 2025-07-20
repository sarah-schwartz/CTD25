import sys
import os
from unittest.mock import MagicMock

# הוסף את הנתיב לתיקיית המודולים
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'It1_interfaces')))

from Piece import Piece
from Command import Command
from State import State

def test_piece_on_command_updates_state():
    # Mock של מצב ש-Piece ישתמש בו
    mock_state = MagicMock()
    mock_state.is_command_possible.return_value = True
    mock_state.process_command.return_value = mock_state
    
    piece = Piece("soldier", mock_state)
    
    # תקן את יצירת Command לפורמט הנכון (piece_id, command_type, params, additional_params)
    cmd = Command("p1", "move", {}, {})
    
    piece.on_command(cmd, 1000)
    
    # בדיקות שהמתודות הנכונות נקראו
    mock_state.is_command_possible.assert_called_once_with(cmd)
    mock_state.process_command.assert_called_once_with(cmd)
    mock_state.update.assert_called_once_with(1000)

def test_piece_reset():
    mock_state = MagicMock()
    piece = Piece("soldier", mock_state)
    
    piece.reset(0)
    
    # בדיקה שהמתודות הנכונות נקראו
    mock_state.reset.assert_called_once()
    mock_state.update.assert_called_once_with(0)

def test_piece_update():
    mock_state = MagicMock()
    piece = Piece("soldier", mock_state)
    
    piece.update(2000)
    
    # בדיקה שהמתודה הנכונה נקראה
    mock_state.update.assert_called_once_with(2000)