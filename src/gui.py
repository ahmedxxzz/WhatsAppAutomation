import customtkinter as ctk
import threading
import json
import os
from tkinter import filedialog

from scheduler import Scheduler
from csv_manager import CSVManager
from worker import AutomationWorker

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("L-WAS: WhatsApp Automation")
        self.geometry("900x600")

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- Components ---
        self.scheduler = Scheduler()
        self.csv_manager = CSVManager()
        self.worker = None

        self._create_sidebar()
        self._create_tabs()
        self._load_state()

    def _create_sidebar(self):
        self.sidebar = ctk.CTkFrame(self, width=140, corner_radius=0)
        self.sidebar.grid(row=0, column=0, rowspan=4, sticky="nsew")
        self.sidebar.grid_rowconfigure(4, weight=1)

        ctk.CTkLabel(self.sidebar, text="L-WAS", font=ctk.CTkFont(size=20, weight="bold")).grid(row=0, column=0, padx=20, pady=(20, 10))
        
        self.btn_load_csv = ctk.CTkButton(self.sidebar, text="Load CSV", command=self.load_csv_dialog)
        self.btn_load_csv.grid(row=1, column=0, padx=20, pady=10)

        self.lbl_status = ctk.CTkLabel(self.sidebar, text="Status: IDLE", text_color="gray")
        self.lbl_status.grid(row=2, column=0, padx=20, pady=10)

    def _create_tabs(self):
        self.tabview = ctk.CTkTabview(self)
        self.tabview.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        
        self.tab_run = self.tabview.add("Run Dashboard")
        self.tab_config = self.tabview.add("Configuration")
        self.tab_templates = self.tabview.add("Templates")

        self._setup_run_tab()
        self._setup_config_tab()
        self._setup_templates_tab()

    def _setup_run_tab(self):
        # Controls
        self.frame_controls = ctk.CTkFrame(self.tab_run)
        self.frame_controls.pack(pady=10, fill="x", padx=10)
        
        self.btn_start = ctk.CTkButton(self.frame_controls, text="START", fg_color="green", command=self.start_worker)
        self.btn_start.pack(side="left", padx=5)
        
        self.btn_pause = ctk.CTkButton(self.frame_controls, text="PAUSE", fg_color="orange", command=self.pause_worker, state="disabled")
        self.btn_pause.pack(side="left", padx=5)
        
        self.btn_stop = ctk.CTkButton(self.frame_controls, text="STOP", fg_color="red", command=self.stop_worker, state="disabled")
        self.btn_stop.pack(side="left", padx=5)

        # Info
        self.lbl_file_info = ctk.CTkLabel(self.tab_run, text="No CSV loaded")
        self.lbl_file_info.pack(pady=5)

        # Progress
        self.progress = ctk.CTkProgressBar(self.tab_run)
        self.progress.pack(pady=10, fill="x", padx=20)
        self.progress.set(0)

        # Logs
        self.log_box = ctk.CTkTextbox(self.tab_run, height=300)
        self.log_box.pack(pady=10, fill="both", expand=True, padx=10)

    def _setup_config_tab(self):
        # Schedule
        ctk.CTkLabel(self.tab_config, text="Working Days (Comma separated: Mon,Tue,Wed)").pack(pady=5)
        self.entry_days = ctk.CTkEntry(self.tab_config, width=300)
        self.entry_days.pack(pady=5)
        self.entry_days.insert(0, "Mon,Tue,Wed,Thu,Fri")

        ctk.CTkLabel(self.tab_config, text="Start Time (HH:MM)").pack(pady=5)
        self.entry_start = ctk.CTkEntry(self.tab_config)
        self.entry_start.pack(pady=5)
        self.entry_start.insert(0, "09:00")

        ctk.CTkLabel(self.tab_config, text="End Time (HH:MM)").pack(pady=5)
        self.entry_end = ctk.CTkEntry(self.tab_config)
        self.entry_end.pack(pady=5)
        self.entry_end.insert(0, "18:00")

        # Rate Limit
        ctk.CTkLabel(self.tab_config, text="Messages per Minute").pack(pady=5)
        self.entry_rate = ctk.CTkEntry(self.tab_config)
        self.entry_rate.pack(pady=5)
        self.entry_rate.insert(0, "5")
        
        # Done Number
        ctk.CTkLabel(self.tab_config, text="Completion Notification Number").pack(pady=5)
        self.entry_done_num = ctk.CTkEntry(self.tab_config)
        self.entry_done_num.pack(pady=5)

        ctk.CTkButton(self.tab_config, text="Save Settings", command=self._save_state).pack(pady=20)

    def _setup_templates_tab(self):
        self.txt_male = self._create_template_area("Male Template")
        self.txt_female = self._create_template_area("Female Template")
        self.txt_group = self._create_template_area("Group/Default Template")
        
        ctk.CTkLabel(self.tab_templates, text="Variables: {name}, {phone}, {username_type}").pack(pady=10)
        ctk.CTkButton(self.tab_templates, text="Save Templates", command=self._save_state).pack(pady=10)

    def _create_template_area(self, label):
        ctk.CTkLabel(self.tab_templates, text=label).pack(pady=2)
        box = ctk.CTkTextbox(self.tab_templates, height=80)
        box.pack(pady=5, fill="x", padx=20)
        return box

    # --- Logic ---

    def log(self, message):
        self.log_box.insert("end", f"{message}\n")
        self.log_box.see("end")

    def load_csv_dialog(self):
        path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if path:
            self.csv_path = path
            self.lbl_file_info.configure(text=f"Selected: {os.path.basename(path)}")
            self.log(f"CSV Loaded: {path}")

    def start_worker(self):
        if not hasattr(self, 'csv_path'):
            self.log("Error: No CSV loaded.")
            return

        self._save_state()
        
        # Filter CSV
        try:
            queue, skipped = self.csv_manager.load_and_filter(self.csv_path)
            self.log(f"Processing {len(queue)} contacts. Skipped {skipped} (already worked).")
            
            if len(queue) == 0:
                self.log("No new contacts to process.")
                return
        except Exception as e:
            self.log(f"Error loading CSV: {e}")
            return

        # Config
        days = [d.strip() for d in self.entry_days.get().split(',')]
        self.scheduler.update_config(days, self.entry_start.get(), self.entry_end.get())
        
        templates = {
            'male': self.txt_male.get("1.0", "end-1c"),
            'female': self.txt_female.get("1.0", "end-1c"),
            'group': self.txt_group.get("1.0", "end-1c")
        }
        
        config = {
            'rate_limit': int(self.entry_rate.get()),
            'done_number': self.entry_done_num.get()
        }

        callbacks = {
            'on_log': self.log,
            'on_progress': self.progress.set,
            'on_finish': self.on_worker_finish
        }

        self.worker = AutomationWorker(queue, templates, self.scheduler, config, callbacks)
        self.worker.csv_manager = self.csv_manager
        self.worker.start()
        
        self.btn_start.configure(state="disabled")
        self.btn_pause.configure(state="normal")
        self.btn_stop.configure(state="normal")
        self.lbl_status.configure(text="Status: RUNNING", text_color="green")

    def pause_worker(self):
        if self.worker:
            self.worker.paused = not self.worker.paused
            if self.worker.paused:
                self.btn_pause.configure(text="RESUME", fg_color="green")
                self.lbl_status.configure(text="Status: PAUSED", text_color="orange")
            else:
                self.btn_pause.configure(text="PAUSE", fg_color="orange")
                self.lbl_status.configure(text="Status: RUNNING", text_color="green")

    def stop_worker(self):
        if self.worker:
            self.worker.stop()
            self.worker = None
        self.on_worker_finish()
        self.log("Worker Stopped by user.")

    def on_worker_finish(self):
        self.btn_start.configure(state="normal")
        self.btn_pause.configure(state="disabled")
        self.btn_stop.configure(state="disabled")
        self.lbl_status.configure(text="Status: IDLE", text_color="gray")
        self.progress.set(0)

    def _save_state(self):
        state = {
            'days': self.entry_days.get(),
            'start': self.entry_start.get(),
            'end': self.entry_end.get(),
            'rate': self.entry_rate.get(),
            'done_num': self.entry_done_num.get(),
            'tmpl_m': self.txt_male.get("1.0", "end-1c"),
            'tmpl_f': self.txt_female.get("1.0", "end-1c"),
            'tmpl_g': self.txt_group.get("1.0", "end-1c"),
        }
        with open('state.json', 'w') as f:
            json.dump(state, f)

    def _load_state(self):
        if os.path.exists('state.json'):
            try:
                with open('state.json', 'r') as f:
                    state = json.load(f)
                    self.entry_days.delete(0, "end"); self.entry_days.insert(0, state.get('days', ''))
                    self.entry_start.delete(0, "end"); self.entry_start.insert(0, state.get('start', '09:00'))
                    self.entry_end.delete(0, "end"); self.entry_end.insert(0, state.get('end', '18:00'))
                    self.entry_rate.delete(0, "end"); self.entry_rate.insert(0, state.get('rate', '5'))
                    self.entry_done_num.delete(0, "end"); self.entry_done_num.insert(0, state.get('done_num', ''))
                    
                    self.txt_male.delete("1.0", "end"); self.txt_male.insert("1.0", state.get('tmpl_m', ''))
                    self.txt_female.delete("1.0", "end"); self.txt_female.insert("1.0", state.get('tmpl_f', ''))
                    self.txt_group.delete("1.0", "end"); self.txt_group.insert("1.0", state.get('tmpl_g', ''))
            except:
                pass