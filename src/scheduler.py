from datetime import datetime
import calendar

class Scheduler:
    def __init__(self):
        # Structure: {'Mon': [{'start': '09:00', 'end': '12:00'}, ...], 'Tue': ...}
        self.schedule_map = {} 

    def update_config(self, schedule_map):
        self.schedule_map = schedule_map

    def is_allowed(self):
        now = datetime.now()
        current_day = calendar.day_name[now.weekday()][:3] # Mon, Tue...
        current_time_str = now.strftime("%H:%M")

        if current_day not in self.schedule_map:
            return False, f"No sessions configured for {current_day}"

        sessions = self.schedule_map[current_day]
        if not sessions:
            return False, f"No sessions configured for {current_day}"

        for session in sessions:
            start = session.get('start')
            end = session.get('end')
            
            if start <= current_time_str <= end:
                return True, f"Active (Session: {start}-{end})"

        return False, f"Outside all sessions for {current_day} (Time: {current_time_str})"