import os
import subprocess
import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext
import threading
import queue
from src.orchestrator.scanner_orchestrator import ScannerOrchestrator
from src.gui.editor_window import EditorWindow
from src.orchestrator import model_generator
from src.run.generate_csv import write_csv_all

class ScannerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Microservices Security Scanner")
        self.geometry("800x600")
        self.project_path = tk.StringVar()
        self.log_queue = queue.Queue()
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        top_frame = ttk.Frame(main_frame)
        top_frame.pack(fill=tk.X, pady=5)
        ttk.Label(top_frame, text="Project Path:").pack(side=tk.LEFT, padx=(0, 5))
        self.path_entry = ttk.Entry(top_frame, textvariable=self.project_path, width=70)
        self.path_entry.pack(side=tk.LEFT, expand=True, fill=tk.X)
        self.browse_button = ttk.Button(top_frame, text="Browse...", command=self.browse_directory)
        self.browse_button.pack(side=tk.LEFT, padx=(5, 0))
        self.scan_button = ttk.Button(main_frame, text="Start Scan", command=self.start_scan)
        self.scan_button.pack(pady=10, fill=tk.X)
        self.progress_bar = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress_bar.pack(pady=5, fill=tk.X)
        self.log_area = scrolledtext.ScrolledText(main_frame, wrap=tk.WORD, height=25)
        self.log_area.pack(expand=True, fill=tk.BOTH)
        self.log_area.configure(state='disabled')
        self.after(100, self.process_queue)

    def browse_directory(self):
        path = filedialog.askdirectory(title="Select a Microservices Project Folder")
        if path:
            self.project_path.set(path)

    def log(self, message):
        self.log_queue.put(message)

    def process_queue(self):
        try:
            while True:
                message = self.log_queue.get_nowait()
                self.log_area.configure(state='normal')
                self.log_area.insert(tk.END, message + '\n')
                self.log_area.configure(state='disabled')
                self.log_area.see(tk.END)
        except queue.Empty:
            pass
        self.after(100, self.process_queue)

    def start_scan(self):
        path = self.project_path.get()
        if not path:
            self.log("ERROR: Please select a project path first.")
            return
        self.scan_button.config(state="disabled")
        self.browse_button.config(state="disabled")
        self.progress_bar.start()
        self.analysis_thread = threading.Thread(
            target=self.run_analysis_thread,
            args=(path,)
        )
        self.analysis_thread.start()

    def run_analysis_thread(self, path):
        try:
            orchestrator = ScannerOrchestrator(project_path=path, log_callback=self.log)
            orchestrator.run_scan()
        except Exception as e:
            self.log(f"FATAL ERROR: An error occurred during the scan: {e}")
        finally:
            self.after(0, self.scan_finished)

    def scan_finished(self):
        self.progress_bar.stop()
        self.log("✅ Scan and Link Analysis complete. Opening editor window...")
        json_output_path = "output/discovered_components.json"
        editor = EditorWindow(self, json_output_path)
        self.wait_window(editor)
        self.log("\nEditor closed. Starting final model generation and prediction...")
        self.progress_bar.start()
        prediction_thread = threading.Thread(target=self.run_prediction_thread)
        prediction_thread.start()

    def run_prediction_thread(self):
        try:
            json_output_path = "output/discovered_components.json"
            python_model_path = "output/discovered_model.py"
            model_generator.generate_python_model(
                json_path=json_output_path,
                output_path=python_model_path,
                project_path=self.project_path.get(),
                log_callback=self.log
            )
            self.log(f"--- STAGE 4: Scanning the Model and Running Predictions ---")
            write_csv_all()
            rscript_executable = r"C:\Program Files\R\R-4.5.1\bin\Rscript.exe"
            project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
            prediction_dir = os.path.join(project_root, "src", "prediction")
            r_scripts = [
                "api_gateways_bffs_for_traffic_control_lrm_and_prediction_analysis.r",
                "authorization_on_client_service_paths_lrm_and_prediction_analysis.r",
                "backend_authorization_lrm_and_prediction_analysis.r",
                "sensitive_data_lrm_and_prediction_analysis.r"
            ]
            for script_name in r_scripts:
                try:
                    result = subprocess.run(
                        [rscript_executable, "--vanilla", script_name],
                        capture_output=True, text=True, check=True, encoding='utf-8',
                        cwd=prediction_dir
                    )
                    self.log(result.stdout)
                except Exception as e:
                    self.log(f"ERROR processing {script_name}: {e}")
        finally:
            self.after(0, self.prediction_finished)

    def prediction_finished(self):
        self.log("\n🚀 All steps are complete!")
        self.progress_bar.stop()
        self.scan_button.config(state="normal")
        self.browse_button.config(state="normal")