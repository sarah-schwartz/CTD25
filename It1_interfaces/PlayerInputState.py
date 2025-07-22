# file: player_input_state.py

from typing import Optional, List

class PlayerInputState:
    def __init__(self, is_player_one: bool):
        """
        מנהל את כל המידע הקשור למצב הקלט של שחקן.
        :param is_player_one: האם זהו שחקן מספר 1 (True) או 2 (False).
        """
        self.cursor: List[int] = [0, 0]
        self.selected_piece_id: Optional[str] = None
        self.has_selected_piece: bool = False
        self.is_player_one: bool = is_player_one
        
        # שדה לשמירת המיקום ההתחלתי של הכלי שנבחר
        self.selection_start_pos: Optional[List[int]] = None

    def reset_selection(self):
        """
        מאפס את מצב הבחירה של השחקן.
        """
        self.has_selected_piece = False
        self.selected_piece_id = None
        self.selection_start_pos = None