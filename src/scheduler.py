from datetime import datetime
import calendar

class Scheduler:
    def __init__(self):
        # Structure: {'Mon': [{'start': '09:00', 'end': '12:00'}, ...], 'Tue': ...}
        self.schedule_map = {} 

    def update_config(self, schedule_map):
        """
        Updates the internal schedule.
        schedule_map must be a dictionary where keys are Day names (3 letters)
        and values are lists of dicts: [{'start': 'HH:MM', 'end': 'HH:MM'}]
        """
        self.schedule_map = schedule_map

    def is_allowed(self):
        """
        Checks if current time is within ANY defined session for the current day.
        """
        now = datetime.now()
        current_day = calendar.day_name[now.weekday()][:3] # Mon, Tue...
        current_time_str = now.strftime("%H:%M")

        # 1. Check if day exists in schedule
        if current_day not in self.schedule_map:
            return False, f"No sessions configured for {current_day}"

        sessions = self.schedule_map[current_day]
        if not sessions:
            return False, f"No sessions configured for {current_day}"

        # 2. Iterate through all sessions for today
        for session in sessions:
            start = session.get('start')
            end = session.get('end')
            
            if start <= current_time_str <= end:
                return True, f"Active (Session: {start}-{end})"

        # 3. If loop finishes without returning True
        return False, f"Outside all sessions for {current_day} (Time: {current_time_str})"