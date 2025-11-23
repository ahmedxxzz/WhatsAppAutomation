import threading
import time
import random
from node_client import NodeClient

class AutomationWorker(threading.Thread):
    def __init__(self, queue, templates, scheduler, config, callbacks):
        super().__init__()
        self.queue = queue 
        self.templates = templates  # Now a list of 3 templates
        self.scheduler = scheduler
        self.config = config 
        # config now expects: {'delay_min': float, 'delay_max': float, 'done_number': str}
        self.callbacks = callbacks 
        
        self.running = True
        self.paused = False
        self.client = NodeClient()
        self.csv_manager = None
        self.template_index = 0  # For rotating through templates
        
    def run(self):
        total = len(self.queue)
        current = 0
        
        self.log(f"Worker started. Queue size: {total}")

        while self.running and current < total:
            if self.paused:
                self.log("Paused...")
                time.sleep(1)
                continue

            # 1. Check Schedule
            allowed, reason = self.scheduler.is_allowed()
            if not allowed:
                self.log(f"Waiting: {reason}")
                time.sleep(30) 
                continue

            # 2. Process Item
            item = self.queue[current]
            phone = item['phone']
            
            # Rotate through templates
            template = self.templates[self.template_index % len(self.templates)]
            self.template_index += 1
            
            from utils import format_message
            message = format_message(template, item)

            self.log(f"Sending to {item['name']} ({phone})...")

            # 3. Send
            success, response = self.client.send_message(phone, message)

            if success:
                self.log(f"SUCCESS: {phone}")
                if self.csv_manager:
                    self.csv_manager.log_worked(item)
            else:
                self.log(f"FAILED: {phone} - {response}")
                if self.csv_manager:
                    self.csv_manager.log_failed(item, str(response))

            # 4. Update Progress
            current += 1
            self.callbacks['on_progress'](current / total)

            # 5. Random Delay (NEW LOGIC)
            try:
                delay_min = float(self.config.get('delay_min', 3))
                delay_max = float(self.config.get('delay_max', 7))
                if delay_min < 0: delay_min = 0
                if delay_max < delay_min: delay_max = delay_min
                delay = random.uniform(delay_min, delay_max)
            except (ValueError, TypeError):
                delay = random.uniform(3.0, 7.0)
            
            self.log(f"Waiting {delay:.2f} seconds before next message...")
            time.sleep(delay)

        self.log("Queue completed.")
        
        done_num = self.config.get('done_number')
        if done_num:
            self.client.send_message(done_num, "Automation Batch Completed Successfully.")

        self.callbacks['on_finish']()

    def log(self, msg):
        if self.callbacks['on_log']:
            self.callbacks['on_log'](msg)

    def stop(self):
        self.running = False