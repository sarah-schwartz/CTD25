from typing import Dict, Optional
from Command import Command
from Moves import Moves
from Graphics import Graphics
from Physics import Physics

class State:
    def __init__(self, moves: Moves, graphics: Graphics, physics: Physics):
        self._moves = moves
        self._graphics = graphics
        self._physics = physics
        self.transitions: Dict[str, "State"] = {}
        self._current_command: Optional[Command] = None

    def set_transition(self, event: str, target: "State"):
        """הגדרת מעבר בין מצבים ע"פ אירוע (סוג הפקודה)."""
        self.transitions[event] = target

    def reset(self, cmd: Command):
        """איפוס מצב לפי פקודה חדשה."""
        self._current_command = cmd
        self._graphics.reset(cmd)
        self._physics.reset(cmd)

    def update(self, now_ms: int) -> "State":
        """עדכון רכיבי הגרפיקה והפיזיקה, ובדיקה למעבר מצב אם יש פקודה חדשה."""
        self._graphics.update(now_ms)
        self._physics.update(now_ms)

        cmd = self._physics.get_command()
        if cmd is not None:
            return self.process_command(cmd)

        return self

    def process_command(self, cmd: Command) -> "State":
        """מעבד פקודה ומחזיר את המצב הבא אם קיים מעבר עבור הפקודה."""
        next_state = self.transitions.get(cmd.type)
        if next_state:
            next_state.reset(cmd)
            return next_state
        return self

    def can_transition(self, now_ms: int) -> bool:
        """בודק אם הפיזיקה סיימה ואפשר לעבור מצב."""
        return self._physics.is_finished()

    def get_command(self) -> Optional[Command]:
        """מחזיר את הפקודה הנוכחית."""
        return self._current_command