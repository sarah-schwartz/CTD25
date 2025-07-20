import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'It1_interfaces')))

from Physics import IdlePhysics, MovePhysics
from Board import Board
from Command import Command
from unittest.mock import MagicMock

def test_idle_physics_reset():
    board = MagicMock(spec=Board)
    physics = IdlePhysics((5, 5), board, speed_m_s=1.0)
    cmd = Command(1, "idle", {}, {})  # הוסף פרמטר נוסף
    physics.reset(cmd)
    assert physics.get_pos() == (5, 5)

def test_move_physics_updates_position():
    board = MagicMock(spec=Board)
    physics = MovePhysics((0, 0), board, speed_m_s=1.0)
    cmd = Command(1, "move", {}, {})  # שנה מ-"idle" ל-"move"
    physics.reset(cmd)  # השתמש במשתנה במקום ליצור חדש

    pos_before = physics.get_pos()
    physics.update(1000)
    pos_after = physics.get_pos()

    assert physics.finished is True