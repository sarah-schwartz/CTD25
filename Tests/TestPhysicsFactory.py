import sys
import os
import pytest
from unittest.mock import MagicMock

# הוסף את הנתיב לתיקיית המודולים - זה מה שחסר!
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'It1_interfaces')))

# עכשיו נסה לייבא
from PhysicsFactory import PhysicsFactory
from Physics import Physics, IdlePhysics, MovePhysics
from Board import Board
from Command import Command

class DummyCommand:
    def __init__(self, type_):
        self.type = type_

def test_physics_factory_creates_idle():
    mock_board = MagicMock(spec=Board)
    factory = PhysicsFactory(mock_board)
    cfg = {"speed_m_s": 2.5}
   
    physics = factory.create((0, 0), DummyCommand("idle"), cfg)
   
    assert isinstance(physics, IdlePhysics)
    assert physics.get_pos() == (0, 0)
    assert physics.speed == 2.5
    assert physics.board is mock_board
    assert physics.cell == (0, 0)

def test_physics_factory_creates_move():
    mock_board = MagicMock(spec=Board)
    factory = PhysicsFactory(mock_board)
    cfg = {"speed_m_s": 1.0}
   
    physics = factory.create((0, 0), DummyCommand("move"), cfg)
   
    assert isinstance(physics, MovePhysics)
    assert physics.get_pos() == (0, 0)
    assert physics.speed == 1.0
    assert physics.board is mock_board
    assert physics.cell == (0, 0)

def test_physics_factory_default_speed():
    """בדיקה שמהירות ברירת המחדל עובדת"""
    mock_board = MagicMock(spec=Board)
    factory = PhysicsFactory(mock_board)
    cfg = {}  # ללא speed_m_s
   
    physics = factory.create((0, 0), DummyCommand("idle"), cfg)
   
    assert physics.speed == 1.0  # ברירת המחדל

def test_physics_capabilities():
    """בדיקת יכולות התפיסה"""
    mock_board = MagicMock(spec=Board)
    factory = PhysicsFactory(mock_board)
    
    idle_physics = factory.create((0, 0), DummyCommand("idle"), {})
    move_physics = factory.create((0, 0), DummyCommand("move"), {})
    
    # IdlePhysics
    assert idle_physics.can_be_captured() == True
    assert idle_physics.can_capture() == False
    
    # MovePhysics
    assert move_physics.can_be_captured() == False
    assert move_physics.can_capture() == True