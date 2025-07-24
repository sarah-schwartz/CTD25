
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'It1_interfaces')))

import pytest
from unittest.mock import Mock
from State import State
from Command import Command


@pytest.fixture
def mock_dependencies():
    mock_moves = Mock()
    mock_graphics = Mock()
    mock_physics = Mock()
    return mock_moves, mock_graphics, mock_physics


@pytest.fixture
def sample_command():
    cmd = Mock(spec=Command)
    cmd.type = "move"
    cmd.timestamp = 1234
    return cmd


def test_reset_sets_command_and_calls_components(mock_dependencies, sample_command):
    moves, gfx, phys = mock_dependencies
    state = State(moves, gfx, phys)

    state.reset(sample_command)

    assert state.get_command() == sample_command
    gfx.reset.assert_called_once_with(sample_command)
    phys.reset.assert_called_once_with(sample_command)


def test_set_transition_and_process_command_changes_state(mock_dependencies, sample_command):
    moves, gfx, phys = mock_dependencies
    state1 = State(moves, gfx, phys)
    state2 = State(moves, gfx, phys)

    state1.set_transition("move", state2)

    next_state = state1.process_command(sample_command)
    assert next_state is state2
    assert next_state.get_command() == sample_command
    next_state._graphics.reset.assert_called_with(sample_command)
    next_state._physics.reset.assert_called_with(sample_command)


def test_update_stays_in_same_state_if_no_command(mock_dependencies):
    moves, gfx, phys = mock_dependencies
    phys.get_command.return_value = None

    state = State(moves, gfx, phys)
    current = state.update(now_ms=1000)

    gfx.update.assert_called_once_with(1000)
    phys.update.assert_called_once_with(1000)
    assert current is state


def test_update_transitions_when_command_returned(mock_dependencies, sample_command):
    moves, gfx, phys = mock_dependencies
    phys.get_command.return_value = sample_command

    state1 = State(moves, gfx, phys)
    state2 = State(moves, gfx, phys)
    state1.set_transition("move", state2)

    next_state = state1.update(now_ms=3000)

    assert next_state is state2
    assert next_state.get_command() == sample_command
    next_state._graphics.reset.assert_called_with(sample_command)
    next_state._physics.reset.assert_called_with(sample_command)


def test_can_transition_true_if_physics_finished(mock_dependencies):
    moves, gfx, phys = mock_dependencies
    phys.is_finished.return_value = True
    state = State(moves, gfx, phys)

    assert state.can_transition(now_ms=1000) is True


def test_can_transition_false_if_not_finished(mock_dependencies):
    moves, gfx, phys = mock_dependencies
    phys.is_finished.return_value = False
    state = State(moves, gfx, phys)

    assert state.can_transition(now_ms=1000) is False