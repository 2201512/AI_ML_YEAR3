import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import subprocess
import os

# Main GUI class
class PipelineGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Data Pipeline GUI")
        self.root.geometry("400x300")

        # Copy terminal output to GUI
        

        # Initialize folder paths
        self.training_data_folder = None
        self.cleaned_data_folder = None
        self.model_output_folder = None
        
        # Directory selection buttons
        self.create_button("Select Training Data Folder", self.select_training_data_folder)
        self.create_button("Select Cleaned Data Folder", self.select_cleaned_data_folder)
        self.create_button("Select Model Output Folder", self.select_model_output_folder)
        
        # File selection for EDA
        self.create_button("Select Data for EDA", self.select_eda_file)
        
        # Run buttons for each stage
        self.create_button("Run Data Cleaning", self.run_data_cleaning)
        self.create_button("Run EDA", self.run_eda)
        self.create_button("Run Model Training", self.run_model_training)
        self.create_button("Run Prediction", self.run_prediction)
        
        # Status label
        self.status_label = tk.Label(self.root, text="Status: Waiting")
        self.status_label.pack(pady=10)

    def create_button(self, text, command):
        button = tk.Button(self.root, text=text, command=command, width=30)
        button.pack(pady=5)

    # Directory and file selection functions
    def select_training_data_folder(self):
        self.training_data_folder = filedialog.askdirectory()
        self.status_label.config(text=f"Selected Training Data: {self.training_data_folder}")

    def select_cleaned_data_folder(self):
        self.cleaned_data_folder = filedialog.askdirectory()
        self.status_label.config(text=f"Selected Cleaned Data: {self.cleaned_data_folder}")

    def select_model_output_folder(self):
        self.model_output_folder = filedialog.askdirectory()
        self.status_label.config(text=f"Selected Model Output: {self.model_output_folder}")

    def select_eda_file(self):
        self.eda_file = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        self.status_label.config(text=f"Selected EDA File: {self.eda_file}")

    # Run functions for each stage
    def run_data_cleaning(self):
        if not self.training_data_folder or not self.cleaned_data_folder:
            messagebox.showwarning("Warning", "Please select both training data and cleaned data folders.")
            return
        self.run_script("clean_data.py", self.training_data_folder, self.cleaned_data_folder)
        # self.run_script("clean_data.py", "cleaned_data_folder")

    def run_eda(self):
        if not self.eda_file:
            messagebox.showwarning("Warning", "Please select an EDA file.")
            return
        self.run_script("perform_eda.py", self.eda_file, self.cleaned_data_folder)
        # self.run_script("perform_eda.py", "eda_file")

    def run_model_training(self):
        if not self.cleaned_data_folder or not self.model_output_folder:
            messagebox.showwarning("Warning", "Please select cleaned data and model output folders.")
            return
        # self.run_script("model_training.py", self.cleaned_data_folder, self.model_output_folder)
        self.run_script("model_training.py", self.cleaned_data_folder, self.model_output_folder, "--model_output")
        # self.run_script("model_training.py", "model_output_folder")

    def run_prediction(self):
        if not self.cleaned_data_folder or not self.model_output_folder:
            messagebox.showwarning("Warning", "Please select cleaned data and model output folders.")
            return
        self.run_script("perform_prediction.py", self.cleaned_data_folder, self.model_output_folder)
        # self.run_script("perform_prediction.py", "model_output_folder")

    # def run_script(self, script_name, folder_name):
    #     try:
    #         subprocess.run(["python", script_name, "--input_folder", getattr(self, folder_name)], check=True)
    #         self.status_label.config(text=f"{script_name} completed successfully")
    #     except subprocess.CalledProcessError:
    #         messagebox.showerror("Error", f"Failed to run {script_name}")
    #         self.status_label.config(text=f"Error: {script_name} failed")
    # Version that takes input and output folders as arguments
    # def run_script(self, script_name, input_folder, output_folder):
    #     try:
    #         subprocess.run(["python", script_name, "--input_folder", input_folder, "--output_folder", output_folder], check=True)
    #         self.status_label.config(text=f"{script_name} completed successfully")
    #     except subprocess.CalledProcessError:
    #         messagebox.showerror("Error", f"Failed to run {script_name}")
    #         self.status_label.config(text=f"Error: {script_name} failed")
    def run_script(self, script_name, input_folder, output_folder, folder_arg_name="--output_folder"):
        try:
            subprocess.run(
                ["python", script_name, "--input_folder", input_folder, folder_arg_name, output_folder],
                check=True
            )
            self.status_label.config(text=f"{script_name} completed successfully")
        except subprocess.CalledProcessError:
            messagebox.showerror("Error", f"Failed to run {script_name}")
            self.status_label.config(text=f"Error: {script_name} failed")


# Initialize the GUI
root = tk.Tk()
app = PipelineGUI(root)
root.mainloop()
