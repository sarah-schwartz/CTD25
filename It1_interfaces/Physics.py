from abc import ABC, abstractmethod
from Command import Command
import time

class Physics(ABC):
    """מחלקת בסיס לפיזיקה"""
    
    def __init__(self, initial_pos: tuple, board, speed_m_s: float = 1.0):
        self.initial_pos = initial_pos
        self.current_pos = initial_pos
        self.board = board
        self.speed = speed_m_s
        self.finished = False
        self.command = None
        self.start_time_ms = None
        self.next_state_when_finished = "idle"
    
    @abstractmethod
    def reset(self, command: Command):
        """איפוס הפיזיקה עם פקודה חדשה"""
        pass
    
    @abstractmethod
    def update(self, now_ms: int):
        """עדכון הפיזיקה"""
        pass
    
    def get_pos(self) -> tuple:
        """החזרת המיקום הנוכחי"""
        return self.current_pos
    
    def set_pos(self, pos: tuple):
        """הגדרת מיקום חדש"""
        self.current_pos = pos
    
    def is_finished(self) -> bool:
        """בדיקה האם הפיזיקה סיימה"""
        return self.finished
    
    def get_command(self) -> Command:
        """החזרת פקודה למעבר מצב אם הפיזיקה סיימה"""
        if self.finished and self.next_state_when_finished:
            return Command("auto", self.next_state_when_finished, {}, timestamp_ms=time.time_ns() // 1000000)
        return None
    
    def copy(self) -> 'Physics':
        """יצירת עותק של הפיזיקה"""
        new_physics = self.__class__(self.initial_pos, self.board, self.speed)
        new_physics.current_pos = self.current_pos
        new_physics.finished = self.finished
        new_physics.next_state_when_finished = self.next_state_when_finished
        return new_physics
    
    def can_be_captured(self) -> bool:
        """האם הpiece יכול להיתפס במצב זה"""
        return True
    
    def can_capture(self) -> bool:
        """האם הpiece יכול לתפוס במצב זה"""
        return False

class IdlePhysics(Physics):
    """פיזיקה למצב idle - לא זז"""
    
    def reset(self, command: Command):
        self.command = command
        self.finished = False
        self.start_time_ms = None
    
    def update(self, now_ms: int):
        # במצב idle הpiece לא זז ולא עושה כלום
        # הוא מוכן לקבל פקודות חדשות
        pass
    
    def can_be_captured(self) -> bool:
        return True
    
    def can_capture(self) -> bool:
        return False

class MovePhysics(Physics):
    """פיזיקה למצב move - תנועה בין משבצות"""
    
    def __init__(self, initial_pos: tuple, board, speed_m_s: float = 1.0):
        super().__init__(initial_pos, board, speed_m_s)
        self.target_pos = None
        self.next_state_when_finished = "long_rest"
    
    def reset(self, command: Command):
        self.command = command
        self.finished = False
        self.start_time_ms = None
        # נניח שהפקודה מכילה את המיקום היעד
        if "target" in command.params:
            self.target_pos = command.params["target"]
        else:
            self.target_pos = self.current_pos
    
    def update(self, now_ms: int):
        if self.start_time_ms is None:
            self.start_time_ms = now_ms
            return
        
        if self.target_pos is None or self.current_pos == self.target_pos:
            self.finished = True
            return
        
        # חישוב המרחק והזמן הנדרש
        elapsed_time_s = (now_ms - self.start_time_ms) / 1000.0
        
        # תנועה פשוטה - נניח שזה תמיד לוקח שנייה אחת לעבור משבצת
        if elapsed_time_s >= 1.0:
            self.current_pos = self.target_pos
            self.finished = True
    
    def can_be_captured(self) -> bool:
        return False
    
    def can_capture(self) -> bool:
        return True

class JumpPhysics(Physics):
    """פיזיקה למצב jump - קפיצה באותה משבצת"""
    
    def __init__(self, initial_pos: tuple, board, speed_m_s: float = 1.0):
        super().__init__(initial_pos, board, speed_m_s)
        self.next_state_when_finished = "short_rest"
    
    def reset(self, command: Command):
        self.command = command
        self.finished = False
        self.start_time_ms = None
    
    def update(self, now_ms: int):
        if self.start_time_ms is None:
            self.start_time_ms = now_ms
            return
        
        # קפיצה לוקחת חצי שנייה
        elapsed_time_s = (now_ms - self.start_time_ms) / 1000.0
        if elapsed_time_s >= 0.5:
            self.finished = True
    
    def can_be_captured(self) -> bool:
        return False
    
    def can_capture(self) -> bool:
        return True

class ShortRestPhysics(Physics):
    """פיזיקה למצב short_rest - מנוחה קצרה אחרי קפיצה"""
    
    def __init__(self, initial_pos: tuple, board, speed_m_s: float = 1.0):
        super().__init__(initial_pos, board, speed_m_s)
        self.rest_duration_s = 1.0  # שנייה אחת של מנוחה
        self.next_state_when_finished = "idle"
    
    def reset(self, command: Command):
        self.command = command
        self.finished = False
        self.start_time_ms = None
    
    def update(self, now_ms: int):
        if self.start_time_ms is None:
            self.start_time_ms = now_ms
            return
        
        elapsed_time_s = (now_ms - self.start_time_ms) / 1000.0
        if elapsed_time_s >= self.rest_duration_s:
            self.finished = True
    
    def can_be_captured(self) -> bool:
        return True
    
    def can_capture(self) -> bool:
        return False

class LongRestPhysics(Physics):
    """פיזיקה למצב long_rest - מנוחה ארוכה אחרי תנועה"""
    
    def __init__(self, initial_pos: tuple, board, speed_m_s: float = 1.0):
        super().__init__(initial_pos, board, speed_m_s)
        self.rest_duration_s = 2.0  # שתי שניות של מנוחה
        self.next_state_when_finished = "idle"
    
    def reset(self, command: Command):
        self.command = command
        self.finished = False
        self.start_time_ms = None
    
    def update(self, now_ms: int):
        if self.start_time_ms is None:
            self.start_time_ms = now_ms
            return
        
        elapsed_time_s = (now_ms - self.start_time_ms) / 1000.0
        if elapsed_time_s >= self.rest_duration_s:
            self.finished = True
    
    def can_be_captured(self) -> bool:
        return True
    
    def can_capture(self) -> bool:
        return False