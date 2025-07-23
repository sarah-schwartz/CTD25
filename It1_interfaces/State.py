from typing import Dict, Optional
from Command import Command
from Graphics import Graphics
from Physics import Physics
import pathlib
from PhysicsFactory import PhysicsFactory
from GraphicsFactory import GraphicsFactory
from Moves import Moves
import json

class State:
    def __init__(self, name: str, graphics: Graphics, physics: Physics, next_state_name: Optional[str]):
        self.name = name
        self._graphics = graphics
        self._physics = physics
        self.transitions: Dict[str, "State"] = {}
        self.next_state_when_finished = next_state_name

    def reset(self, cmd: Optional[Command]):
        self._graphics.reset()
        self._physics.reset(cmd)

    def update(self, now_ms: int):
        self._graphics.update(now_ms)
        self._physics.update(now_ms)

    def is_finished(self) -> bool:
        return self._physics.is_finished() and self._graphics.is_finished()

    def set_transition(self, event: str, target: "State"):
        self.transitions[event] = target

    def copy(self):
        new_state = State(self.name, self._graphics.copy(), self._physics.copy(), self.next_state_when_finished)
        return new_state


class StateManager:
    def __init__(self, states: Dict[str, State], initial_state_name: str):
        self.states = states
        if initial_state_name not in states:
            raise ValueError(f"Initial state '{initial_state_name}' not found.")
        self.current_state = states[initial_state_name]
        self.current_state.reset(None)

    def copy(self):
        new_states = {name: state.copy() for name, state in self.states.items()}
        for name, state in self.states.items():
            for event, target_state in state.transitions.items():
                new_states[name].set_transition(event, new_states[target_state.name])
        return StateManager(new_states, self.current_state.name)
        
    def update(self, now_ms: int):
        self.current_state.update(now_ms)

        if self.current_state.is_finished():
            next_state_name = self.current_state.next_state_when_finished
            if next_state_name and next_state_name in self.states:
                self.current_state = self.states[next_state_name]
                self.current_state.reset(None)

    def process_command(self, cmd: Command):
        next_state = self.current_state.transitions.get(cmd.type)
        if next_state:
            self.current_state = next_state
            self.current_state.reset(cmd)

    @staticmethod
    def from_config(piece_folder: pathlib.Path,
                    board,
                    physics_factory: PhysicsFactory,
                    graphics_factory: GraphicsFactory) -> "StateManager":

        states: Dict[str, State] = {}
        all_configs = {}

        states_folder = piece_folder / "states"
        for state_path in states_folder.iterdir():
            if not state_path.is_dir():
                continue
            
            state_name = state_path.name
            cfg_path = state_path / "config.json"
            if cfg_path.exists():
                with open(cfg_path, 'r', encoding='utf-8') as f:
                    cfg = json.load(f)
                    all_configs[state_name] = cfg

                    gfx = graphics_factory.create(
                        state_path / "sprites",
                        cfg.get("graphics", {})
                    )
                    phys = physics_factory.create(
                        cfg.get("physics", {})
                    )
                    
                    next_state = cfg.get("physics", {}).get("next_state_when_finished")
                    states[state_name] = State(state_name, gfx, phys, next_state)

        for state_name, cfg in all_configs.items():
            transitions = cfg.get("transitions", {})
            for event, target_state_name in transitions.items():
                if state_name in states and target_state_name in states:
                    states[state_name].set_transition(event, states[target_state_name])

        return StateManager(states, initial_state_name="idle")