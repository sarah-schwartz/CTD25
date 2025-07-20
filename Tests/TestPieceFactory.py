import sys
import os
import pathlib
import pytest
from unittest.mock import MagicMock, patch, mock_open
# הוסף את הנתיב לתיקיית המודולים (התאם לפי הסביבה שלך)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'It1_interfaces')))
from PieceFactory import PieceFactory
from Piece import Piece
from State import State

@patch('PieceFactory.GraphicsFactory')
@patch('PieceFactory.PhysicsFactory')  
@patch('PieceFactory.Moves')
@patch('PieceFactory.State')
@patch('builtins.open', new_callable=mock_open, read_data='{"initial_state": "idle", "states": {}}')
@patch('json.load')
def test_create_piece(mock_json_load, mock_file_open, mock_state_class, mock_moves_class, mock_physics_factory_class, mock_graphics_factory_class):
    # Mock את json.load כדי להחזיר JSON תקין
    mock_json_load.return_value = {
        "initial_state": "idle",
        "states": {
            "idle": {"physics": "idle", "graphics": "idle"}
        }
    }
    
    # יצירת mocks של המפעלים והמחלקות
    board_mock = MagicMock()
    pieces_root_mock = MagicMock(spec=pathlib.Path)
    
    # סימולציה של תיקיית pieces_root עם תיקיית "soldier"
    fake_piece_dir = MagicMock(spec=pathlib.Path)
    fake_piece_dir.is_dir.return_value = True
    fake_piece_dir.name = "soldier"
    fake_piece_dir.__truediv__ = MagicMock()  # עבור path operations
    fake_piece_dir.__truediv__.return_value = MagicMock()  # עבור config_path ו sprites_folder
    pieces_root_mock.iterdir.return_value = [fake_piece_dir]
    
    # הגדרות עבור המפעלים
    mock_graphics_factory_class.return_value.create.return_value = MagicMock()
    mock_physics_factory_class.return_value.create.return_value = MagicMock()
    mock_moves_class.return_value = MagicMock()
    
    # יצירת State mock שיחזור את עצמו
    mock_state_instance = MagicMock()  # הסר spec=State כדי לאפשר כל מתודה
    mock_state_instance.copy.return_value = mock_state_instance
    mock_state_instance.set_position = MagicMock()  # הוסף מתודות נדרשות
    mock_state_class.from_config.return_value = mock_state_instance
    
    # יצירת ה-factory - שיזין את תיקיית pieces_root עם ה-soldier
    factory = PieceFactory(board_mock, pieces_root_mock)
    
    # נקרא ל-create_piece עם סוג הקיים "soldier"
    piece = factory.create_piece("soldier", (1, 1))
    
    # בדיקות:
    # 1. שהפונקציה מחזירה אובייקט מסוג Piece
    assert isinstance(piece, Piece)
    
    # 2. שבוצעו קריאות לפונקציות יצירת ה-State
    mock_state_class.from_config.assert_called()
    
    # 3. בדיקה ש-key של "soldier" נמצא במילון ה-state_machine_templates
    assert "soldier" in factory.state_machine_templates