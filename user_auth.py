import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import hashlib
import re

class UserAuth:
    def __init__(self, parent, db_manager):
        self.parent = parent
        self.db_manager = db_manager
        
        # Create necessary tables if they don't exist
        self.create_users_table()
    
    def create_users_table(self):
        """Create users table in database if it doesn't exist"""
        self.db_manager.cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT NOT NULL,
            email TEXT,
            date_joined TEXT DEFAULT CURRENT_TIMESTAMP,
            tests_completed INTEGER DEFAULT 0,
            avg_wpm REAL DEFAULT 0,
            avg_accuracy REAL DEFAULT 0
        )
        ''')
        self.db_manager.conn.commit()
    
    def hash_password(self, password):
        """Hash a password for security"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def validate_email(self, email):
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        return re.match(pattern, email) is not None
    
    def show_login(self):
        """Display the login dialog"""
        login_window = tk.Toplevel(self.parent)
        login_window.title("Login")
        login_window.geometry("400x300")
        login_window.configure(bg="#323437")
        login_window.transient(self.parent)
        login_window.grab_set()
        
        # Title
        title_label = tk.Label(login_window, text="User Login", 
                            font=("Courier", 18, "bold"), bg="#323437", fg="#e2b714")
        title_label.pack(pady=20)
        
        # Form frame
        form_frame = tk.Frame(login_window, bg="#323437")
        form_frame.pack(pady=10)
        
        # Username
        username_label = tk.Label(form_frame, text="Username:", 
                               font=("Courier", 12), bg="#323437", fg="#d1d0c5")
        username_label.grid(row=0, column=0, sticky='e', padx=10, pady=10)
        
        username_entry = tk.Entry(form_frame, font=("Courier", 12), bg="#2c2e31", fg="#d1d0c5",
                               width=20)
        username_entry.grid(row=0, column=1, padx=10, pady=10)
        
        # Password
        password_label = tk.Label(form_frame, text="Password:", 
                               font=("Courier", 12), bg="#323437", fg="#d1d0c5")
        password_label.grid(row=1, column=0, sticky='e', padx=10, pady=10)
        
        password_entry = tk.Entry(form_frame, font=("Courier", 12), bg="#2c2e31", fg="#d1d0c5",
                               width=20, show="*")
        password_entry.grid(row=1, column=1, padx=10, pady=10)
        
        # Buttons frame
        buttons_frame = tk.Frame(login_window, bg="#323437")
        buttons_frame.pack(pady=20)
        
        # Login button
        login_button = tk.Button(buttons_frame, text="Login", font=("Courier", 12),
                              bg="#e2b714", fg="#323437", width=10,
                              command=lambda: self.login(username_entry.get(), password_entry.get(), login_window))
        login_button.grid(row=0, column=0, padx=10)
        
        # Cancel button
        cancel_button = tk.Button(buttons_frame, text="Cancel", font=("Courier", 12),
                               bg="#d1d0c5", fg="#323437", width=10,
                               command=login_window.destroy)
        cancel_button.grid(row=0, column=1, padx=10)
        
        # Register link
        register_label = tk.Label(login_window, text="Don't have an account? Register here", 
                               font=("Courier", 10, "underline"), bg="#323437", fg="#d1d0c5",
                               cursor="hand2")
        register_label.pack(pady=10)
        register_label.bind("<Button-1>", lambda e: self.switch_to_register(login_window))
    
    def show_register(self):
        """Display the registration dialog"""
        register_window = tk.Toplevel(self.parent)
        register_window.title("Register")
        register_window.geometry("400x350")
        register_window.configure(bg="#323437")
        register_window.transient(self.parent)
        register_window.grab_set()
        
        # Title
        title_label = tk.Label(register_window, text="Create Account", 
                            font=("Courier", 18, "bold"), bg="#323437", fg="#e2b714")
        title_label.pack(pady=20)
        
        # Form frame
        form_frame = tk.Frame(register_window, bg="#323437")
        form_frame.pack(pady=10)
        
        # Username
        username_label = tk.Label(form_frame, text="Username:", 
                               font=("Courier", 12), bg="#323437", fg="#d1d0c5")
        username_label.grid(row=0, column=0, sticky='e', padx=10, pady=10)
        
        username_entry = tk.Entry(form_frame, font=("Courier", 12), bg="#2c2e31", fg="#d1d0c5",
                               width=20)
        username_entry.grid(row=0, column=1, padx=10, pady=10)
        
        # Email
        email_label = tk.Label(form_frame, text="Email:", 
                            font=("Courier", 12), bg="#323437", fg="#d1d0c5")
        email_label.grid(row=1, column=0, sticky='e', padx=10, pady=10)
        
        email_entry = tk.Entry(form_frame, font=("Courier", 12), bg="#2c2e31", fg="#d1d0c5",
                            width=20)
        email_entry.grid(row=1, column=1, padx=10, pady=10)
        
        # Password
        password_label = tk.Label(form_frame, text="Password:", 
                               font=("Courier", 12), bg="#323437", fg="#d1d0c5")
        password_label.grid(row=2, column=0, sticky='e', padx=10, pady=10)
        
        password_entry = tk.Entry(form_frame, font=("Courier", 12), bg="#2c2e31", fg="#d1d0c5",
                               width=20, show="*")
        password_entry.grid(row=2, column=1, padx=10, pady=10)
        
        # Confirm Password
        confirm_label = tk.Label(form_frame, text="Confirm:", 
                              font=("Courier", 12), bg="#323437", fg="#d1d0c5")
        confirm_label.grid(row=3, column=0, sticky='e', padx=10, pady=10)
        
        confirm_entry = tk.Entry(form_frame, font=("Courier", 12), bg="#2c2e31", fg="#d1d0c5",
                              width=20, show="*")
        confirm_entry.grid(row=3, column=1, padx=10, pady=10)
        
        # Buttons frame
        buttons_frame = tk.Frame(register_window, bg="#323437")
        buttons_frame.pack(pady=20)
        
        # Register button
        register_button = tk.Button(buttons_frame, text="Register", font=("Courier", 12),
                                 bg="#e2b714", fg="#323437", width=10,
                                 command=lambda: self.register(
                                     username_entry.get(), 
                                     email_entry.get(),
                                     password_entry.get(), 
                                     confirm_entry.get(), 
                                     register_window))
        register_button.grid(row=0, column=0, padx=10)
        
        # Cancel button
        cancel_button = tk.Button(buttons_frame, text="Cancel", font=("Courier", 12),
                               bg="#d1d0c5", fg="#323437", width=10,
                               command=register_window.destroy)
        cancel_button.grid(row=0, column=1, padx=10)
        
        # Login link
        login_label = tk.Label(register_window, text="Already have an account? Login here", 
                            font=("Courier", 10, "underline"), bg="#323437", fg="#d1d0c5",
                            cursor="hand2")
        login_label.pack(pady=10)
        login_label.bind("<Button-1>", lambda e: self.switch_to_login(register_window))
    
    def login(self, username, password, window):
        """Process login attempt"""
        if not username or not password:
            messagebox.showerror("Error", "Username and password are required")
            return
        
        # Get user from database
        self.db_manager.cursor.execute(
            "SELECT * FROM users WHERE username = ?", 
            (username,)
        )
        user = self.db_manager.cursor.fetchone()
        
        # Check if user exists and password matches
        if user and user[1] == self.hash_password(password):
            self.parent.current_user = username
            messagebox.showinfo("Login Successful", f"Welcome back, {username}!")
            window.destroy()
            # Show the typing test interface
            self.parent.start_test("time", 30)
        else:
            messagebox.showerror("Login Failed", "Invalid username or password")
    
    def register(self, username, email, password, confirm_password, window):
        """Process registration attempt"""
        # Validate inputs
        if not username or not email or not password or not confirm_password:
            messagebox.showerror("Error", "All fields are required")
            return
        
        if password != confirm_password:
            messagebox.showerror("Error", "Passwords do not match")
            return
        
        if not self.validate_email(email):
            messagebox.showerror("Error", "Invalid email format")
            return
        
        if len(password) < 6:
            messagebox.showerror("Error", "Password must be at least 6 characters long")
            return
        
        # Check if username already exists
        self.db_manager.cursor.execute(
            "SELECT * FROM users WHERE username = ?", 
            (username,)
        )
        if self.db_manager.cursor.fetchone():
            messagebox.showerror("Error", "Username already exists")
            return
        
        # Insert new user into database
        try:
            hashed_password = self.hash_password(password)
            self.db_manager.cursor.execute(
                "INSERT INTO users (username, password, email) VALUES (?, ?, ?)",
                (username, hashed_password, email)
            )
            self.db_manager.conn.commit()
            
            self.parent.current_user = username
            messagebox.showinfo("Registration Successful", f"Welcome, {username}!")
            window.destroy()
            # Show the typing test interface
            self.parent.start_test("time", 30)
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Error creating account: {e}")
    
    def switch_to_register(self, window):
        """Close login window and open registration window"""
        window.destroy()
        self.show_register()
    
    def switch_to_login(self, window):
        """Close registration window and open login window"""
        window.destroy()
        self.show_login()
    
    def logout(self):
        """Log out the current user"""
        if self.parent.current_user:
            self.parent.current_user = None
            messagebox.showinfo("Logout", "You have been logged out")
            self.parent.show_welcome_screen()
        else:
            messagebox.showinfo("Error", "No user is currently logged in")
    
    def get_user_stats(self, username):
        """Get user statistics from database"""
        self.db_manager.cursor.execute(
            "SELECT tests_completed, avg_wpm, avg_accuracy FROM users WHERE username = ?",
            (username,)
        )
        return self.db_manager.cursor.fetchone()
    
    def update_user_stats(self, username, wpm, accuracy):
        """Update user statistics after a test"""
        # Get current stats
        self.db_manager.cursor.execute(
            "SELECT tests_completed, avg_wpm, avg_accuracy FROM users WHERE username = ?",
            (username,)
        )
        stats = self.db_manager.cursor.fetchone()
        
        if stats:
            tests_completed, avg_wpm, avg_accuracy = stats
            tests_completed += 1
            
            # Calculate new averages
            new_avg_wpm = ((avg_wpm * (tests_completed - 1)) + wpm) / tests_completed
            new_avg_accuracy = ((avg_accuracy * (tests_completed - 1)) + accuracy) / tests_completed
            
            # Update user stats
            self.db_manager.cursor.execute(
                """UPDATE users 
                   SET tests_completed = ?, avg_wpm = ?, avg_accuracy = ? 
                   WHERE username = ?""",
                (tests_completed, new_avg_wpm, new_avg_accuracy, username)
            )
            self.db_manager.conn.commit()
            
    def show_profile(self):
        """Display user profile and stats"""
        if not self.parent.current_user:
            messagebox.showinfo("Login Required", "Please log in to view your profile")
            return
            
        # Get user stats
        stats = self.get_user_stats(self.parent.current_user)
        if not stats:
            return
            
        tests_completed, avg_wpm, avg_accuracy = stats
        
        # Create profile window
        profile_window = tk.Toplevel(self.parent)
        profile_window.title("User Profile")
        profile_window.geometry("400x350")
        profile_window.configure(bg="#323437")
        profile_window.transient(self.parent)
        
        # Title
        title_label = tk.Label(profile_window, text=f"Profile: {self.parent.current_user}", 
                            font=("Courier", 18, "bold"), bg="#323437", fg="#e2b714")
        title_label.pack(pady=20)
        
        # Stats frame
        stats_frame = tk.Frame(profile_window, bg="#323437")
        stats_frame.pack(pady=20)
        
        # Tests completed
        tests_label = tk.Label(stats_frame, text=f"Tests Completed: {tests_completed}", 
                            font=("Courier", 14), bg="#323437", fg="#d1d0c5")
        tests_label.pack(pady=5, anchor='w')
        
        # Average WPM
        wpm_label = tk.Label(stats_frame, text=f"Average WPM: {avg_wpm:.1f}", 
                          font=("Courier", 14), bg="#323437", fg="#d1d0c5")
        wpm_label.pack(pady=5, anchor='w')
        
        # Average accuracy
        accuracy_label = tk.Label(stats_frame, text=f"Average Accuracy: {avg_accuracy:.1f}%", 
                               font=("Courier", 14), bg="#323437", fg="#d1d0c5")
        accuracy_label.pack(pady=5, anchor='w')
        
        # Buttons frame
        buttons_frame = tk.Frame(profile_window, bg="#323437")
        buttons_frame.pack(pady=20)
        
        # View progress button
        progress_button = tk.Button(buttons_frame, text="View Progress", font=("Courier", 12),
                                  bg="#e2b714", fg="#323437", width=15,
                                  command=self.parent.show_progress)
        progress_button.grid(row=0, column=0, padx=10, pady=10)
        
        # Change password button
        password_button = tk.Button(buttons_frame, text="Change Password", font=("Courier", 12),
                                 bg="#d1d0c5", fg="#323437", width=15,
                                 command=lambda: self.show_change_password())
        password_button.grid(row=0, column=1, padx=10, pady=10)
        
        # Logout button
        logout_button = tk.Button(buttons_frame, text="Logout", font=("Courier", 12),
                               bg="#d1d0c5", fg="#323437", width=15,
                               command=lambda: [profile_window.destroy(), self.logout()])
        logout_button.grid(row=1, column=0, columnspan=2, padx=10, pady=10)
    
    def show_change_password(self):
        """Display change password dialog"""
        if not self.parent.current_user:
            messagebox.showinfo("Login Required", "Please log in to change your password")
            return
            
        # Create change password window
        password_window = tk.Toplevel(self.parent)
        password_window.title("Change Password")
        password_window.geometry("400x300")
        password_window.configure(bg="#323437")
        password_window.transient(self.parent)
        password_window.grab_set()
        
        # Title
        title_label = tk.Label(password_window, text="Change Password", 
                            font=("Courier", 18, "bold"), bg="#323437", fg="#e2b714")
        title_label.pack(pady=20)
        
        # Form frame
        form_frame = tk.Frame(password_window, bg="#323437")
        form_frame.pack(pady=10)
        
        # Current password
        current_label = tk.Label(form_frame, text="Current Password:", 
                              font=("Courier", 12), bg="#323437", fg="#d1d0c5")
        current_label.grid(row=0, column=0, sticky='e', padx=10, pady=10)
        
        current_entry = tk.Entry(form_frame, font=("Courier", 12), bg="#2c2e31", fg="#d1d0c5",
                              width=20, show="*")
        current_entry.grid(row=0, column=1, padx=10, pady=10)
        
        # New password
        new_label = tk.Label(form_frame, text="New Password:", 
                          font=("Courier", 12), bg="#323437", fg="#d1d0c5")
        new_label.grid(row=1, column=0, sticky='e', padx=10, pady=10)
        
        new_entry = tk.Entry(form_frame, font=("Courier", 12), bg="#2c2e31", fg="#d1d0c5",
                          width=20, show="*")
        new_entry.grid(row=1, column=1, padx=10, pady=10)
        
        # Confirm new password
        confirm_label = tk.Label(form_frame, text="Confirm New:", 
                              font=("Courier", 12), bg="#323437", fg="#d1d0c5")
        confirm_label.grid(row=2, column=0, sticky='e', padx=10, pady=10)
        
        confirm_entry = tk.Entry(form_frame, font=("Courier", 12), bg="#2c2e31", fg="#d1d0c5",
                              width=20, show="*")
        confirm_entry.grid(row=2, column=1, padx=10, pady=10)
        
        # Buttons frame
        buttons_frame = tk.Frame(password_window, bg="#323437")
        buttons_frame.pack(pady=20)
        
        # Change button
        change_button = tk.Button(buttons_frame, text="Change", font=("Courier", 12),
                               bg="#e2b714", fg="#323437", width=10,
                               command=lambda: self.change_password(
                                   current_entry.get(),
                                   new_entry.get(),
                                   confirm_entry.get(),
                                   password_window))
        change_button.grid(row=0, column=0, padx=10)
        
        # Cancel button
        cancel_button = tk.Button(buttons_frame, text="Cancel", font=("Courier", 12),
                               bg="#d1d0c5", fg="#323437", width=10,
                               command=password_window.destroy)
        cancel_button.grid(row=0, column=1, padx=10)
    
    def change_password(self, current_password, new_password, confirm_password, window):
        """Process password change attempt"""
        if not current_password or not new_password or not confirm_password:
            messagebox.showerror("Error", "All fields are required")
            return
        
        if new_password != confirm_password:
            messagebox.showerror("Error", "New passwords do not match")
            return
        
        if len(new_password) < 6:
            messagebox.showerror("Error", "Password must be at least 6 characters long")
            return
        
        # Check current password
        self.db_manager.cursor.execute(
            "SELECT password FROM users WHERE username = ?", 
            (self.parent.current_user,)
        )
        stored_password = self.db_manager.cursor.fetchone()[0]
        
        if stored_password != self.hash_password(current_password):
            messagebox.showerror("Error", "Current password is incorrect")
            return
        
        # Update password
        try:
            hashed_new_password = self.hash_password(new_password)
            self.db_manager.cursor.execute(
                "UPDATE users SET password = ? WHERE username = ?",
                (hashed_new_password, self.parent.current_user)
            )
            self.db_manager.conn.commit()
            
            messagebox.showinfo("Success", "Password changed successfully")
            window.destroy()
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Error changing password: {e}")