import os
import subprocess
import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox
from tkinter import ttk
import threading

class PipelineGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Data Pipeline GUI")

        # Frame setup
        main_frame = tk.Frame(root)
        # main_frame.pack(padx=10, pady=10)
        self.root.minsize(800, 600)
        main_frame.pack(fill='both', expand=True)
        left_frame = tk.Frame(main_frame)
        left_frame.pack(side='left', fill='both', expand=True, padx=10, pady=10)
        right_frame = tk.Frame(main_frame)
        right_frame.pack(side='right', fill='both', expand=True, padx=10, pady=10)

        # Folder selectors for each step
        self.training_data_folder = self.add_folder_selector(left_frame, "Select Training Data Folder:", self.update_file_list)
        self.cleaned_data_folder = self.add_folder_selector(left_frame, "Select Cleaned Data Folder:", self.update_eda_file_list)
        self.model_training_folder = self.add_folder_selector(left_frame, "Select Model Training Folder:", self.update_model_training_file_list)
        self.model_output_folder = self.add_folder_selector(left_frame, "Select Model Output Folder:")
        self.eda_output_folder = self.add_folder_selector(left_frame, "Select EDA Output Folder:")

        # Dropdown for selecting file for cleaning from training data folder
        self.file_label = tk.Label(left_frame, text="Select File for Data Cleaning:")
        self.file_label.pack(anchor="w")
        self.file_dropdown = ttk.Combobox(left_frame, state="readonly")
        self.file_dropdown.pack(fill="x", pady=5)

        # Dropdown for selecting file for EDA
        self.eda_file_label = tk.Label(left_frame, text="Select File for EDA:")
        self.eda_file_label.pack(anchor="w")
        self.eda_file_dropdown = ttk.Combobox(left_frame, state="readonly")
        self.eda_file_dropdown.pack(fill="x", pady=5)

        # Dropdown for selecting file for model training
        self.model_file_label = tk.Label(left_frame, text="Select Cleaned File for Model Training:")
        self.model_file_label.pack(anchor="w")
        self.model_file_dropdown = ttk.Combobox(left_frame, state="readonly")
        self.model_file_dropdown.pack(fill="x", pady=5)

        # Dropdown for selecting file for prediction
        self.prediction_file_label = tk.Label(left_frame, text="Select File for Prediction:")
        self.prediction_file_label.pack(anchor="w")
        self.prediction_file_dropdown = ttk.Combobox(left_frame, state="readonly")
        self.prediction_file_dropdown.pack(fill="x", pady=5)

        # Buttons for each script step
        self.add_button(left_frame, "Run Data Cleaning", self.run_data_cleaning_thread)
        self.add_button(left_frame, "Run EDA", self.run_eda_thread)
        self.add_button(left_frame, "Run Model Training", self.run_model_training_thread)
        self.add_button(left_frame, "Run Prediction", self.run_prediction_thread)

        # Output box to capture terminal output
        self.output_text = scrolledtext.ScrolledText(right_frame, wrap=tk.WORD)
        self.output_text.pack(fill='both', expand=True)
        # For terminal input
        self.output_text.bind("<Return>", self.on_enter)  # Bind Enter key to capture user input
        self.current_process = None  # Store the current subprocess for user input

    def on_enter(self, event):
        """Handle Enter key press for user input in output_text."""
        if self.current_process:
            # Find the index of the last newline character
            last_newline_index = self.output_text.search('\n', 'end-1c', '1.0', backwards=True)
            if last_newline_index:
                user_input_start = self.output_text.index('%s + 1c' % last_newline_index)
            else:
                user_input_start = '1.0'
            user_input = self.output_text.get(user_input_start, 'end-1c') + '\n'
            self.current_process.stdin.write(user_input)
            self.current_process.stdin.flush()
            self.output_text.insert(tk.END, '\n')  # Add a newline after input
            return 'break'  # Prevent default behavior of adding another newline


    def run_command(self, command):
        """Run a shell command and capture real-time output with interactive input."""
        # self.current_process = subprocess.Popen(
        #     command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=True
        # )

        # # Start a thread to capture output without blocking the GUI
        env = os.environ.copy()
        env['PYTHONUNBUFFERED'] = '1'  # Ensure unbuffered output
        self.current_process = subprocess.Popen(
            command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            shell=True,
            env=env
        )
        threading.Thread(target=self.capture_output).start()

    def capture_output(self):
        """Capture real-time output from the subprocess and display it in output_text."""
        for line in self.current_process.stdout:
            self.output_text.insert(tk.END, line)
            self.output_text.see(tk.END)
            # Move the insertion cursor to the end
            self.output_text.mark_set(tk.INSERT, tk.END)
            self.output_text.focus_set()
            self.root.update()  # Update the GUI with new output

        for line in self.current_process.stderr:
            self.output_text.insert(tk.END, line)
            self.output_text.see(tk.END)
            # Move the insertion cursor to the end
            self.output_text.mark_set(tk.INSERT, tk.END)
            self.output_text.focus_set()
            self.root.update()

        # Close process streams after completion
        self.current_process.stdout.close()
        self.current_process.stderr.close()
        self.current_process.wait()
        self.current_process = None  # Reset the process


    def add_folder_selector(self, frame, label_text, command=None):
        container = tk.Frame(frame)
        container.pack(fill='x', pady=5)

        label = tk.Label(container, text=label_text)
        label.pack(anchor="w")

        folder_path = tk.StringVar()
        entry_container = tk.Frame(container)
        entry_container.pack(fill='x')

        folder_entry = tk.Entry(entry_container, textvariable=folder_path)
        folder_entry.pack(side='left', fill='x', expand=True)

        browse_button = tk.Button(entry_container, text="Browse", command=lambda: self.select_folder(folder_path, command))
        browse_button.pack(side='left', padx=5)

        return folder_path


    def browse_folder(self, folder_path_var, update_command=None):
        selected_folder = filedialog.askdirectory()
        if selected_folder:
            folder_path_var.set(selected_folder)
            if update_command:
                update_command(selected_folder)

    def add_button(self, frame, text, command):
        button = tk.Button(frame, text=text, command=command)
        button.pack(fill="x", pady=5)

    def select_folder(self, folder_path_var, callback=None):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            folder_path_var.set(folder_selected)
            if callback:
                callback(folder_selected)

    def update_file_list(self, folder_path):
        """Update the dropdown list with files from the selected training data folder."""
        if not folder_path:
            return

        files = [f for f in os.listdir(folder_path) if f.endswith('.csv')]
        self.file_dropdown['values'] = files  # Update dropdown values
        if files:
            self.file_dropdown.current(0)  # Set the first file as the default selection

    # def update_eda_file_list(self, folder_path):
    #     """Update the dropdown list with files from the selected cleaned data folder for EDA."""
    #     if not folder_path:
    #         return

    #     files = [f for f in os.listdir(folder_path) if f.endswith('.csv')]
    #     self.eda_file_dropdown['values'] = files
    #     if files:
    #         self.eda_file_dropdown.current(0)

    def update_eda_file_list(self, folder_path):
        """Update the dropdown list with files from the selected cleaned data folder for EDA and prediction."""
        if not folder_path:
            return

        files = [f for f in os.listdir(folder_path) if f.endswith('.csv')]
        self.eda_file_dropdown['values'] = files
        self.prediction_file_dropdown['values'] = files  # Update prediction file dropdown
        if files:
            self.eda_file_dropdown.current(0)
            self.prediction_file_dropdown.current(0)


    def update_model_training_file_list(self, folder_path):
        # Updates model training files based on model_training_folder
        files = [f for f in os.listdir(folder_path) if f.endswith('.csv')]
        self.model_file_dropdown['values'] = files
        if files:
            self.model_file_dropdown.current(0)

    # def run_command(self, command):
    #     process = subprocess.Popen(
    #         command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=True
    #     )

    #     # Capture real-time output
    #     for line in process.stdout:
    #         self.output_text.insert(tk.END, line)
    #         self.output_text.see(tk.END)
    #         self.root.update()

    #     for line in process.stderr:
    #         self.output_text.insert(tk.END, line)
    #         self.output_text.see(tk.END)
    #         self.root.update()

    #     process.stdout.close()
    #     process.stderr.close()
    #     process.wait()

    def run_data_cleaning_thread(self):
        threading.Thread(target=self.run_clean_data).start()

    def run_eda_thread(self):
        threading.Thread(target=self.run_perform_eda).start()

    def run_model_training_thread(self):
        threading.Thread(target=self.run_model_training).start()

    def run_prediction_thread(self):
        threading.Thread(target=self.run_prediction).start()

    def run_clean_data(self):
        training_data_folder = self.training_data_folder.get()
        selected_file = self.file_dropdown.get()
        cleaned_data_folder = self.cleaned_data_folder.get()

        if training_data_folder and selected_file and cleaned_data_folder:
            # Ensure that the cleaned data folder exists
            os.makedirs(cleaned_data_folder, exist_ok=True)

            # Constructing the input and output paths correctly
            input_file_path = os.path.join(training_data_folder, selected_file)
            output_file_name = f"cleaned_{selected_file}"
            output_file_path = os.path.join(cleaned_data_folder, output_file_name)

            # Adjusted command to avoid --input_file; use --file instead, matching the argument name in clean_data.py
            command = f"python clean_data.py --input_folder {training_data_folder} --output_folder {cleaned_data_folder} --file {selected_file}"
            
            # Run the command
            self.run_command(command)
        else:
            messagebox.showerror("Error", "Please select the training data folder, cleaned data folder, and a file for data cleaning.")

    def run_perform_eda(self):
        cleaned_data_folder = self.cleaned_data_folder.get()
        selected_file = self.eda_file_dropdown.get()
        eda_output_folder = self.eda_output_folder.get()

        if cleaned_data_folder and selected_file and eda_output_folder:
            os.makedirs(eda_output_folder, exist_ok=True)
            input_file_path = os.path.join(cleaned_data_folder, selected_file)
            command = f"python perform_eda.py --input_folder {cleaned_data_folder} --output_folder {eda_output_folder} --file {selected_file}"
            self.run_command(command)
        else:
            messagebox.showerror("Error", "Please select the cleaned data folder, EDA output folder, and a file for EDA.")

    def run_model_training(self):
        selected_file = self.model_file_dropdown.get()
        cleaned_data_folder = self.cleaned_data_folder.get()
        model_output_folder = self.model_output_folder.get()

        # if cleaned_data_folder and model_output_folder and selected_file:
        if model_output_folder and selected_file:
            # command = f"python model_training.py --input_folder {cleaned_data_folder} --model_output {model_output_folder}"
            # command = f"python model_training.py --model_output {model_output_folder}"
            command = f"python -u model_training.py --model_output {model_output_folder}"
            self.run_command(command)
        else:
            messagebox.showerror("Error", "Please select cleaned data and model output folders for training.")

    # def run_perform_prediction(self):
    #     model_folder = self.model_output_folder.get()
    #     output_folder = "predict_outputs"
    #     if model_folder:
    #         command = f"python perform_prediction.py --model_folder {model_folder} --output_folder {output_folder}"
    #         self.run_command(command)
    #     else:
    #         messagebox.showerror("Error", "Please select model output folder for prediction.")

    def run_prediction(self):
        input_folder = self.cleaned_data_folder.get()
        model_folder = self.model_output_folder.get()
        output_folder = "visualize_output"  # You can also add a folder selector for this if needed
        selected_file = self.prediction_file_dropdown.get()

        if input_folder and model_folder and selected_file:
            command = f"python -u perform_prediction.py --input_folder {input_folder} --model_folder {model_folder} --output_folder {output_folder} --file {selected_file}"
            self.run_command(command)
        else:
            messagebox.showerror("Error", "Please select input, model, and output folders, and a file for prediction.")



if __name__ == "__main__":
    root = tk.Tk()
    app = PipelineGUI(root)
    root.mainloop()
