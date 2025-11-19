import threading
import time
from node_client import NodeClient

class AutomationWorker(threading.Thread):
    def __init__(self, queue, templates, scheduler, config, callbacks):
        super().__init__()
        self.queue = queue 
        self.templates = templates 
        self.scheduler = scheduler
        self.config = config 
        self.callbacks = callbacks 
        
        self.running = True
        self.paused = False
        self.client = NodeClient()
        self.csv_manager = None
        
    def run(self):
        total = len(self.queue)
        current = 0
        
        self.log(f"Worker started. Queue size: {total}")

        while self.running and current < total:
            if self.paused:
                self.log("Paused...")
                time.sleep(1)
                continue

            # 1. Check Schedule (Uses new Multi-Session Logic)
            allowed, reason = self.scheduler.is_allowed()
            if not allowed:
                # To avoid spamming logs, we can check if the last log was a wait message
                # For simplicity here, we just wait longer
                self.log(f"Waiting: {reason}")
                time.sleep(30) # Check every 30s
                continue

            # 2. Process Item
            item = self.queue[current]
            phone = item['phone']
            u_type = item.get('username_type', 'group').lower()
            
            tmpl = self.templates.get(u_type, self.templates.get('group', ''))
            
            from utils import format_message
            message = format_message(tmpl, item)

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

            # 5. Rate Limit Sleep
            wait_time = 60.0 / float(self.config.get('rate_limit', 5))
            time.sleep(wait_time)

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