import sys
import pathlib
import tempfile
import pytest

# מוסיף את תקיית CTD25 לנתיב
sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))

from It1_interfaces.Moves import Moves  # עדכון כאן!

@pytest.fixture
def tmp_rules_file():
    with tempfile.NamedTemporaryFile("w+", delete=False, suffix=".txt") as f:
        f.write("# knight-like movement\n")
        f.write("2,1\n")
        f.write("1,2\n")
        f.write("-1,-2\n")
        f.write("-2,-1\n")
        path = pathlib.Path(f.name)
    yield path
    path.unlink()

def test_moves_within_board(tmp_rules_file):
    moves = Moves(tmp_rules_file, dims=(8, 8))
    results = moves.get_moves(3, 3)
    expected = [(5, 4), (4, 5), (2, 1), (1, 2)]
    assert set(results) == set(expected)

def test_moves_near_edge(tmp_rules_file):
    moves = Moves(tmp_rules_file, dims=(8, 8))
    results = moves.get_moves(0, 0)
    expected = [(1, 2), (2, 1)]
    assert set(results) == set(expected)

def test_invalid_rule_file():
    with tempfile.NamedTemporaryFile("w+", delete=False, suffix=".txt") as f:
        f.write("bad_line\n")
        path = pathlib.Path(f.name)
    with pytest.raises(ValueError):
        Moves(path, dims=(8, 8))
    path.unlink()