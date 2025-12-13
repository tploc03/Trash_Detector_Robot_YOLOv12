from enum import Enum
import time

class RobotState(Enum):
    IDLE = "IDLE"                  
    SEARCH_STEP = "SEARCH_STEP"    
    SEARCH_WAIT = "SEARCH_WAIT"    
    VERIFYING = "VERIFYING"        
    ALIGNING = "ALIGNING"          
    CHASING = "CHASING"            
    REACHED = "REACHED"            

class RobotController:
    def __init__(self, base_speed=60, screen_width=640):
        self.state = RobotState.IDLE
        self.base_speed = base_speed
        self.screen_width = screen_width
        self.center_x = screen_width // 2
        
        #Scan
        self.SCAN_TURN_DURATION = 0.4  
        self.SCAN_WAIT_DURATION = 1.0  
        self.SCAN_SPEED = 90
        self.ALIGN_SPEED = 40
        self.SEARCH_DELAY = 0.5
        self.LOST_TARGET_TIMEOUT = 1.0
        #Xác thực
        self.CONFIRM_TIME = 2.0        
        
        #Di chuyển
        self.ALIGN_TOLERANCE = 40      
        self.TURN_SENSITIVITY = 0.2   
        self.STOP_DISTANCE = 10        
        

        self.target_x = None
        self.current_label = ""
        self.dist_front = 999
        
        self.confidence_threshold = 0.2

        self.state_timer = 0           
        self.first_seen_time = 0       
        self.last_seen_time = 0        
        self.search_enabled = False
        self.search_started_time = 0

    def update_sensors(self, front, left, right):
        self.dist_front = front if front > 0 else 999

    def update_detection(self, detections):
        """Cập nhật dữ liệu từ AI"""
        if not detections:
            return
        
        best = max(detections, key=lambda x: x['conf'])
        

        if best['conf'] < self.confidence_threshold:
            return

        self.target_x = best['center_x']
        self.current_label = best['label']
        self.last_seen_time = time.time()
        
        if abs(best['center_x'] - self.center_x) > self.ALIGN_TOLERANCE:
            print(f"Skip {self.current_label} outside tolerance (x={best['center_x']})")
            return
    
        if self.state in [RobotState.SEARCH_STEP, RobotState.SEARCH_WAIT, RobotState.IDLE]:
            print(f"Spotted {self.current_label} ({best['conf']:.2f}) at x={best['center_x']} -> Verifying")
            self.state = RobotState.VERIFYING
            self.first_seen_time = time.time()

    def enable_search(self, enabled):
        self.search_enabled = enabled
        if enabled:
            self.state = RobotState.SEARCH_WAIT
            self.search_started_time = time.time()
            self.state_timer = time.time()
        else:
            self.state = RobotState.IDLE

    def compute_control(self):
        now = time.time()
        
        # 1. Dừng nếu quá gần
        if self.dist_front < self.STOP_DISTANCE:
            self.state = RobotState.REACHED
            return 0, 0, f"REACHED: {self.current_label}"

        # 2. Xử lý mất dấu
        if self.state in [RobotState.VERIFYING, RobotState.ALIGNING, RobotState.CHASING]:
            if now - self.last_seen_time > self.LOST_TARGET_TIMEOUT:
                if self.search_enabled:
                    self.state = RobotState.SEARCH_WAIT 
                    self.state_timer = now
                else:
                    self.state = RobotState.IDLE
                return 0, 0, "Lost Target"

        # --- STATE MACHINE ---

        elif self.state == RobotState.SEARCH_WAIT:
            if now - self.state_timer > self.SEARCH_DELAY:
                self.state = RobotState.SEARCH_STEP
                self.state_timer = now
                return -self.SCAN_SPEED, self.SCAN_SPEED, "Step Turn"
            
            remaining = self.SEARCH_DELAY - (now - self.state_timer)
            return 0, 0, f"Searching ({remaining:.1f}s)..."

        if self.state == RobotState.SEARCH_STEP:
            if now - self.state_timer > self.SCAN_TURN_DURATION:
                self.state = RobotState.SEARCH_WAIT
                self.state_timer = now
                return 0, 0, "Scanning"
            
            # Quay trái (L-, R+)
            return -self.SCAN_SPEED, self.SCAN_SPEED, "Step Turn"

        elif self.state == RobotState.VERIFYING:
            duration = now - self.first_seen_time
            if duration >= self.CONFIRM_TIME:
                self.state = RobotState.ALIGNING
                return 0, 0, "CONFIRMED!"
            return 0, 0, f"Verifying ({duration:.1f}s)"

        elif self.state == RobotState.ALIGNING:
            error = self.target_x - self.center_x
            
            if abs(error) < self.ALIGN_TOLERANCE:
                self.state = RobotState.CHASING
                L = self.base_speed
                R = self.base_speed
                return int(L), int(R), "LOCKED"
            
            turn_speed = self.ALIGN_SPEED 
            if error > 0: 
                return turn_speed, -turn_speed, "Aligning Right"
            else: 
                return -turn_speed, turn_speed, "Aligning Left"

        elif self.state == RobotState.CHASING:
            error = self.target_x - self.center_x
            turn = int(error * self.TURN_SENSITIVITY)
            turn = max(-40, min(40, turn))
            
            L = self.base_speed + turn
            R = self.base_speed - turn
            
            return int(L), int(R), f"Dist: {self.dist_front}cm"

        return 0, 0, "IDLE"

    def reset_after_reach(self):
        self.state = RobotState.SEARCH_WAIT 
        self.state_timer = time.time()
        self.target_x = None

    def emergency_stop(self):
        self.state = RobotState.IDLE
        return 0, 0, "STOP"

    def get_state_color(self):
        if self.state == RobotState.VERIFYING: return "#FFA500" 
        if self.state == RobotState.ALIGNING: return "#FFFF00"  
        if self.state == RobotState.CHASING: return "#00FF00"   
        if self.state == RobotState.REACHED: return "#00FFFF"   
        return "#FFFFFF"