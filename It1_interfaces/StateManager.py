from typing import Dict, Optional
from transitions import Machine
import json
import pathlib
import copy

from State import State
from Command import Command
from PhysicsFactory import PhysicsFactory
from GraphicsFactory import GraphicsFactory

class StateManager:
    """Manages state transitions for game pieces using transitions library."""
    
    # Define state transitions configuration
    STATE_TRANSITIONS = {
        'idle': {
            'allowed_commands': ['move', 'jump'],
            'transitions_to': {
                'move': 'move',
                'jump': 'jump'
            }
        },
        'move': {
            'allowed_commands': [],
            'auto_transition': 'long_rest'
        },
        'jump': {
            'allowed_commands': [],
            'auto_transition': 'short_rest'
        },
        'long_rest': {
            'allowed_commands': [],
            'auto_transition': 'idle'
        },
        'short_rest': {
            'allowed_commands': [],
            'auto_transition': 'idle'
        }
    }

    def __init__(self, states: Dict[str, State], initial_state_name: str = "idle"):
        """Initialize state manager with states dictionary and initial state."""
        self.states = states
        self.current_state_name = initial_state_name
        self.current_state = states[initial_state_name]

        # Configure state machine transitions
        transitions = []
        
        # Add command-based transitions
        for state_name, config in self.STATE_TRANSITIONS.items():
            for cmd in config.get('allowed_commands', []):
                if cmd in config['transitions_to']:
                    transitions.append({
                        'trigger': cmd,
                        'source': state_name,
                        'dest': config['transitions_to'][cmd],
                        'conditions': ['_is_valid_command'],
                        'before': '_handle_command_transition'
                    })

        # Add automatic transitions when states finish
        for state_name, config in self.STATE_TRANSITIONS.items():
            if 'auto_transition' in config:
                transitions.append({
                    'trigger': f'finish_{state_name}',
                    'source': state_name,
                    'dest': config['auto_transition'],
                    'before': '_on_state_change'
                })

        # Initialize state machine
        self.machine = Machine(
            model=self,
            states=list(states.keys()),
            transitions=transitions,
            initial=initial_state_name,
            after_state_change='_after_state_change',
            send_event=True 
        )
        self.current_state.reset(None)

    def _is_valid_command(self,event) -> bool:
        """Check if command is valid for current state."""
        cmd = event.kwargs.get('cmd')
        if self.current_state_name not in self.STATE_TRANSITIONS:
            return False
            
        allowed_commands = self.STATE_TRANSITIONS[self.current_state_name].get('allowed_commands', [])
        return cmd.type in allowed_commands

    # יש לשנות את החתימה והתוכן של הפונקציה
    def _handle_command_transition(self, event):
        """Handle state transition by resetting the destination state."""
        cmd = event.kwargs.get('cmd')
        if cmd is None:
            print("Warning: Transition triggered without a command.")
            return
        dest_state_name = event.transition.dest
        if dest_state_name in self.states:
            destination_state = self.states[dest_state_name]
            destination_state.reset(cmd)
        print(f"Transitioning state due to command: {cmd.type}")


    def _on_state_change(self):
        """Handle state initialization before transition."""
        self.current_state.reset(None)


    def _after_state_change(self, *args, **kwargs):
        """Update current state after transition."""
        self.current_state = self.states[self.current_state_name]

    def update(self, now_ms: int):
        """Update current state and check for automatic transitions."""
        self.current_state.update(now_ms)
        
        # Check for automatic transitions
        if (self.current_state.is_finished() and 
            self.current_state_name in self.STATE_TRANSITIONS and
            'auto_transition' in self.STATE_TRANSITIONS[self.current_state_name]):
            
            trigger = f'finish_{self.current_state_name}'
            if hasattr(self, trigger):
                getattr(self, trigger)()
    def copy(self):
        return copy.deepcopy(self)

    def process_command(self, cmd: Command):
        """Process incoming command."""
        self.trigger(cmd.type, cmd=cmd) 

    @staticmethod
    def from_config(piece_folder: pathlib.Path,
                   board,
                   physics_factory: PhysicsFactory,
                   graphics_factory: GraphicsFactory) -> "StateManager":
        """Create StateManager instance from configuration files."""
        states: Dict[str, State] = {}

        # Create states from config files
        states_folder = piece_folder / "states"
        for state_name in StateManager.STATE_TRANSITIONS.keys():
            state_path = states_folder / state_name
            if not state_path.is_dir():
                continue

            cfg_path = state_path / "config.json"
            if cfg_path.exists():
                with open(cfg_path, 'r', encoding='utf-8') as f:
                    cfg = json.load(f)

                    gfx = graphics_factory.create(
                        state_path / "sprites",
                        cfg.get("graphics", {})
                    )
                    phys = physics_factory.create(
                        cfg.get("physics", {})
                    )

                    # Get auto transition if exists
                    next_state = None
                    if 'auto_transition' in StateManager.STATE_TRANSITIONS.get(state_name, {}):
                        next_state = StateManager.STATE_TRANSITIONS[state_name]['auto_transition']

                    states[state_name] = State(state_name, gfx, phys, next_state)

        return StateManager(states)