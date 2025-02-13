import tkinter as tk
from tkinter import ttk
import threading
import time
import subprocess
import speech_recognition as sr
from pynput import mouse, keyboard
from datetime import datetime
import ttkbootstrap as ttb

class LockPromptWindow:
    def __init__(self, on_response):
        self.window = ttb.Window(themename="cyborg")
        self.window.title("System Lock")
        self.on_response = on_response
        
        # Set window properties
        self.window.geometry("500x400")
        self.window.lift()
        self.window.attributes('-topmost', True)
        
        # Center the window
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        x = (screen_width - 500) // 2
        y = (screen_height - 400) // 2
        self.window.geometry(f"500x400+{x}+{y}")
        
        # Create widgets
        main_frame = ttb.Frame(self.window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        ttb.Label(main_frame, text="Do you want to lock the system?",
                 font=('Calibri', 18, 'bold')).pack(pady=10)
        
        ttb.Label(main_frame, text="1. Click Yes/No\n"
                 "2. Press 'Y' or 'N'\n"
                 "3. Say 'Yes' or 'No'",
                 justify=tk.LEFT).pack(pady=10)
        
        self.timer_label = ttb.Label(main_frame, text="Time remaining: 10s",
                                   font=('Calibri', 10))
        self.timer_label.pack(pady=10)
        
        # Buttons frame
        button_frame = ttb.Frame(main_frame)
        button_frame.pack(pady=20)
        
        ttb.Button(button_frame, text="Yes", 
                  command=lambda: self.on_response(True)).pack(side=tk.LEFT, padx=20)
        ttb.Button(button_frame, text="No",
                  command=lambda: self.on_response(False)).pack(side=tk.LEFT, padx=20)
        
        # Start countdown
        self.remaining_time = 10
        self.update_timer()
    
    def update_timer(self):
        if self.remaining_time > 0:
            self.timer_label.config(text=f"Time remaining: {self.remaining_time}s")
            self.remaining_time -= 1
            self.window.after(1000, self.update_timer)
    
    def close(self):
        self.window.destroy()

class SystemMonitor:
    def __init__(self):
        self.last_activity = datetime.now()
        self.monitoring = True
        self.user_responded = False
        self.lock_system = True
        self.prompt_active = False
        self.prompt_window = None
        
        # Create mouse and keyboard listeners
        self.mouse_listener = mouse.Listener(
            on_move=self.on_activity,
            on_click=self.on_activity,
            on_scroll=self.on_activity)
        
        self.keyboard_listener = keyboard.Listener(
            on_press=self.on_key_press)
    
    def on_activity(self, *args):
        if not self.prompt_active:
            self.last_activity = datetime.now()
            print("\rActivity detected! Timer reset.", end='', flush=True)
    
    def on_key_press(self, key):
        if self.prompt_active:
            try:
                if hasattr(key, 'char'):
                    if key.char.lower() == 'y':
                        self.handle_response(True)
                    elif key.char.lower() == 'n':
                        self.handle_response(False)
            except AttributeError:
                pass
        else:
            self.last_activity = datetime.now()
            print("\rActivity detected! Timer reset.", end='', flush=True)
    
    
    def start_monitoring(self):
        self.mouse_listener.start()
        self.keyboard_listener.start()
        
        print("\nMonitoring started. System will prompt after 20 seconds of inactivity.")
        print("Move mouse or press keys to reset timer.")
        print("\nInactivity timer:")
        
        while self.monitoring:
            if not self.prompt_active:
                inactivity_time = (datetime.now() - self.last_activity).seconds
                print(f"\rInactive time: {inactivity_time} seconds {'=' * inactivity_time}", end='', flush=True)
                
                if inactivity_time >= 20:
                    print("\nInactivity threshold reached!")
                    self.handle_inactivity()
            
            time.sleep(1)
    
    def handle_inactivity(self):
        self.prompt_active = True
        self.user_responded = False
        self.lock_system = True
        
        
        # Create and show prompt window
        self.prompt_window = LockPromptWindow(self.handle_response)
        
        # Wait for 5 seconds
        start_time = time.time()
        while time.time() - start_time < 10 and not self.user_responded:
            self.prompt_window.window.update()
            time.sleep(0.1)
        
        # Close window if still open
        if self.prompt_window:
            self.prompt_window.close()
            self.prompt_window = None
        
        # Handle final decision
        if not self.user_responded:
            print("\nNo response received - locking system")
            self.lock_system = True
            
        if self.lock_system:
            print("\nLocking system...")
            self.lock_screen()
        else:
            print("\nResuming monitoring...")
        
        self.prompt_active = False
        self.last_activity = datetime.now()
    
    def handle_response(self, should_lock):
        if not self.user_responded:
            print(f"\nReceived response: {'lock' if should_lock else 'do not lock'}")
            self.user_responded = True
            self.lock_system = should_lock
            if self.prompt_window:
                self.prompt_window.close()
                self.prompt_window = None
    
    def lock_screen(self):
        subprocess.run(['gnome-screensaver-command', '-l'])
    
    def stop_monitoring(self):
        self.monitoring = False
        self.mouse_listener.stop()
        self.keyboard_listener.stop()

if __name__ == "__main__":
    monitor = SystemMonitor()
    try:
        monitor.start_monitoring()
    except KeyboardInterrupt:
        print("\nMonitoring stopped by user")
        monitor.stop_monitoring()