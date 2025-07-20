from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional
@dataclass
class Command:
    timestamp: int          # ms since game start
    piece_id: str
    type: str               # "Move" | "Jump" | …
    params: List            # payload (e.g. ["e2", "e4"])
from typing import Dict, Optional
class Command:
    def __init__(self,
                 piece_id: str,
                 type: str,
                 params: Dict,
                 timestamp_ms: Optional[int] = None):
        """
        מייצג פקודה במשחק:
        :param piece_id: מזהה הכלי (למשל "p1")
        :param type: סוג הפקודה (למשל "move", "idle")
        :param params: פרמטרים משלימים (כמו {"from": (0, 1), "to": (0, 2)})
        :param timestamp_ms: זמן הפקודה (מילישניות), אם יש
        """
        self.piece_id = piece_id
        self.type = type
        self.params = params
        self.timestamp_ms = timestamp_ms
    def __repr__(self):
        return f"Command(piece_id={self.piece_id}, type={self.type}, params={self.params}, timestamp_ms={self.timestamp_ms})"





