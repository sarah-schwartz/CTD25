import unittest
from unittest.mock import MagicMock
from StateManager import StateManager
from State import State
from Command import Command

class TestStateManager(unittest.TestCase):
    def setUp(self):
        # יצירת מצב מדומה עם reset, update וכו'
        self.mock_state = MagicMock(spec=State)
        self.mock_state.is_finished.return_value = False
        self.mock_state.name = 'idle'
        self.states = {
            'idle': self.mock_state,
            'move': MagicMock(spec=State),
            'jump': MagicMock(spec=State),
            'long_rest': MagicMock(spec=State),
            'short_rest': MagicMock(spec=State)
        }

        for name, s in self.states.items():
            s.name = name
            s.is_finished.return_value = False
            s.reset.return_value = None
            s.update.return_value = None

        self.sm = StateManager(self.states)

    def test_initial_state_is_idle(self):
        self.assertEqual(self.sm.current_state_name, 'idle')
        self.assertEqual(self.sm.current_state.name, 'idle')

    def test_handle_valid_command_transitions_to_correct_state(self):
        cmd = Command('move')
        self.sm.process_command(cmd)
        self.assertEqual(self.sm.state, 'move')  # עובר למצב move

    def test_invalid_command_does_not_change_state(self):
        cmd = Command('attack')  # לא קיים במצבים המותרים
        current = self.sm.current_state_name
        self.sm.process_command(cmd)
        self.assertEqual(self.sm.current_state_name, current)

    def test_automatic_transition(self):
        self.sm.current_state_name = 'move'
        self.sm.current_state = self.states['move']
        self.states['move'].is_finished.return_value = True
        self.sm.update(now_ms=12345)
        self.assertEqual(self.sm.current_state_name, 'long_rest')

    def test_copy_returns_new_instance(self):
        sm_copy = self.sm.copy()
        self.assertIsNot(sm_copy, self.sm)
        self.assertIsInstance(sm_copy, StateManager)
        self.assertEqual(sm_copy.current_state_name, self.sm.current_state_name)

    def test_reset_called_on_transition(self):
        cmd = Command('jump')
        self.sm.process_command(cmd)
        self.states['jump'].reset.assert_called()

if __name__ == '__main__':
    unittest.main()
