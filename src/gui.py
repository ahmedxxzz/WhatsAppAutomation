import customtkinter as ctk
import json
import os
from tkinter import filedialog, messagebox

from scheduler import Scheduler
from csv_manager import CSVManager
from worker import AutomationWorker

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

DAYS_OF_WEEK = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("L-WAS v2.1: Fixed Delay Automation")
        self.geometry("1000x700")

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Data Structures
        self.scheduler = Scheduler()
        self.csv_manager = CSVManager()
        self.worker = None
        self.schedule_data = {day: [] for day in DAYS_OF_WEEK} 

        self._create_sidebar()
        self._create_tabs()
        self._load_state()

    def _create_sidebar(self):
        self.sidebar = ctk.CTkFrame(self, width=140, corner_radius=0)
        self.sidebar.grid(row=0, column=0, rowspan=4, sticky="nsew")
        self.sidebar.grid_rowconfigure(4, weight=1)

        ctk.CTkLabel(self.sidebar, text="L-WAS v2.1", font=ctk.CTkFont(size=20, weight="bold")).grid(row=0, column=0, padx=20, pady=(20, 10))
        
        self.btn_load_csv = ctk.CTkButton(self.sidebar, text="Load CSV", command=self.load_csv_dialog)
        self.btn_load_csv.grid(row=1, column=0, padx=20, pady=10)

        self.lbl_status = ctk.CTkLabel(self.sidebar, text="Status: IDLE", text_color="gray")
        self.lbl_status.grid(row=2, column=0, padx=20, pady=10)

    def _create_tabs(self):
        self.tabview = ctk.CTkTabview(self)
        self.tabview.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        
        self.tab_run = self.tabview.add("Run Dashboard")
        self.tab_config = self.tabview.add("Schedule Manager")
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
        # --- Global Settings (Updated for Delay) ---
        frame_global = ctk.CTkFrame(self.tab_config)
        frame_global.pack(pady=10, fill="x", padx=10)
        ctk.CTkLabel(frame_global, text="Global Settings", font=("Arial", 14, "bold")).pack(pady=5)
        
        f_g_in = ctk.CTkFrame(frame_global, fg_color="transparent")
        f_g_in.pack(pady=5)

        # NEW: Message Delay Range (Min-Max)
        ctk.CTkLabel(f_g_in, text="Delay Min (sec):").pack(side="left", padx=5)
        self.entry_delay_min = ctk.CTkEntry(f_g_in, width=60)
        self.entry_delay_min.pack(side="left", padx=5)
        self.entry_delay_min.insert(0, "3") # Default 3 seconds
        
        ctk.CTkLabel(f_g_in, text="Max (sec):").pack(side="left", padx=5)
        self.entry_delay_max = ctk.CTkEntry(f_g_in, width=60)
        self.entry_delay_max.pack(side="left", padx=5)
        self.entry_delay_max.insert(0, "7") # Default 7 seconds

        # Done Number
        ctk.CTkLabel(f_g_in, text="Done Number:").pack(side="left", padx=5)
        self.entry_done_num = ctk.CTkEntry(f_g_in, width=120)
        self.entry_done_num.pack(side="left", padx=5)

        # --- Schedule Creator (Multi-Session) ---
        frame_sched = ctk.CTkFrame(self.tab_config)
        frame_sched.pack(pady=10, fill="both", expand=True, padx=10)
        
        ctk.CTkLabel(frame_sched, text="Session Manager", font=("Arial", 14, "bold")).pack(pady=5)

        # Input Row
        frame_input = ctk.CTkFrame(frame_sched)
        frame_input.pack(pady=5)

        self.combo_day = ctk.CTkComboBox(frame_input, values=DAYS_OF_WEEK, width=80)
        self.combo_day.pack(side="left", padx=5)
        self.combo_day.set("Mon")

        self.entry_start = ctk.CTkEntry(frame_input, placeholder_text="09:00", width=70)
        self.entry_start.pack(side="left", padx=5)
        
        ctk.CTkLabel(frame_input, text="-").pack(side="left")

        self.entry_end = ctk.CTkEntry(frame_input, placeholder_text="12:00", width=70)
        self.entry_end.pack(side="left", padx=5)

        ctk.CTkButton(frame_input, text="Add Session", width=100, command=self.add_session_ui).pack(side="left", padx=10)

        # List of Sessions
        self.scroll_sessions = ctk.CTkScrollableFrame(frame_sched, label_text="Active Sessions")
        self.scroll_sessions.pack(pady=10, fill="both", expand=True, padx=10)

        # Save Button
        ctk.CTkButton(self.tab_config, text="Save All Settings", command=self._save_state, fg_color="green").pack(pady=10)

    def _setup_templates_tab(self):
        self.txt_template1 = self._create_template_area("Template 1")
        self.txt_template2 = self._create_template_area("Template 2")
        self.txt_template3 = self._create_template_area("Template 3")
        
        ctk.CTkLabel(self.tab_templates, text="Variables: {name} - Messages will rotate through templates").pack(pady=10)
        ctk.CTkButton(self.tab_templates, text="Save Templates", command=self._save_state).pack(pady=10)

    def _create_template_area(self, label):
        ctk.CTkLabel(self.tab_templates, text=label).pack(pady=2)
        box = ctk.CTkTextbox(self.tab_templates, height=80)
        box.pack(pady=5, fill="x", padx=20)
        return box

    # --- Logic ---

    def add_session_ui(self):
        day = self.combo_day.get()
        start = self.entry_start.get().strip()
        end = self.entry_end.get().strip()

        try:
            if len(start) != 5 or len(end) != 5 or ':' not in start or ':' not in end:
                raise ValueError
            if start >= end:
                messagebox.showerror("Error", "Start time must be before End time.")
                return
        except:
            messagebox.showerror("Error", "Invalid Format. Use HH:MM (e.g., 09:00)")
            return

        session = {'start': start, 'end': end}
        self.schedule_data[day].append(session)
        self.schedule_data[day].sort(key=lambda x: x['start'])
        self.refresh_session_list()

    def remove_session(self, day, index):
        del self.schedule_data[day][index]
        self.refresh_session_list()

    def refresh_session_list(self):
        for widget in self.scroll_sessions.winfo_children():
            widget.destroy()

        for day in DAYS_OF_WEEK:
            sessions = self.schedule_data.get(day, [])
            if sessions:
                lbl_day = ctk.CTkLabel(self.scroll_sessions, text=f"--- {day} ---", font=("Arial", 12, "bold"))
                lbl_day.pack(pady=(10, 2), anchor="w")
                
                for idx, s in enumerate(sessions):
                    row = ctk.CTkFrame(self.scroll_sessions, fg_color="transparent")
                    row.pack(fill="x", pady=2)
                    
                    txt = f"{s['start']} - {s['end']}"
                    ctk.CTkLabel(row, text=txt).pack(side="left", padx=10)
                    
                    btn_del = ctk.CTkButton(row, text="X", width=30, fg_color="red", 
                                            command=lambda d=day, i=idx: self.remove_session(d, i))
                    btn_del.pack(side="right", padx=10)

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
        
        try:
            queue, skipped = self.csv_manager.load_and_filter(self.csv_path)
            self.log(f"Processing {len(queue)} contacts. Skipped {skipped} (already worked).")
            if len(queue) == 0:
                self.log("No new contacts to process.")
                return
        except Exception as e:
            self.log(f"Error loading CSV: {e}")
            return

        self.scheduler.update_config(self.schedule_data)
        
        templates = [
            self.txt_template1.get("1.0", "end-1c"),
            self.txt_template2.get("1.0", "end-1c"),
            self.txt_template3.get("1.0", "end-1c")
        ]
        
        # Validate Delay Range
        try:
            delay_min = float(self.entry_delay_min.get())
            delay_max = float(self.entry_delay_max.get())
            if delay_min <= 0 or delay_max <= 0:
                raise ValueError("Delays must be positive")
            if delay_min > delay_max:
                raise ValueError("Min delay must be less than or equal to max delay")
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid delay range: {e}")
            return

        config = {
            'delay_min': delay_min,
            'delay_max': delay_max,
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
            'delay_min': self.entry_delay_min.get(),
            'delay_max': self.entry_delay_max.get(),
            'done_num': self.entry_done_num.get(),
            'tmpl_1': self.txt_template1.get("1.0", "end-1c"),
            'tmpl_2': self.txt_template2.get("1.0", "end-1c"),
            'tmpl_3': self.txt_template3.get("1.0", "end-1c"),
            'schedule': self.schedule_data
        }
        with open('state.json', 'w') as f:
            json.dump(state, f)

    def _load_state(self):
        if os.path.exists('state.json'):
            try:
                with open('state.json', 'r') as f:
                    state = json.load(f)
                    
                    # Load delay range (with backward compatibility)
                    delay_min = state.get('delay_min', '3')
                    delay_max = state.get('delay_max', '7')
                    self.entry_delay_min.delete(0, "end"); self.entry_delay_min.insert(0, delay_min)
                    self.entry_delay_max.delete(0, "end"); self.entry_delay_max.insert(0, delay_max)
                    
                    self.entry_done_num.delete(0, "end"); self.entry_done_num.insert(0, state.get('done_num', ''))
                    
                    self.txt_template1.delete("1.0", "end"); self.txt_template1.insert("1.0", state.get('tmpl_1', ''))
                    self.txt_template2.delete("1.0", "end"); self.txt_template2.insert("1.0", state.get('tmpl_2', ''))
                    self.txt_template3.delete("1.0", "end"); self.txt_template3.insert("1.0", state.get('tmpl_3', ''))

                    saved_sched = state.get('schedule', {})
                    for day in DAYS_OF_WEEK:
                        self.schedule_data[day] = saved_sched.get(day, [])
                    
                    self.refresh_session_list()
            except Exception as e:
                print(f"Error loading state: {e}")