import sys
import os

# מוסיף את תיקיית It1_interfaces לנתיב החיפוש
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'It1_interfaces')))

import pytest
from Command import Command

def test_command_basic_creation():
    cmd = Command("p1", "move", {"from": (0, 0), "to": (1, 1)}, timestamp_ms=1234)

    assert cmd.piece_id == "p1"
    assert cmd.type == "move"
    assert cmd.params == {"from": (0, 0), "to": (1, 1)}
    assert cmd.timestamp_ms == 1234


def test_command_without_timestamp():
    cmd = Command("k2", "idle", {})

    assert cmd.piece_id == "k2"
    assert cmd.type == "idle"
    assert cmd.params == {}
    assert cmd.timestamp_ms is None


def test_command_repr():
    cmd = Command("x7", "jump", {"over": (2, 2)}, timestamp_ms=999)
    expected = "Command(piece_id=x7, type=jump, params={'over': (2, 2)}, timestamp_ms=999)"
    assert repr(cmd) == expected