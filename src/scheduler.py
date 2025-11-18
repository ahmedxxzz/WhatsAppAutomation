from datetime import datetime
import calendar

class Scheduler:
    def __init__(self):
        self.allowed_days = [] # e.g., ['Mon', 'Tue']
        self.start_time = "09:00"
        self.end_time = "17:00"

    def update_config(self, days, start, end):
        self.allowed_days = days
        self.start_time = start
        self.end_time = end

    def is_allowed(self):
        now = datetime.now()
        
        # 1. Check Day
        current_day_name = calendar.day_name[now.weekday()][:3] # Mon, Tue...
        if current_day_name not in self.allowed_days:
            return False, f"Day {current_day_name} not allowed"

        # 2. Check Time
        current_time_str = now.strftime("%H:%M")
        if self.start_time <= current_time_str <= self.end_time:
            return True, "Active"
        
        return False, f"Outside hours ({self.start_time}-{self.end_time})"