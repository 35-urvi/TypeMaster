import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from datetime import datetime
import matplotlib.dates as mdates

class StatsVisualizer:
    def __init__(self, parent_frame, db_manager):
        """Initialize the stats visualizer with a parent frame and database manager"""
        self.parent_frame = parent_frame
        self.db_manager = db_manager
        
    def create_wpm_graph(self, wpm_over_time, final_wpm):
        """Create a graph showing WPM over time for a single test"""
        # Create figure and axis
        fig = plt.Figure(figsize=(6, 3), dpi=100)
        ax = fig.add_subplot(111)
        
        # Plot WPM over time
        if wpm_over_time:
            time_points = list(range(1, len(wpm_over_time) + 1))
            ax.plot(time_points, wpm_over_time, marker='o', linestyle='-', color='#e2b714')
            
            # Add horizontal line for final WPM
            ax.axhline(y=final_wpm, color='#d1d0c5', linestyle='--', alpha=0.7)
            
            # Add text for final WPM
            ax.text(len(time_points) * 0.8, final_wpm * 1.05, f"Final WPM: {final_wpm:.1f}", 
                   color='#d1d0c5', fontsize=9)
        else:
            ax.text(0.5, 0.5, "No data available", 
                   horizontalalignment='center', verticalalignment='center',
                   transform=ax.transAxes, color='#d1d0c5')
        
        # Configure appearance
        ax.set_facecolor('#2c2e31')
        fig.patch.set_facecolor('#323437')
        ax.spines['bottom'].set_color('#d1d0c5')
        ax.spines['top'].set_color('#2c2e31')
        ax.spines['left'].set_color('#d1d0c5')
        ax.spines['right'].set_color('#2c2e31')
        ax.tick_params(axis='both', colors='#d1d0c5')
        ax.set_title('WPM Over Time', color='#d1d0c5')
        ax.set_xlabel('Time (seconds)', color='#d1d0c5')
        ax.set_ylabel('WPM', color='#d1d0c5')
        
        # Create canvas and add to parent frame
        canvas = FigureCanvasTkAgg(fig, master=self.parent_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(pady=10, padx=10, fill=tk.BOTH, expand=True)
    
    def show_progress_window(self, username):
        """Show a window with user progress over time"""
        # Create new toplevel window
        progress_window = tk.Toplevel()
        progress_window.title(f"Typing Progress - {username}")
        progress_window.geometry("800x600")
        progress_window.configure(bg="#323437")
        
        # Get user progress data
        progress_data = self.db_manager.get_user_progress(username)
        
        if not progress_data:
            # No data available
            no_data_label = tk.Label(progress_window, text="No typing test data available.", 
                                   font=("Courier", 16), bg="#323437", fg="#d1d0c5")
            no_data_label.pack(expand=True)
            return
        
        # Create notebook for tabs
        notebook = ttk.Notebook(progress_window)
        
        # Create WPM progress tab
        wpm_frame = tk.Frame(notebook, bg="#323437")
        self.create_progress_graph(wpm_frame, progress_data, "wpm", "WPM Progress Over Time")
        notebook.add(wpm_frame, text="WPM Progress")
        
        # Create accuracy progress tab
        accuracy_frame = tk.Frame(notebook, bg="#323437")
        self.create_progress_graph(accuracy_frame, progress_data, "accuracy", "Accuracy Progress Over Time")
        notebook.add(accuracy_frame, text="Accuracy Progress")
        
        # Create statistics tab
        stats_frame = tk.Frame(notebook, bg="#323437")
        self.create_stats_summary(stats_frame, username, progress_data)
        notebook.add(stats_frame, text="Statistics Summary")
        
        notebook.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)
        
        # Add close button
        close_button = tk.Button(progress_window, text="Close", font=("Courier", 12),
                               bg="#e2b714", fg="#323437", width=10,
                               command=progress_window.destroy)
        close_button.pack(pady=10)
    
    def create_progress_graph(self, parent_frame, progress_data, data_type, title):
        """Create a graph showing progress over time for WPM or accuracy"""
        # Extract data
        y_values = [row[0] if data_type == "wpm" else row[1] for row in progress_data]
        timestamps = [datetime.strptime(row[2], "%Y-%m-%d %H:%M:%S") for row in progress_data]
        
        # Create figure and axis
        fig = plt.Figure(figsize=(10, 6), dpi=100)
        ax = fig.add_subplot(111)
        
        # Plot data
        ax.plot(timestamps, y_values, marker='o', linestyle='-', color='#e2b714')
        
        # Add trend line
        if len(y_values) > 1:
            z = np.polyfit(range(len(timestamps)), y_values, 1)
            p = np.poly1d(z)
            ax.plot(timestamps, p(range(len(timestamps))), "r--", alpha=0.7, label="Trend")
            
            # Add text indicating improvement
            slope = z[0]
            if slope > 0:
                trend_text = f"Improving: +{slope:.2f} per test"
            elif slope < 0:
                trend_text = f"Declining: {slope:.2f} per test"
            else:
                trend_text = "No change over time"
                
            ax.text(0.02, 0.95, trend_text, transform=ax.transAxes, 
                   color='#d1d0c5', fontsize=10)
        
        # Configure date formatting
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        fig.autofmt_xdate()
        
        # Configure appearance
        ax.set_facecolor('#2c2e31')
        fig.patch.set_facecolor('#323437')
        ax.spines['bottom'].set_color('#d1d0c5')
        ax.spines['top'].set_color('#2c2e31')
        ax.spines['left'].set_color('#d1d0c5')
        ax.spines['right'].set_color('#2c2e31')
        ax.tick_params(axis='both', colors='#d1d0c5')
        ax.set_title(title, color='#d1d0c5')
        ax.set_xlabel('Date', color='#d1d0c5')
        
        if data_type == "wpm":
            ax.set_ylabel('Words Per Minute', color='#d1d0c5')
        else:
            ax.set_ylabel('Accuracy (%)', color='#d1d0c5')
            ax.set_ylim(0, 100)
        
        # Create canvas and add to parent frame
        canvas = FigureCanvasTkAgg(fig, master=parent_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(pady=10, padx=10, fill=tk.BOTH, expand=True)
    
    def create_stats_summary(self, parent_frame, username, progress_data):
        """Create a summary of user statistics"""
        # Calculate statistics
        wpm_values = [row[0] for row in progress_data]
        accuracy_values = [row[1] for row in progress_data]
        
        avg_wpm = sum(wpm_values) / len(wpm_values)
        max_wpm = max(wpm_values)
        avg_accuracy = sum(accuracy_values) / len(accuracy_values)
        max_accuracy = max(accuracy_values)
        tests_completed = len(progress_data)
        
        # Find most recent highest WPM
        highest_wpm_index = wpm_values.index(max_wpm)
        highest_wpm_date = datetime.strptime(progress_data[highest_wpm_index][2], "%Y-%m-%d %H:%M:%S")
        
        # Create stats frame
        stats_container = tk.Frame(parent_frame, bg="#323437")
        stats_container.pack(expand=True, fill=tk.BOTH, padx=20, pady=20)
        
        # Title
        title_label = tk.Label(stats_container, text=f"Statistics for {username}", 
                             font=("Courier", 18, "bold"), bg="#323437", fg="#e2b714")
        title_label.pack(pady=(0, 20))
        
        # Create stats grid
        stats_frame = tk.Frame(stats_container, bg="#323437")
        stats_frame.pack()
        
        # Tests completed
        tests_label = tk.Label(stats_frame, text="Tests Completed:", 
                             font=("Courier", 14), bg="#323437", fg="#d1d0c5",
                             anchor="e", width=25)
        tests_label.grid(row=0, column=0, sticky="e", pady=5)
        
        tests_value = tk.Label(stats_frame, text=str(tests_completed), 
                             font=("Courier", 14, "bold"), bg="#323437", fg="#e2b714",
                             anchor="w", width=10)
        tests_value.grid(row=0, column=1, sticky="w", pady=5)
        
        # Average WPM
        avg_wpm_label = tk.Label(stats_frame, text="Average WPM:", 
                               font=("Courier", 14), bg="#323437", fg="#d1d0c5",
                               anchor="e", width=25)
        avg_wpm_label.grid(row=1, column=0, sticky="e", pady=5)
        
        avg_wpm_value = tk.Label(stats_frame, text=f"{avg_wpm:.1f}", 
                               font=("Courier", 14, "bold"), bg="#323437", fg="#e2b714",
                               anchor="w", width=10)
        avg_wpm_value.grid(row=1, column=1, sticky="w", pady=5)
        
        # Highest WPM
        max_wpm_label = tk.Label(stats_frame, text="Highest WPM:", 
                               font=("Courier", 14), bg="#323437", fg="#d1d0c5",
                               anchor="e", width=25)
        max_wpm_label.grid(row=2, column=0, sticky="e", pady=5)
        
        max_wpm_value = tk.Label(stats_frame, text=f"{max_wpm:.1f}", 
                               font=("Courier", 14, "bold"), bg="#323437", fg="#e2b714",
                               anchor="w", width=10)
        max_wpm_value.grid(row=2, column=1, sticky="w", pady=5)
        
        # Average Accuracy
        avg_acc_label = tk.Label(stats_frame, text="Average Accuracy:", 
                               font=("Courier", 14), bg="#323437", fg="#d1d0c5",
                               anchor="e", width=25)
        avg_acc_label.grid(row=3, column=0, sticky="e", pady=5)
        
        avg_acc_value = tk.Label(stats_frame, text=f"{avg_accuracy:.1f}%", 
                               font=("Courier", 14, "bold"), bg="#323437", fg="#e2b714",
                               anchor="w", width=10)
        avg_acc_value.grid(row=3, column=1, sticky="w", pady=5)
        
        # Highest Accuracy
        max_acc_label = tk.Label(stats_frame, text="Highest Accuracy:", 
                               font=("Courier", 14), bg="#323437", fg="#d1d0c5",
                               anchor="e", width=25)
        max_acc_label.grid(row=4, column=0, sticky="e", pady=5)
        
        max_acc_value = tk.Label(stats_frame, text=f"{max_accuracy:.1f}%", 
                               font=("Courier", 14, "bold"), bg="#323437", fg="#e2b714",
                               anchor="w", width=10)
        max_acc_value.grid(row=4, column=1, sticky="w", pady=5)
        
        # Best WPM date
        date_label = tk.Label(stats_frame, text="Best Performance Date:", 
                            font=("Courier", 14), bg="#323437", fg="#d1d0c5",
                            anchor="e", width=25)
        date_label.grid(row=5, column=0, sticky="e", pady=5)
        
        date_value = tk.Label(stats_frame, text=highest_wpm_date.strftime("%Y-%m-%d"), 
                            font=("Courier", 14, "bold"), bg="#323437", fg="#e2b714",
                            anchor="w", width=10)
        date_value.grid(row=5, column=1, sticky="w", pady=5)
    
    def show_leaderboard(self):
        """Show a window with the global leaderboard"""
        # Create new toplevel window
        leaderboard_window = tk.Toplevel()
        leaderboard_window.title("Typing Speed Leaderboard")
        leaderboard_window.geometry("700x500")
        leaderboard_window.configure(bg="#323437")
        
        # Title
        title_label = tk.Label(leaderboard_window, text="Global Leaderboard", 
                             font=("Courier", 20, "bold"), bg="#323437", fg="#e2b714")
        title_label.pack(pady=20)
        
        # Get leaderboard data
        leaderboard_data = self.db_manager.get_leaderboard(20)  # Get top 20
        
        if not leaderboard_data:
            # No data available
            no_data_label = tk.Label(leaderboard_window, text="No leaderboard data available yet.", 
                                   font=("Courier", 16), bg="#323437", fg="#d1d0c5")
            no_data_label.pack(expand=True)
        else:
            # Create scrollable frame for leaderboard
            container = tk.Frame(leaderboard_window, bg="#323437")
            container.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
            
            # Create canvas
            canvas = tk.Canvas(container, bg="#323437", highlightthickness=0)
            scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
            scrollable_frame = tk.Frame(canvas, bg="#323437")
            
            scrollable_frame.bind(
                "<Configure>",
                lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
            )
            
            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)
            
            # Pack scrollbar and canvas
            canvas.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")
            
            # Create headers
            headers_frame = tk.Frame(scrollable_frame, bg="#2c2e31")
            headers_frame.pack(fill=tk.X, pady=(0, 2))
            
            # Header labels
            headers = ["Rank", "Username", "WPM", "Accuracy", "Mode", "Difficulty", "Date"]
            widths = [5, 15, 8, 10, 10, 12, 20]
            
            for i, (header, width) in enumerate(zip(headers, widths)):
                header_label = tk.Label(headers_frame, text=header, 
                                      font=("Courier", 12, "bold"), bg="#2c2e31", fg="#d1d0c5",
                                      width=width)
                header_label.grid(row=0, column=i, padx=2, pady=5)
            
            # Add leaderboard entries
            for i, entry in enumerate(leaderboard_data):
                # Alternate row colors
                bg_color = "#323437" if i % 2 == 0 else "#2c2e31"
                
                row_frame = tk.Frame(scrollable_frame, bg=bg_color)
                row_frame.pack(fill=tk.X, pady=1)
                
                # Rank
                rank_label = tk.Label(row_frame, text=str(i+1), 
                                    font=("Courier", 12), bg=bg_color, fg="#d1d0c5",
                                    width=widths[0])
                rank_label.grid(row=0, column=0, padx=2, pady=3)
                
                # Username
                username_label = tk.Label(row_frame, text=entry[0], 
                                        font=("Courier", 12), bg=bg_color, fg="#e2b714",
                                        width=widths[1])
                username_label.grid(row=0, column=1, padx=2, pady=3)
                
                # WPM
                wpm_label = tk.Label(row_frame, text=f"{entry[1]:.1f}", 
                                   font=("Courier", 12), bg=bg_color, fg="#d1d0c5",
                                   width=widths[2])
                wpm_label.grid(row=0, column=2, padx=2, pady=3)
                
                # Accuracy
                accuracy_label = tk.Label(row_frame, text=f"{entry[2]:.1f}%", 
                                        font=("Courier", 12), bg=bg_color, fg="#d1d0c5",
                                        width=widths[3])
                accuracy_label.grid(row=0, column=3, padx=2, pady=3)
                
                # Mode
                mode_label = tk.Label(row_frame, text=entry[3].title(), 
                                    font=("Courier", 12), bg=bg_color, fg="#d1d0c5",
                                    width=widths[4])
                mode_label.grid(row=0, column=4, padx=2, pady=3)
                
                # Difficulty
                difficulty_label = tk.Label(row_frame, text=entry[4].title(), 
                                          font=("Courier", 12), bg=bg_color, fg="#d1d0c5",
                                          width=widths[5])
                difficulty_label.grid(row=0, column=5, padx=2, pady=3)
                
                # Date
                date_label = tk.Label(row_frame, text=entry[5].split()[0], 
                                    font=("Courier", 12), bg=bg_color, fg="#d1d0c5",
                                    width=widths[6])
                date_label.grid(row=0, column=6, padx=2, pady=3)
        
        # Add close button
        close_button = tk.Button(leaderboard_window, text="Close", font=("Courier", 12),
                               bg="#e2b714", fg="#323437", width=10,
                               command=leaderboard_window.destroy)
        close_button.pack(pady=15)