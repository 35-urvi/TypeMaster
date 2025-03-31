import os
import pygame
import threading

class SoundManager:
    def __init__(self):
        """Initialize the sound manager"""
        # Initialize pygame mixer for sound playback
        pygame.mixer.init()
        
        # Set default sound enabled status
        self.sound_enabled = True
        
        # Load sound files
        self.sounds = {}
        self.load_sounds()
    
    def load_sounds(self):
        """Load sound effects"""
        # Create sounds directory if it doesn't exist
        if not os.path.exists("sounds"):
            os.makedirs("sounds")
            print("Created 'sounds' directory. Please add sound files to this directory.")
            return
        
        # Try to load key sound
        key_sound_path = os.path.join("sounds", "keypress.mp3")
        if os.path.exists(key_sound_path):
            self.sounds["key"] = pygame.mixer.Sound(key_sound_path)
        else:
            print(f"Key sound file not found at: {key_sound_path}")
        
        # Try to load error sound
        error_sound_path = os.path.join("sounds", "error.mp3")
        if os.path.exists(error_sound_path):
            self.sounds["error"] = pygame.mixer.Sound(error_sound_path)
        
        # Try to load completion sound
        complete_sound_path = os.path.join("sounds", "complete.mp3")
        if os.path.exists(complete_sound_path):
            self.sounds["complete"] = pygame.mixer.Sound(complete_sound_path)
    
    def play_sound(self, sound_name):
        """Play a sound if sound is enabled"""
        if not self.sound_enabled:
            return
        
        if sound_name in self.sounds:
            # Play sound in a separate thread to prevent UI freezing
            threading.Thread(target=self._play_sound_thread, args=(sound_name,)).start()
    
    def _play_sound_thread(self, sound_name):
        """Thread function to play sound"""
        try:
            self.sounds[sound_name].play()
        except Exception as e:
            print(f"Error playing sound {sound_name}: {e}")
    
    def play_key_sound(self):
        """Play key press sound"""
        self.play_sound("key")
    
    def play_error_sound(self):
        """Play error sound"""
        self.play_sound("error")
    
    def play_complete_sound(self):
        """Play test completion sound"""
        self.play_sound("complete")
    
    def toggle_sound(self):
        """Toggle sound on/off"""
        self.sound_enabled = not self.sound_enabled
        return self.sound_enabled