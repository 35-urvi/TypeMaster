import tkinter as tk
from tkinter import ttk, messagebox

class SettingsManager:
    def __init__(self, parent_app):
        """Initialize settings manager"""
        self.parent_app = parent_app
        
        # Default settings
        self.settings = {
            "sound_enabled": True,
            "theme": "dark",
            "font_size": 18
        }
    
    def get_font_size(self):
        """Get current font size"""
        return self.settings["font_size"]
    
    def set_font_size(self, size):
        """Set font size"""
        self.settings["font_size"] = size
    
    def get_theme(self):
        """Get current theme"""
        return self.settings["theme"]
    
    def set_theme(self, theme):
        """Set theme"""
        self.settings["theme"] = theme
        # Apply theme changes
        self.apply_theme(theme)
    
    def apply_theme(self, theme):
        """Apply visual theme to the application"""
        if theme == "dark":
            bg_color = "#323437"
            fg_color = "#d1d0c5"
            accent_color = "#e2b714"
            input_bg = "#2c2e31"
        elif theme == "light":
            bg_color = "#f5f5f5"
            fg_color = "#323437"
            accent_color = "#e2b714"
            input_bg = "#ffffff"
        else:  # Default to dark
            bg_color = "#323437"
            fg_color = "#d1d0c5"
            accent_color = "#e2b714"
            input_bg = "#2c2e31"
        
        # Apply to main window and frames
        try:
            self.parent_app.configure(bg=bg_color)
            self.parent_app.main_frame.configure(bg=bg_color)
            
            # Update other widgets - this is just a starting point
            for widget in self.parent_app.main_frame.winfo_children():
                try:
                    if isinstance(widget, tk.Frame):
                        widget.configure(bg=bg_color)
                    elif isinstance(widget, tk.Label):
                        widget.configure(bg=bg_color, fg=fg_color)
                    elif isinstance(widget, tk.Button):
                        widget.configure(bg=accent_color, fg=bg_color)
                    elif isinstance(widget, tk.Entry):
                        widget.configure(bg=input_bg, fg=fg_color)
                except Exception:
                    # Skip widgets that don't support these configurations
                    pass
        except Exception as e:
            print(f"Error applying theme: {e}")
    
    def show_settings_dialog(self):
        """Show settings dialog"""
        settings_dialog = tk.Toplevel(self.parent_app)
        settings_dialog.title("Settings")
        settings_dialog.geometry("500x400")
        settings_dialog.configure(bg="#323437")
        settings_dialog.transient(self.parent_app)
        settings_dialog.grab_set()
        
        # Create notebook for tabbed settings
        notebook = ttk.Notebook(settings_dialog)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Profile tab
        profile_frame = tk.Frame(notebook, bg="#323437")
        notebook.add(profile_frame, text="Profile")
        
        # Get current user
        current_user = self.parent_app.current_user
        if current_user and current_user != "guest":
            self.display_user_profile(profile_frame, current_user)
        else:
            no_user_label = tk.Label(profile_frame, text="Please log in to view profile", 
                                    font=("Courier", 14), bg="#323437", fg="#d1d0c5")
            no_user_label.pack(pady=20)
        
        # Appearance settings tab
        appearance_frame = tk.Frame(notebook, bg="#323437")
        notebook.add(appearance_frame, text="Appearance")
        
        # Theme setting
        theme_frame = tk.Frame(appearance_frame, bg="#323437")
        theme_frame.pack(fill=tk.X, pady=10)
        
        theme_label = tk.Label(theme_frame, text="Theme:", 
                             font=("Courier", 12), bg="#323437", fg="#d1d0c5")
        theme_label.grid(row=0, column=0, sticky='w', padx=10)
        
        theme_var = tk.StringVar(value=self.settings["theme"])
        theme_options = ["dark", "light"]
        theme_menu = ttk.Combobox(theme_frame, textvariable=theme_var, 
                                values=theme_options, state="readonly")
        theme_menu.grid(row=0, column=1, padx=10)
        
        # Sound settings tab
        sound_frame = tk.Frame(notebook, bg="#323437")
        notebook.add(sound_frame, text="Sound")
        
        # Sound enabled setting
        sound_enabled_frame = tk.Frame(sound_frame, bg="#323437")
        sound_enabled_frame.pack(fill=tk.X, pady=10)
        
        sound_var = tk.BooleanVar(value=self.settings["sound_enabled"])
        sound_check = tk.Checkbutton(sound_enabled_frame, text="Enable Sound Effects", 
                                   variable=sound_var, bg="#323437", fg="#d1d0c5",
                                   selectcolor="#323437", activebackground="#323437")
        sound_check.pack(padx=10, pady=10, anchor='w')
        
        # Buttons frame
        buttons_frame = tk.Frame(settings_dialog, bg="#323437")
        buttons_frame.pack(pady=10)
        
        # Save button
        save_button = tk.Button(buttons_frame, text="Save", font=("Courier", 12),
                              bg="#e2b714", fg="#323437", width=10,
                              command=lambda: self.save_settings(
                                  theme_var.get(),

                                  sound_var.get(),
                                  settings_dialog
                              ))
        save_button.grid(row=0, column=0, padx=10)
        
        # Cancel button
        cancel_button = tk.Button(buttons_frame, text="Cancel", font=("Courier", 12),
                                bg="#d1d0c5", fg="#323437", width=10,
                                command=settings_dialog.destroy)
        cancel_button.grid(row=0, column=1, padx=10)
    
    def display_user_profile(self, frame, username):
        """Display user profile information"""
        # Get user data from database
        self.parent_app.db_manager.cursor.execute(
            "SELECT username, email, tests_completed, avg_wpm, avg_accuracy, date_joined FROM users WHERE username = ?",
            (username,)
        )
        user_data = self.parent_app.db_manager.cursor.fetchone()
        
        if not user_data:
            error_label = tk.Label(frame, text="Error: User data not found", 
                                 font=("Courier", 14), bg="#323437", fg="#e2b714")
            error_label.pack(pady=20)
            return
            
        # Unpack user data
        username, email, tests_completed, avg_wpm, avg_accuracy, join_date = user_data
        
        # Create profile display
        profile_title = tk.Label(frame, text="User Profile", 
                               font=("Courier", 16, "bold"), bg="#323437", fg="#e2b714")
        profile_title.pack(pady=(20, 30))
        
        # Profile info container
        info_frame = tk.Frame(frame, bg="#323437")
        info_frame.pack(pady=10, fill=tk.X, padx=20)
        
        # Username
        username_label = tk.Label(info_frame, text="Username:", 
                                font=("Courier", 12, "bold"), bg="#323437", fg="#d1d0c5")
        username_label.grid(row=0, column=0, sticky='w', pady=5, padx=10)
        
        username_value = tk.Label(info_frame, text=username, 
                                font=("Courier", 12), bg="#323437", fg="#d1d0c5")
        username_value.grid(row=0, column=1, sticky='w', pady=5)
        
        # Email
        email_label = tk.Label(info_frame, text="Email:", 
                             font=("Courier", 12, "bold"), bg="#323437", fg="#d1d0c5")
        email_label.grid(row=1, column=0, sticky='w', pady=5, padx=10)
        
        email_value = tk.Label(info_frame, text=email, 
                             font=("Courier", 12), bg="#323437", fg="#d1d0c5")
        email_value.grid(row=1, column=1, sticky='w', pady=5)
        
        # Join Date
        join_label = tk.Label(info_frame, text="Joined:", 
                            font=("Courier", 12, "bold"), bg="#323437", fg="#d1d0c5")
        join_label.grid(row=2, column=0, sticky='w', pady=5, padx=10)
        
        join_value = tk.Label(info_frame, text=join_date, 
                            font=("Courier", 12), bg="#323437", fg="#d1d0c5")
        join_value.grid(row=2, column=1, sticky='w', pady=5)
        
        # Tests Completed
        tests_label = tk.Label(info_frame, text="Tests Completed:", 
                             font=("Courier", 12, "bold"), bg="#323437", fg="#d1d0c5")
        tests_label.grid(row=3, column=0, sticky='w', pady=5, padx=10)
        
        tests_value = tk.Label(info_frame, text=str(tests_completed), 
                             font=("Courier", 12), bg="#323437", fg="#d1d0c5")
        tests_value.grid(row=3, column=1, sticky='w', pady=5)
        
        # Average WPM
        wpm_label = tk.Label(info_frame, text="Average WPM:", 
                           font=("Courier", 12, "bold"), bg="#323437", fg="#d1d0c5")
        wpm_label.grid(row=4, column=0, sticky='w', pady=5, padx=10)
        
        wpm_value = tk.Label(info_frame, text=f"{avg_wpm:.1f}" if avg_wpm else "N/A", 
                           font=("Courier", 12), bg="#323437", fg="#d1d0c5")
        wpm_value.grid(row=4, column=1, sticky='w', pady=5)
        
        # Average Accuracy
        acc_label = tk.Label(info_frame, text="Average Accuracy:", 
                           font=("Courier", 12, "bold"), bg="#323437", fg="#d1d0c5")
        acc_label.grid(row=5, column=0, sticky='w', pady=5, padx=10)
        
        acc_value = tk.Label(info_frame, text=f"{avg_accuracy:.1f}%" if avg_accuracy else "N/A", 
                           font=("Courier", 12), bg="#323437", fg="#d1d0c5")
        acc_value.grid(row=5, column=1, sticky='w', pady=5)
    
    def save_settings(self, theme, sound_enabled, dialog):
        """Save settings and apply changes"""
        # Update settings
        self.settings["theme"] = theme
        self.settings["sound_enabled"] = sound_enabled
        
        # Apply theme
        self.apply_theme(theme)
        
        # Update sound setting
        self.parent_app.sound_manager.sound_enabled = sound_enabled
        
        # Close dialog
        dialog.destroy()
        
        # Show confirmation
        messagebox.showinfo("Settings", "Settings have been saved successfully!")