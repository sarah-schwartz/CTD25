import unittest
import sys
import os
from unittest.mock import MagicMock, patch
from pathlib import Path

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'It1_interfaces')))

from Graphics import Graphics
from img import Img
from Command import Command
from Board import Board

class TestGraphics(unittest.TestCase):
    def setUp(self):
        self.mock_board = MagicMock(spec=Board)
        
        self.test_dir = Path("test_sprites")
        
        self.mock_frames = {
            "idle": [MagicMock(spec=Img), MagicMock(spec=Img)],
            "move": [MagicMock(spec=Img), MagicMock(spec=Img)]
        }

    @patch("Graphics.Img")  
    @patch("pathlib.Path.is_dir", return_value=True)
    def test_init_loads_frames(self, mock_is_dir, mock_img_class):
        mock_idle_dir = MagicMock(spec=Path)
        mock_idle_dir.name = "idle"
        mock_idle_dir.is_dir.return_value = True
        mock_idle_dir.glob.return_value = [Path("1.png"), Path("2.png")]
        
        mock_move_dir = MagicMock(spec=Path)
        mock_move_dir.name = "move"
        mock_move_dir.is_dir.return_value = True
        mock_move_dir.glob.return_value = [Path("1.png"), Path("2.png")]
        
        mock_img_instance = MagicMock(spec=Img)
        mock_img_class.return_value = mock_img_instance
        
        with patch.object(Path, 'iterdir', return_value=[mock_idle_dir, mock_move_dir]):
            g = Graphics(sprites_folder=self.test_dir, board=self.mock_board)
            
            self.assertIn("idle", g.frames_by_state)
            self.assertIn("move", g.frames_by_state)
            self.assertEqual(len(g.frames_by_state["idle"]), 2)
            self.assertEqual(len(g.frames_by_state["move"]), 2)
            self.assertEqual(g.current_state, "idle")
            self.assertEqual(g.current_frame, 0)

    def test_copy_creates_shallow_copy(self):
        g = Graphics.__new__(Graphics)
        g.frame_time_ms = 100
        g.loop = True
        g.board = self.mock_board
        g.frames_by_state = self.mock_frames
        g.current_state = "idle"
        g.current_frame = 1
        g.last_update_ms = 1234
        g.finished = False
        
        g_copy = g.copy()
        
        self.assertEqual(g_copy.frame_time_ms, g.frame_time_ms)
        self.assertEqual(g_copy.loop, g.loop)
        self.assertEqual(g_copy.board, g.board)
        self.assertIs(g_copy.frames_by_state, g.frames_by_state)  # shallow copy - אותו אובייקט
        self.assertEqual(g_copy.current_state, g.current_state)
        self.assertEqual(g_copy.current_frame, g.current_frame)
        self.assertEqual(g_copy.last_update_ms, g.last_update_ms)
        self.assertEqual(g_copy.finished, g.finished)

    def test_reset_sets_state_and_resets_frame(self):
        g = Graphics.__new__(Graphics)
        g.frames_by_state = self.mock_frames
        g.current_state = "move"
        g.current_frame = 3
        g.last_update_ms = 1000
        g.finished = True
        
        class Cmd:
            def __init__(self, type):
                self.type = type
        
        cmd = Cmd("idle")
        g.reset(cmd)
        
        self.assertEqual(g.current_state, "idle")
        self.assertEqual(g.current_frame, 0)
        self.assertIsNone(g.last_update_ms)
        self.assertFalse(g.finished)
        
        cmd2 = Cmd("jump")
        g.reset(cmd2)
        self.assertEqual(g.current_state, "idle")  

    def test_update_advances_frame_correctly(self):
        g = Graphics.__new__(Graphics)
        g.frame_time_ms = 100
        g.loop = True
        g.frames_by_state = self.mock_frames
        g.current_state = "idle"
        g.current_frame = 0
        g.last_update_ms = None
        g.finished = False
        
        g.update(1000)
        self.assertEqual(g.last_update_ms, 1000)
        self.assertEqual(g.current_frame, 0)
        
        g.update(1110)
        self.assertEqual(g.current_frame, 1)
        self.assertEqual(g.last_update_ms, 1100)
        
        g.update(1220)
        self.assertEqual(g.current_frame, 0)  
        self.assertEqual(g.last_update_ms, 1200)
        
        g.loop = False
        g.current_frame = 1
        g.last_update_ms = 1200
        g.finished = False
        g.update(1330)
        self.assertEqual(g.current_frame, 1)  
        self.assertTrue(g.finished)

    def test_get_img_returns_correct_frame(self):
        g = Graphics.__new__(Graphics)
        g.frames_by_state = self.mock_frames
        g.current_state = "idle"
        g.current_frame = 1
        
        img = g.get_img()
        self.assertEqual(img, self.mock_frames["idle"][1])

if __name__ == "__main__":
    unittest.main()