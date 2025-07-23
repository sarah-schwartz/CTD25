class PlayerInputState:
    def __init__(self, is_player_one: bool):
        self.cursor = [0, 0] 
        self.selected_piece_id = None
        self.has_selected_piece = False
        self.is_player_one = is_player_one

    def reset_selection(self):
        self.has_selected_piece = False
        self.selected_piece_id = None