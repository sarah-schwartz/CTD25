from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional



class Command:
    def __init__(self,
                 piece_id: str,
                 type: str,
                 params: Dict,
                 timestamp_ms: Optional[int] = None):
        self.piece_id = piece_id
        self.type = type
        self.params = params
        self.timestamp_ms = timestamp_ms

    def __repr__(self):
        return f"Command(piece_id={self.piece_id}, type={self.type}, params={self.params}, timestamp_ms={self.timestamp_ms})"
