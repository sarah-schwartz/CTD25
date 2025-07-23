import json
import pathlib
from typing import Dict, Optional
from Command import Command
from Graphics import Graphics
from Physics import Physics, IdlePhysics, MovePhysics, JumpPhysics, ShortRestPhysics, LongRestPhysics
from GraphicsFactory import GraphicsFactory
from PhysicsFactory import PhysicsFactory
from Moves import Moves

class State:
    def __init__(self, moves: Moves, graphics: Graphics, physics: Physics):
        self._moves = moves
        self._graphics = graphics
        self._physics = physics
        self._command = None
        self._transitions = {}
    
    def set_transition(self, command_type: str, next_state: 'State'):
        """הגדרת מעבר מצב"""
        self._transitions[command_type] = next_state
    
    def reset(self, command: Command = None):
        """איפוס המצב עם פקודה חדשה"""
        self._command = command
        if command:
            self._graphics.reset(command)
            self._physics.reset(command)
    
    def update(self, now_ms: int) -> 'State':
        """עדכון המצב - מחזיר את המצב הבא אם יש מעבר"""
        self._graphics.update(now_ms)
        self._physics.update(now_ms)
        
        # בדיקה אם Physics סיים והזמן הגיע לעבור למצב הבא
        next_command = self._physics.get_command()
        if next_command and next_command.type in self._transitions:
            next_state = self._transitions[next_command.type]
            next_state.reset(next_command)
            return next_state
        
        return self
    
    def process_command(self, command: Command) -> 'State':
        """עיבוד פקודה חדשה ומעבר למצב מתאים"""
        if command.type in self._transitions:
            next_state = self._transitions[command.type]
            next_state.reset(command)
            return next_state
        return self
    
    def is_command_possible(self, command: Command) -> bool:
        """בדיקה האם הפקודה אפשרית במצב הנוכחי"""
        return command.type in self._transitions
    
    def can_transition(self, now_ms: int) -> bool:
        """בדיקה האם ניתן לעבור למצב הבא"""
        return self._physics.is_finished()
    
    def get_command(self) -> Optional[Command]:
        """החזרת הפקודה הנוכחית"""
        return self._command
    
    def draw(self, board):
        """ציור המצב הנוכחי"""
        img = self._graphics.get_img()
        if img:
            pos = self._physics.get_pos()
            # המרה מקואורדינטות לוגיות לפיקסלים
            pixel_x = int(pos[0] * board.cell_W_pix)
            pixel_y = int(pos[1] * board.cell_H_pix)
            img.draw_on(board.img, pixel_x, pixel_y)
    
    def get_position(self) -> tuple:
        """החזרת המיקום הנוכחי"""
        return self._physics.get_pos()
    
    def set_position(self, pos: tuple):
        """הגדרת מיקום חדש"""
        self._physics.set_pos(pos)
    
    def copy(self) -> 'State':
        """יצירת עותק של המצב"""
        new_state = State(self._moves, self._graphics.copy(), self._physics.copy())
        new_state._transitions = self._transitions.copy()
        return new_state

class StateManager:
    """מנהל מצבים שיוצר ומנהל את מכונת המצבים לכל piece"""
    
    @staticmethod
    def from_config(piece_folder: pathlib.Path, moves: Moves, 
                   graphics_factory: GraphicsFactory, physics_factory: PhysicsFactory) -> State:
        """יצירת StateManager מקובץ הגדרות"""
        
        # קריאת הגדרות כלליות של הpiece
        config_path = piece_folder / "config.json"
        with open(config_path, 'r') as f:
            piece_config = json.load(f)
        
        initial_state_name = piece_config["initial_state"]
        states_config = piece_config["states"]
        
        # יצירת מילון המצבים
        states = {}
        
        # תיקיית המצבים - זה המבנה החדש שלך
        states_folder = piece_folder / "states"
        
        if not states_folder.exists():
            raise FileNotFoundError(f"States folder not found: {states_folder}")
        
        # עבור כל מצב ביצירת State אובייקט
        for state_name in states_config.keys():
            state_folder = states_folder / state_name
            
            if not state_folder.exists():
                print(f"Warning: State folder {state_folder} not found, skipping")
                continue
            
            # קריאת הגדרות המצב הספציפי
            state_config_path = state_folder / "config.json"
            if state_config_path.exists():
                with open(state_config_path, 'r') as f:
                    state_specific_config = json.load(f)
            else:
                # הגדרות ברירת מחדל אם אין קובץ config
                state_specific_config = {
                    "physics": {"speed_m_per_sec": 0.0, "next_state_when_finished": "idle"},
                    "graphics": {"frames_per_sec": 6, "is_loop": True}
                }
            
            # יצירת Graphics עבור המצב
            sprites_folder = state_folder / "sprites"
            graphics = graphics_factory.create(sprites_folder, state_specific_config["graphics"])
            
            # יצירת Physics עבור המצב
            physics_config = state_specific_config["physics"]
            # יצירת Command זמני עבור הפיזיקה
            temp_command = Command("temp", state_name, {}, timestamp_ms=0)
            physics = physics_factory.create((0, 0), temp_command, physics_config)
            
            # יצירת State
            state = State(moves, graphics, physics)
            states[state_name] = state
        
        # הגדרת מעברי המצבים
        for state_name, state_config in states_config.items():
            if state_name in states:
                current_state = states[state_name]
                
                # הוספת מעברי מצבים מההגדרות
                if "transitions" in state_config:
                    for command_type, next_state_name in state_config["transitions"].items():
                        if next_state_name in states:
                            current_state.set_transition(command_type, states[next_state_name])
                
                # הוספת מעבר אוטומטי מ-Physics
                state_folder = piece_folder / "states" / state_name
                state_config_path = state_folder / "config.json"
                if state_config_path.exists():
                    with open(state_config_path, 'r') as f:
                        state_specific_config = json.load(f)
                        next_state_when_finished = state_specific_config["physics"].get("next_state_when_finished")
                        if next_state_when_finished and next_state_when_finished in states:
                            # הוספת מעבר אוטומטי כאשר הפיזיקה מסיימת
                            current_state.set_transition("auto_finish", states[next_state_when_finished])
        
        # החזרת המצב ההתחלתי
        if initial_state_name not in states:
            raise ValueError(f"Initial state '{initial_state_name}' not found in states")
        
        return states[initial_state_name]