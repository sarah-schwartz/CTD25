from Physics import Physics, IdlePhysics, MovePhysics, JumpPhysics, ShortRestPhysics, LongRestPhysics
from Command import Command
from Board import Board

class PhysicsFactory:
    """מפעל ליצירת אובייקטי Physics לפי סוג המצב"""
    
    def __init__(self, board: Board):
        self.board = board
    
    def create(self, initial_pos: tuple, command: Command, config: dict) -> Physics:
        """יצירת אובייקט Physics לפי סוג הפקודה והגדרות"""
        
        speed_m_s = config.get("speed_m_per_sec", 1.0)
        physics_type = command.type
        
        # יצירת הפיזיקה המתאימה לפי סוג המצב
        if physics_type == "idle":
            physics = IdlePhysics(initial_pos, self.board, speed_m_s)
        elif physics_type == "move":
            physics = MovePhysics(initial_pos, self.board, speed_m_s)
        elif physics_type == "jump":
            physics = JumpPhysics(initial_pos, self.board, speed_m_s)
        elif physics_type == "short_rest":
            physics = ShortRestPhysics(initial_pos, self.board, speed_m_s)
        elif physics_type == "long_rest":
            physics = LongRestPhysics(initial_pos, self.board, speed_m_s)
        else:
            # ברירת מחדל - idle physics
            physics = IdlePhysics(initial_pos, self.board, speed_m_s)
        
        # הגדרת המצב הבא מתוך ההגדרות
        if "next_state_when_finished" in config:
            physics.next_state_when_finished = config["next_state_when_finished"]
        
        return physics