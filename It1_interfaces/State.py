from typing import Optional
from Command import Command
from Graphics import Graphics
from Physics import Physics

class State:
    def __init__(self, name: str, graphics: Graphics, physics: Physics, next_state_name: Optional[str]):
        self.name = name
        self._graphics = graphics
        self._physics = physics
        self.next_state_when_finished = next_state_name

    def reset(self, cmd: Optional[Command]):
        self._graphics.reset()
        if cmd is not None:
            self._physics.reset(cmd)

    def update(self, now_ms: int):
        self._graphics.update(now_ms)
        self._physics.update(now_ms)

    def is_finished(self) -> bool:
        return self._physics.is_finished() and self._graphics.is_finished()

    def copy(self):
        return State(self.name, self._graphics.copy(), self._physics.copy(), self.next_state_when_finished)