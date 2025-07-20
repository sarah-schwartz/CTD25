import sys
import os
import pathlib
import pytest
from unittest.mock import MagicMock, patch

# הוסף את הנתיב לתיקיית המודולים
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'It1_interfaces')))

# ייבוא המחלקות
from GraphicsFactory import GraphicsFactory
from Graphics import Graphics
from img import Img
from Board import Board

@patch("Graphics.Img")  # תיקון: עשה patch על Img במקום שבו הוא משתמש
def test_graphics_factory_create(mock_img_class):
    # יצירת mock board
    mock_board = MagicMock(spec=Board)
    factory = GraphicsFactory(board=mock_board)

    # יצירת mock directories
    fake_idle_dir = MagicMock(spec=pathlib.Path)
    fake_idle_dir.is_dir.return_value = True
    fake_idle_dir.name = "idle"
    fake_idle_dir.glob.return_value = [
        pathlib.Path('/fake/path/idle/1.png'),
        pathlib.Path('/fake/path/idle/2.png')
    ]

    fake_move_dir = MagicMock(spec=pathlib.Path)
    fake_move_dir.is_dir.return_value = True
    fake_move_dir.name = "move"
    fake_move_dir.glob.return_value = [
        pathlib.Path('/fake/path/move/1.png'),
        pathlib.Path('/fake/path/move/2.png')
    ]

    fake_folder = pathlib.Path('/fake/path')

    # הגדרת mock instance של Img
    mock_img_instance = MagicMock()
    mock_img_class.return_value = mock_img_instance

    with patch.object(pathlib.Path, 'iterdir', return_value=[fake_idle_dir, fake_move_dir]):
        cfg = {
            "frames_per_sec": 10,
            "is_loop": True
        }

        # יצירת Graphics באמצעות Factory
        graphics = factory.create(fake_folder, cfg)

        # בדיקות
        assert isinstance(graphics, Graphics)
        assert "idle" in graphics.frames_by_state
        assert "move" in graphics.frames_by_state
        
        # בדיקה שכל ה-frames הם instances של mock
        for frames in graphics.frames_by_state.values():
            assert all(frame is mock_img_instance for frame in frames)
        
        assert graphics.loop is True
        assert graphics.frame_time_ms == int(1000 / 10)

        # בדיקה שהקריאות ל-Img נעשו עם הנתיבים הנכונים
        expected_calls = [
            pathlib.Path('/fake/path/idle/1.png'),
            pathlib.Path('/fake/path/idle/2.png'),
            pathlib.Path('/fake/path/move/1.png'),
            pathlib.Path('/fake/path/move/2.png')
        ]
        
        # בדיקה שמספר הקריאות נכון
        assert mock_img_class.call_count == 4