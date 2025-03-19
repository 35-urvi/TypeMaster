import tkinter as tk
from tkinter import ttk
import time
import random
import threading
import sound_manager

class TypingTest:
    def __init__(self, parent_frame, parent_app, mode, value, difficulty, sound_manager, custom_text=None):
        """Initialize typing test interface"""
        self.parent_frame = parent_frame
        self.parent_app = parent_app
        self.mode = mode
        self.value = value
        self.difficulty = difficulty
        self.sound_manager = sound_manager
        self.custom_text = custom_text
        
        # Test state variables
        self.test_text = ""
        self.current_position = 0
        self.test_start_time = 0
        self.test_active = False
        self.test_completed = False
        self.wpm_over_time = []  # For tracking WPM changes during the test
        self.last_update_time = 0
        self.correct_chars = 0
        self.total_chars = 0
        self.errors = 0
        
        # Timer for time-based tests
        self.remaining_time = 0
        self.timer_active = False
        
        # Create test interface
        self.create_interface()
    
    def create_interface(self):
        """Create test interface"""
        # Test info frame
        self.info_frame = tk.Frame(self.parent_frame, bg="#323437")
        self.info_frame.pack(fill=tk.X, pady=10)
        
        # Left info (Mode & Time/Words)
        left_info = tk.Frame(self.info_frame, bg="#323437")
        left_info.pack(side=tk.LEFT, padx=20)
        
        mode_text = self.mode.title()
        if self.mode == "time":
            mode_text += f" - {self.value}s"
        elif self.mode == "words":
            mode_text += f" - {self.value} words"
        
        self.mode_label = tk.Label(left_info, text=mode_text, 
                                 font=("Courier", 12), bg="#323437", fg="#d1d0c5")
        self.mode_label.pack(anchor='w')
        
        if self.mode == "time":
            self.time_label = tk.Label(left_info, text=f"Time: {self.value}s", 
                                     font=("Courier", 12), bg="#323437", fg="#d1d0c5")
            self.time_label.pack(anchor='w')
        elif self.mode == "words":
            self.words_label = tk.Label(left_info, text=f"Words: 0/{self.value}", 
                                      font=("Courier", 12), bg="#323437", fg="#d1d0c5")
            self.words_label.pack(anchor='w')
        
        # Right info (Stats)
        right_info = tk.Frame(self.info_frame, bg="#323437")
        right_info.pack(side=tk.RIGHT, padx=20)
        
        self.wpm_label = tk.Label(right_info, text="WPM: 0", 
                                font=("Courier", 12), bg="#323437", fg="#d1d0c5")
        self.wpm_label.pack(anchor='e')
        
        self.accuracy_label = tk.Label(right_info, text="Accuracy: 100.0%", 
                                     font=("Courier", 12), bg="#323437", fg="#d1d0c5")
        self.accuracy_label.pack(anchor='e')
        
        # Text display frame
        self.text_frame = tk.Frame(self.parent_frame, bg="#323437")
        self.text_frame.pack(fill=tk.BOTH, expand=True, pady=20)
        
        # Text to type (read-only)
        self.text_display = tk.Text(self.text_frame, font=("Courier", 18), 
                                  bg="#2c2e31", fg="#d1d0c5", wrap=tk.WORD, 
                                  height=8, width=60, padx=10, pady=10, 
                                  state="disabled")
        self.text_display.pack(fill=tk.BOTH, expand=True)
        
        # Configure tags for text coloring
        self.text_display.tag_configure("correct", foreground="#a3be8c")
        self.text_display.tag_configure("error", foreground="#bf616a", background="#802020")
        
        # Input frame
        self.input_frame = tk.Frame(self.parent_frame, bg="#323437")
        self.input_frame.pack(fill=tk.X, pady=20)
        
        # Input field
        self.input_field = tk.Entry(self.input_frame, font=("Courier", 16), 
                                  bg="#2c2e31", fg="#d1d0c5", width=50, 
                                  insertbackground="#d1d0c5")
        self.input_field.pack(fill=tk.X, padx=20)
        
        # Start/Restart text
        self.start_label = tk.Label(self.input_frame, text="Type to start...", 
                                  font=("Courier", 12), bg="#323437", fg="#d1d0c5")
        self.start_label.pack(pady=10)
        
        # Bind input field events
        self.input_field.bind("<Key>", self.on_key_press)
        self.input_field.bind("<KeyRelease>", self.check_input)
        # self.input_field.bind("<space>", self.on_space)
        self.input_field.bind("<BackSpace>", self.on_backspace)
        self.input_field.bind("<Escape>", self.cancel_test)
        
        # Focus the input field
        self.input_field.focus_set()
    
    def generate_test_text(self):
        """Generate text for the test based on mode and difficulty"""
        if self.custom_text:
            return self.custom_text
        
        if self.mode == "words" or self.mode == "time":
            db_manager = self.parent_app.db_manager
            words = db_manager.get_words(self.difficulty)
            
            if not words:
                # Fallback word list if database is empty
                words = ["the", "be", "to", "of", "and", "a", "in", "that", "have", "I", 
                       "it", "for", "not", "on", "with", "he", "as", "you", "do", "at"]
            
            # For word mode, select exactly the specified number of words
            if self.mode == "words":
                selected_words = random.sample(words, min(self.value, len(words)))
                if len(selected_words) < self.value:
                    # If we don't have enough unique words, repeat some
                    remaining = self.value - len(selected_words)
                    selected_words.extend(random.choices(words, k=remaining))
                return " ".join(selected_words)
            
            # For time mode, generate more text than needed
            elif self.mode == "time":
                # Generate more words for longer tests
                word_count = min(self.value * 5, len(words) * 3)  # Approx. 1 word per second × 5
                selected_words = random.choices(words, k=word_count)
                return " ".join(selected_words)
        
        elif self.mode == "paragraph":
            db_manager = self.parent_app.db_manager
            return db_manager.get_paragraph(self.difficulty)
        
        # Default fallback text
        return "The quick brown fox jumps over the lazy dog."
    
    def start(self):
        """Start the typing test"""
        # Generate test text
        self.test_text = self.generate_test_text()
        
        # Display text
        self.text_display.config(state="normal")
        self.text_display.delete("1.0", tk.END)
        self.text_display.insert(tk.END, self.test_text)
        self.text_display.config(state="disabled")
        
        # Reset state variables
        self.current_position = 0
        self.test_completed = False
        self.correct_chars = 0
        self.total_chars = 0
        self.errors = 0
        self.wpm_over_time = []
        
        # If time mode, initialize the countdown
        if self.mode == "time":
            self.remaining_time = self.value
            self.time_label.config(text=f"Time: {self.remaining_time}s")
    
    def on_key_press(self, event):
        """Handle key press event"""
        # Ignore special keys and modified keys
        if event.keysym in ["Shift_L", "Shift_R", "Control_L", "Control_R", "Alt_L", "Alt_R"]:
            return
        
        # Start test on first keypress
        if not self.test_active:
            self.test_active = True
            self.test_start_time = time.time()
            self.last_update_time = self.test_start_time
            
            if self.mode == "time":
                self.timer_active = True
                self.update_timer()
                self.start_label.config(text="Test in progress...")
        
        # Play key sound if enabled
        self.sound_manager.play_key_sound()
    
    def on_space(self, event):
        """Handle space bar press - just for tracking word count"""
        if self.test_active and not self.test_completed:
            # Check if test is complete (for word mode)
            if self.mode == "words":
                current_text = self.input_field.get()
                word_count = len(current_text.split())
                if word_count >= self.value:
                    self.complete_test()
            return "break"  # Allow the space to be added to input
    
    def on_backspace(self, event):
        """Handle backspace key"""
        if self.test_active and not self.test_completed:
            # Just update the display, stats are updated in check_input
            return  # Allow normal backspace behavior

    def check_input(self, event=None):
        """Update display based on current input and calculate accuracy"""
        if self.test_active and not self.test_completed:
            current_text = self.input_field.get()

            # Enable text modification in UI
            self.text_display.config(state="normal")
            self.text_display.delete("1.0", tk.END)
            self.text_display.insert(tk.END, self.test_text)

            # Reset character counters
            self.correct_chars = 0
            self.total_chars = len(current_text)  # Track total typed characters

            # Apply character-by-character highlighting
            for i, char in enumerate(current_text):
                if i < len(self.test_text):
                    expected_char = self.test_text[i]
                    if char == expected_char:
                        self.correct_chars += 1  # Correct character
                        self.text_display.tag_add("correct", f"1.{i}", f"1.{i+1}")
                    else:
                        self.text_display.tag_add("error", f"1.{i}", f"1.{i+1}")

            # Update accuracy and WPM
            self.update_stats()

            # Disable text modification after updating UI
            self.text_display.config(state="disabled")

    
    def calculate_stats(self, current_text):
        """Calculate stats based on current input"""
        # Reset counters
        self.correct_chars = 0
        self.errors = 0
        self.total_chars = len(current_text)
        
        # Count correct characters and errors
        for i, char in enumerate(current_text):
            if i < len(self.test_text):
                if char == self.test_text[i]:
                    self.correct_chars += 1
                else:
                    self.errors += 1
        
        # Play error sound if needed
        if self.errors > 0:
            self.sound_manager.play_error_sound()
        
        # Update stats display
        self.update_stats()
    
    def update_stats(self):
        """Update WPM and accuracy statistics"""
        if not self.test_active or self.test_completed:
            return

        # Calculate elapsed time in minutes
        current_time = time.time()
        elapsed_time = (current_time - self.test_start_time) / 60.0  # Convert to minutes

        # WPM Calculation: Count correct words typed
        words_typed = len(self.input_field.get().split())  # Count words typed
        wpm = words_typed / elapsed_time if elapsed_time > 0 else 0

        # Accuracy Calculation: Correct characters / Total characters
        accuracy = 100.0
        if self.total_chars > 0:
            accuracy = (self.correct_chars / self.total_chars) * 100.0

        # Update UI labels
        self.wpm_label.config(text=f"WPM: {wpm:.1f}")
        self.accuracy_label.config(text=f"Accuracy: {accuracy:.1f}%")

        # Record WPM over time (every second)
        if current_time - self.last_update_time >= 1.0:
            self.wpm_over_time.append(wpm)
            self.last_update_time = current_time

    
    def update_timer(self):
        """Update timer for time-based tests"""
        if self.timer_active and self.remaining_time > 0:
            self.remaining_time -= 1
            self.time_label.config(text=f"Time: {self.remaining_time}s")
            
            # Schedule next update
            if self.remaining_time > 0:
                self.parent_app.after(1000, self.update_timer)
            else:
                self.complete_test()
    
    def complete_test(self):
        """Complete the test and show results"""
        if self.test_completed:
            return

        # Add this near the beginning of the complete_test method
        self.sound_manager.play_complete_sound()

        self.test_completed = True
        self.test_active = False
        self.timer_active = False
        
        # Calculate final stats
        test_end_time = time.time()
        test_duration = test_end_time - self.test_start_time
        
        # Calculate WPM
        if test_duration > 0:
            wpm = (self.total_chars / 5) / (test_duration / 60.0)
        else:
            wpm = 0
        
        # Calculate accuracy
        accuracy = 100.0
        if self.total_chars > 0:
            accuracy = (self.correct_chars / self.total_chars) * 100.0
        
        # Save results
        results = {
            "mode": self.mode,
            "value": self.value,
            "difficulty": self.difficulty,
            "wpm": wpm,
            "accuracy": accuracy,
            "errors": self.errors,
            "correct_chars": self.correct_chars,
            "total_chars": self.total_chars,
            "test_duration": test_duration,
            "wpm_over_time": self.wpm_over_time
        }
        
        # Pass results to parent app
        self.parent_app.save_results(results)
    
    def cancel_test(self, event=None):
        """Cancel the current test"""
        if self.test_active:
            self.test_active = False
            self.timer_active = False
            self.parent_app.show_welcome_screen()
        return "break"  # Prevent default behavior