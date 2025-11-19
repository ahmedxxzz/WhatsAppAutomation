import pandas as pd
import os
import csv

class CSVManager:
    def __init__(self, worked_file="worked.csv", failed_file="failed.csv"):
        self.worked_file = worked_file
        self.failed_file = failed_file
        self._init_file(self.worked_file)
        self._init_file(self.failed_file)

    def _init_file(self, filepath):
        if not os.path.exists(filepath):
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['name', 'phone', 'username_type', 'timestamp'])

    def load_and_filter(self, input_csv_path):
        if not os.path.exists(input_csv_path):
            raise FileNotFoundError("Input CSV not found")

        try:
            df_input = pd.read_csv(input_csv_path, dtype=str)
            df_input.columns = [c.lower().strip() for c in df_input.columns]
        except Exception as e:
            raise Exception(f"Error reading input CSV: {e}")

        worked_phones = set()
        if os.path.exists(self.worked_file):
            try:
                df_worked = pd.read_csv(self.worked_file, dtype=str)
                if 'phone' in df_worked.columns:
                    worked_phones = set(df_worked['phone'].unique())
            except Exception:
                pass 

        queue = []
        skipped_count = 0
        
        for _, row in df_input.iterrows():
            phone = str(row.get('phone', '')).strip()
            if phone in worked_phones:
                skipped_count += 1
                continue
            
            queue.append({
                'name': row.get('name', ''),
                'phone': phone,
                'username_type': row.get('username_type', 'group')
            })

        return queue, skipped_count

    def log_worked(self, data):
        with open(self.worked_file, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                data.get('name'), 
                data.get('phone'), 
                data.get('username_type'), 
                pd.Timestamp.now()
            ])

    def log_failed(self, data, reason):
        with open(self.failed_file, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                data.get('name'), 
                data.get('phone'), 
                data.get('username_type'), 
                reason,
                pd.Timestamp.now()
            ])