import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import time
import random
import os
from datetime import datetime
import sys

# Import our modules
from database_manager import DatabaseManager
from user_auth import UserAuth
from typing_test import TypingTest
from stats_visualizer import StatsVisualizer
from settings_manager import SettingsManager
from sound_manager import SoundManager

class TypeMaster(tk.Tk):
    def __init__(self):
        super().__init__()
        
        # Set up the main window
        self.title("Type Master")
        self.geometry("1000x700")
        self.configure(bg="#323437")
        
        # Initialize database
        self.db_manager = DatabaseManager("typing_data.db")
        self.db_manager.setup_database()
        
        # Initialize user authentication
        self.user_auth = UserAuth(self, self.db_manager)
        self.current_user = None
        
        # Initialize settings
        self.settings_manager = SettingsManager(self)
        
        # Initialize sound manager
        self.sound_manager = SoundManager()
        
        # Create the main frame
        self.main_frame = tk.Frame(self, bg="#323437")
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Create menu bar
        self.create_menu_bar()
        
        # Show login/registration screen or start directly
        self.show_welcome_screen()
    
    def create_menu_bar(self):
        menu_bar = tk.Menu(self)
        
        # File menu
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="Export Results", command=self.export_results)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.quit)
        menu_bar.add_cascade(label="File", menu=file_menu)
        
        # Test modes menu
        test_menu = tk.Menu(menu_bar, tearoff=0)
        test_menu.add_command(label="Time: 15s", command=lambda: self.start_test("time", 15))
        test_menu.add_command(label="Time: 30s", command=lambda: self.start_test("time", 30))
        test_menu.add_command(label="Time: 60s", command=lambda: self.start_test("time", 60))
        test_menu.add_command(label="Time: 120s", command=lambda: self.start_test("time", 120))
        test_menu.add_separator()
        test_menu.add_command(label="Words: 10", command=lambda: self.start_test("words", 10))
        test_menu.add_command(label="Words: 25", command=lambda: self.start_test("words", 25))
        test_menu.add_command(label="Words: 50", command=lambda: self.start_test("words", 50))
        test_menu.add_command(label="Words: 100", command=lambda: self.start_test("words", 100))
        test_menu.add_separator()
        test_menu.add_command(label="Paragraph", command=lambda: self.start_test("paragraph"))
        test_menu.add_command(label="Custom Text", command=self.show_custom_text_dialog)
        menu_bar.add_cascade(label="Test Mode", menu=test_menu)
        
        # Settings menu
        settings_menu = tk.Menu(menu_bar, tearoff=0)
        settings_menu.add_command(label="Toggle Sound", command=self.toggle_sound)
        settings_menu.add_command(label="User Settings", command=self.show_settings)
        menu_bar.add_cascade(label="Settings", menu=settings_menu)
        
        # Stats menu
        stats_menu = tk.Menu(menu_bar, tearoff=0)
        stats_menu.add_command(label="View Progress", command=self.show_progress)
        stats_menu.add_command(label="Leaderboard", command=self.show_leaderboard)
        menu_bar.add_cascade(label="Statistics", menu=stats_menu)
        
        # Help menu
        help_menu = tk.Menu(menu_bar, tearoff=0)
        help_menu.add_command(label="How to Use", command=self.show_help)
        help_menu.add_command(label="About", command=self.show_about)
        menu_bar.add_cascade(label="Help", menu=help_menu)
        
        self.config(menu=menu_bar)
    
    def show_welcome_screen(self):
        # Clear the main frame
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        
        # Create welcome frame
        welcome_frame = tk.Frame(self.main_frame, bg="#323437")
        welcome_frame.pack(expand=True)
        
        # Title
        title_label = tk.Label(welcome_frame, text="TypeMaster-Python Typing Speed Tracker", 
                             font=("Courier", 24, "bold"), bg="#323437", fg="#e2b714")
        title_label.pack(pady=20)
        
        # Subtitle
        subtitle_label = tk.Label(welcome_frame, text="Test your typing skills!", 
                                font=("Courier", 16), bg="#323437", fg="#d1d0c5")
        subtitle_label.pack(pady=10)
        
        # Buttons frame
        buttons_frame = tk.Frame(welcome_frame, bg="#323437")
        buttons_frame.pack(pady=20)
        
        # Login button
        login_button = tk.Button(buttons_frame, text="Login", font=("Courier", 12),
                               bg="#e2b714", fg="#323437", width=15,
                               command=self.user_auth.show_login)
        login_button.grid(row=0, column=0, padx=10, pady=10)
        
        # Register button
        register_button = tk.Button(buttons_frame, text="Register", font=("Courier", 12),
                                  bg="#e2b714", fg="#323437", width=15,
                                  command=self.user_auth.show_register)
        register_button.grid(row=0, column=1, padx=10, pady=10)
        
        # Quick start button
        quick_start_button = tk.Button(buttons_frame, text="Quick Start", font=("Courier", 12),
                                     bg="#d1d0c5", fg="#323437", width=15,
                                     command=lambda: self.start_test("time", 30))
        quick_start_button.grid(row=1, column=0, columnspan=2, padx=10, pady=10)
    
    def start_test(self, mode, value=None, custom_text=None):
        # Clear the main frame
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        
        # Use default difficulty instead of allowing user to select
        default_difficulty = "beginner"
        
        # Create the typing test
        self.typing_test = TypingTest(
            self.main_frame, 
            self, 
            mode, 
            value, 
            default_difficulty,
            self.sound_manager,
            custom_text
        )
        
        # Start the test
        self.typing_test.start()
    
    def save_results(self, results):
        # If user is logged in, save results to database
        username = self.current_user if self.current_user else "guest"
        
        # Save the results to the database
        test_id = self.db_manager.save_test_results(
            username,
            results["mode"],
            results["difficulty"],
            results["wpm"],
            results["accuracy"],
            results["errors"],
            results["correct_chars"],
            results["total_chars"],
            results["test_duration"]
        )
        
        # Show results
        self.show_results(results, test_id)
    
    def show_results(self, results, test_id):
        # Clear the main frame
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        
        # Create results frame
        results_frame = tk.Frame(self.main_frame, bg="#323437")
        results_frame.pack(expand=True, fill=tk.BOTH)
        
        # Title
        title_label = tk.Label(results_frame, text="Test Results", 
                             font=("Courier", 24, "bold"), bg="#323437", fg="#e2b714")
        title_label.pack(pady=20)
        
        # Results
        stats_frame = tk.Frame(results_frame, bg="#323437")
        stats_frame.pack(pady=10)
        
        # WPM
        wpm_label = tk.Label(stats_frame, text=f"Words Per Minute: {results['wpm']:.1f}", 
                           font=("Courier", 16), bg="#323437", fg="#d1d0c5")
        wpm_label.grid(row=0, column=0, pady=5, sticky='w')
        
        # Accuracy
        accuracy_label = tk.Label(stats_frame, text=f"Accuracy: {results['accuracy']:.1f}%", 
                                font=("Courier", 16), bg="#323437", fg="#d1d0c5")
        accuracy_label.grid(row=1, column=0, pady=5, sticky='w')
        
        # Duration
        duration_label = tk.Label(stats_frame, text=f"Duration: {results['test_duration']:.1f}s", 
                                font=("Courier", 16), bg="#323437", fg="#d1d0c5")
        duration_label.grid(row=3, column=0, pady=5, sticky='w')
        
        # Create a visualizer for the graph
        visualizer = StatsVisualizer(results_frame, self.db_manager)
        
        # Create graph of WPM over time
        visualizer.create_wpm_graph(results["wpm_over_time"], results["wpm"])
        
        # Buttons frame
        buttons_frame = tk.Frame(results_frame, bg="#323437")
        buttons_frame.pack(pady=20)
        
        # Restart button
        restart_button = tk.Button(buttons_frame, text="Try Again", font=("Courier", 12),
                                 bg="#e2b714", fg="#323437", width=15,
                                 command=lambda: self.start_test(results["mode"], results["value"]))
        restart_button.grid(row=0, column=0, padx=10)
        
        # Home button
        home_button = tk.Button(buttons_frame, text="Exit", font=("Courier", 12),
                              bg="#d1d0c5", fg="#323437", width=15,
                              command=self.show_welcome_screen)
        home_button.grid(row=0, column=1, padx=10)
    
    def show_custom_text_dialog(self):
        dialog = tk.Toplevel(self)
        dialog.title("Custom Text")
        dialog.geometry("500x300")
        dialog.configure(bg="#323437")
        dialog.transient(self)
        dialog.grab_set()
        
        # Label
        label = tk.Label(dialog, text="Enter custom text for typing test:", 
                       font=("Courier", 12), bg="#323437", fg="#d1d0c5")
        label.pack(pady=10)
        
        # Text area
        text_area = tk.Text(dialog, font=("Courier", 12), bg="#2c2e31", fg="#d1d0c5",
                          height=10, width=50)
        text_area.pack(pady=10, padx=20)
        
        # Button frame
        button_frame = tk.Frame(dialog, bg="#323437")
        button_frame.pack(pady=10)
        
        # Start button
        start_button = tk.Button(button_frame, text="Start Test", font=("Courier", 12),
                               bg="#e2b714", fg="#323437", width=10,
                               command=lambda: self.handle_custom_text(text_area.get("1.0", "end-1c"), dialog))
        start_button.grid(row=0, column=0, padx=10)
        
        # Cancel button
        cancel_button = tk.Button(button_frame, text="Cancel", font=("Courier", 12),
                                bg="#d1d0c5", fg="#323437", width=10,
                                command=dialog.destroy)
        cancel_button.grid(row=0, column=1, padx=10)
    
    def handle_custom_text(self, text, dialog):
        if not text.strip():
            messagebox.showerror("Error", "Please enter some text for the test.")
            return
        
        dialog.destroy()
        self.start_test("custom", None, text)
    
    def toggle_sound(self):
        self.sound_manager.toggle_sound()
        status = "enabled" if self.sound_manager.sound_enabled else "disabled"
        messagebox.showinfo("Sound", f"Sound effects {status}")
    
    def show_settings(self):
        self.settings_manager.show_settings_dialog()
    
    def show_progress(self):
        if not self.current_user:
            messagebox.showinfo("Login Required", "Please log in to view your progress.")
            return
        
        visualizer = StatsVisualizer(None, self.db_manager)
        visualizer.show_progress_window(self.current_user)
    
    def show_leaderboard(self):
        visualizer = StatsVisualizer(None, self.db_manager)
        visualizer.show_leaderboard()
    
    def export_results(self):
        if not self.current_user:
            messagebox.showinfo("Login Required", "Please log in to export your results.")
            return
        
        self.db_manager.export_results(self.current_user)
        messagebox.showinfo("Export", "Results exported successfully to 'typing_results.csv'")
    
    def show_help(self):
        help_text = """
        Typing Speed Tracker Help:
        
        1. Choose a test mode from the 'Test Mode' menu
        2. Type the text displayed as accurately and quickly as possible
        3. Results will be shown after the test is complete
        4. View your progress in the 'Statistics' menu
        
        Keyboard shortcuts:
        - Esc: Cancel current test and Quit application
        """
        
        messagebox.showinfo("Help", help_text)
    
    def show_about(self):
        about_text = """
        Python Typing Speed Tracker
        
        A TypeMaster typing test application
        built with Python, Tkinter, SQLite, and Matplotlib.
        
        Features:
        - user accounts
        - test modes
        - settings
        - statasctics
        - export result
        """
        
        messagebox.showinfo("About", about_text)

if __name__ == "__main__":
    app = TypeMaster()
    app.mainloop()