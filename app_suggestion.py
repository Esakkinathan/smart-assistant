# import os
# import json
# import platform
# import psutil
# import time
# from datetime import datetime, timedelta
# import logging

# class AppSuggestionTracker:
#     def __init__(self, log_dir='app_logs', max_days=5):
#         """
#         Initialize the App Suggestion Tracker
        
#         :param log_dir: Directory to store app logs
#         :param max_days: Number of days to keep app usage records
#         """
#         self.log_dir = log_dir
#         self.max_days = max_days
        
#         # Create log directory if it doesn't exist
#         os.makedirs(log_dir, exist_ok=True)
        
#         # Setup logging
#         logging.basicConfig(level=logging.INFO, 
#                             format='%(asctime)s - %(levelname)s: %(message)s')
#         self.logger = logging.getLogger(__name__)
        
#         # Log file paths
#         self.daily_log_path = os.path.join(log_dir, 'daily_app_usage.json')
#         self.system_boot_log_path = os.path.join(log_dir, 'system_boot_apps.json')
        
#     def get_running_apps(self, duration_minutes=10):
#         """
#         Get apps running in the first 10 minutes after system boot
        
#         :param duration_minutes: Duration to track apps (default 10)
#         :return: Dictionary of apps with their running time
#         """
#         start_time = time.time()
#         app_usage = {}
        
#         try:
#             # Different methods for different operating systems
#             if platform.system() == "Windows":
#                 from psutil import Process
#                 for proc in psutil.process_iter(['pid', 'name', 'create_time']):
#                     try:
#                         # Check if process started after system boot
#                         if time.time() - proc.info['create_time'] <= duration_minutes * 60:
#                             app_name = proc.info['name']
#                             app_usage[app_name] = app_usage.get(app_name, 0) + 1
#                     except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
#                         pass
            
#             elif platform.system() == "Linux":
#                 # Similar approach for Linux, might need adjustment based on specific distribution
#                 for proc in psutil.process_iter(['pid', 'name', 'create_time']):
#                     try:
#                         if time.time() - proc.info['create_time'] <= duration_minutes * 60:
#                             app_name = proc.info['name']
#                             app_usage[app_name] = app_usage.get(app_name, 0) + 1
#                     except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
#                         pass
            
#             elif platform.system() == "Darwin":  # macOS
#                 # macOS specific process tracking
#                 for proc in psutil.process_iter(['pid', 'name', 'create_time']):
#                     try:
#                         if time.time() - proc.info['create_time'] <= duration_minutes * 60:
#                             app_name = proc.info['name']
#                             app_usage[app_name] = app_usage.get(app_name, 0) + 1
#                     except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
#                         pass
            
#             return app_usage
        
#         except Exception as e:
#             self.logger.error(f"Error tracking apps: {e}")
#             return {}
    
#     def log_daily_apps(self, apps):
#         """
#         Log daily app usage with timestamp
        
#         :param apps: Dictionary of apps and their usage count
#         """
#         try:
#             # Load existing logs
#             if os.path.exists(self.daily_log_path):
#                 with open(self.daily_log_path, 'r') as f:
#                     logs = json.load(f)
#             else:
#                 logs = {}
            
#             # Get current date
#             current_date = datetime.now().strftime('%Y-%m-%d')
#             current_day = datetime.now().strftime('%A')
            
#             # Add today's log
#             logs[current_date] = {
#                 'day': current_day,
#                 'apps': apps
#             }
            
#             # Remove logs older than max_days
#             cutoff_date = (datetime.now() - timedelta(days=self.max_days)).strftime('%Y-%m-%d')
#             logs = {k: v for k, v in logs.items() if k >= cutoff_date}
            
#             # Save updated logs
#             with open(self.daily_log_path, 'w') as f:
#                 json.dump(logs, f, indent=4)
            
#             self.logger.info(f"Logged apps for {current_date}")
        
#         except Exception as e:
#             self.logger.error(f"Error logging daily apps: {e}")
    
#     def suggest_apps(self):
#         """
#         Suggest apps based on historical usage
        
#         :return: List of suggested apps
#         """
#         try:
#             # Load logs
#             with open(self.daily_log_path, 'r') as f:
#                 logs = json.load(f)
            
#             current_day = datetime.now().strftime('%A')
#             current_time = datetime.now().hour
            
#             # Filter logs for the same day of the week
#             day_logs = [log for log in logs.values() if log['day'] == current_day]
            
#             # If no logs for this day, use all available logs
#             if not day_logs:
#                 day_logs = list(logs.values())
            
#             # Aggregate app suggestions
#             app_suggestions = {}
#             for log in day_logs:
#                 for app, count in log['apps'].items():
#                     app_suggestions[app] = app_suggestions.get(app, 0) + count
            
#             # Sort suggestions by frequency
#             sorted_suggestions = sorted(app_suggestions.items(), key=lambda x: x[1], reverse=True)
            
#             return [app for app, _ in sorted_suggestions[:5]]  # Top 5 suggestions
        
#         except Exception as e:
#             self.logger.error(f"Error suggesting apps: {e}")
#             return []
    
#     def track_system_boot_apps(self):
#         """
#         Track and log apps opened during system boot
#         """
#         boot_apps = self.get_running_apps()
        
#         try:
#             # Log boot apps
#             with open(self.system_boot_log_path, 'w') as f:
#                 json.dump({
#                     'timestamp': datetime.now().isoformat(),
#                     'apps': boot_apps
#                 }, f, indent=4)
            
#             # Log to daily log as well
#             self.log_daily_apps(boot_apps)
            
#             return boot_apps
        
#         except Exception as e:
#             self.logger.error(f"Error tracking system boot apps: {e}")
#             return {}

# # Example usage
# if __name__ == "__main__":
#     tracker = AppSuggestionTracker()
    
#     # Track apps on system boot
#     boot_apps = tracker.track_system_boot_apps()
#     print("Apps opened after system boot:", boot_apps)
    
#     # Get app suggestions
#     suggestions = tracker.suggest_apps()
#     print("App Suggestions:", suggestions)
# import os
# import json
# import time
# import psutil
# import signal
# import sys
# import threading
# from datetime import datetime, timedelta

# class AppUsageTracker:
#     def __init__(self, log_dir='app_logs', track_duration=10, interval=1):
#         """
#         Initialize App Usage Tracker
        
#         :param log_dir: Directory to store app logs
#         :param track_duration: Duration to track apps in minutes
#         :param interval: Interval between app checks in seconds
#         """
#         self.log_dir = log_dir
#         self.track_duration = track_duration * 60  # Convert to seconds
#         self.interval = interval
#         self.stop_event = threading.Event()
#         self.app_usage = {}
        
#         # Create log directory if it doesn't exist
#         os.makedirs(log_dir, exist_ok=True)
        
#         # Log file path
#         self.log_file = os.path.join(log_dir, f'app_usage_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json')
    
#     def get_active_window(self):
#         """
#         Detect the currently active window/application
#         Works across different platforms
#         """
#         try:
#             # For Windows
#             if sys.platform == 'win32':
#                 import win32gui
#                 active_window = win32gui.GetForegroundWindow()
#                 window_title = win32gui.GetWindowText(active_window)
#                 process_name = self._get_process_name_by_window(active_window)
#                 return process_name or window_title
            
#             # For macOS
#             elif sys.platform == 'darwin':
#                 from AppKit import NSWorkspace
#                 active_app = NSWorkspace.sharedWorkspace().activeApplication()
#                 return active_app['NSApplicationName'] if active_app else 'Unknown'
            
#             # For Linux (using xdotool)
#             elif sys.platform.startswith('linux'):
#                 import subprocess
#                 try:
#                     active_window = subprocess.check_output(['xdotool', 'getactivewindow']).decode().strip()
#                     window_name = subprocess.check_output(['xdotool', 'getwindowname', active_window]).decode().strip()
#                     return window_name
#                 except Exception:
#                     return 'Unknown'
            
#             return 'Unknown'
        
#         except Exception as e:
#             print(f"Error detecting active window: {e}")
#             return 'Unknown'
    
#     def _get_process_name_by_window(self, hwnd):
#         """
#         Get process name for a given window handle (Windows specific)
#         """
#         try:
#             import win32process
#             import win32api
            
#             # Get process ID from window
#             _, pid = win32process.GetWindowThreadProcessId(hwnd)
            
#             # Get process name
#             try:
#                 process = psutil.Process(pid)
#                 return process.name()
#             except (psutil.NoSuchProcess, psutil.AccessDenied):
#                 return None
        
#         except ImportError:
#             return None
    
#     def track_apps(self):
#         """
#         Track app usage for specified duration
#         """
#         start_time = time.time()
        
#         print(f"Starting app tracking for {self.track_duration/60} minutes. Press Ctrl+C to stop.")
        
#         try:
#             while not self.stop_event.is_set():
#                 # Check if tracking duration is exceeded
#                 if time.time() - start_time > self.track_duration:
#                     print("\nTracking duration completed.")
#                     break
                
#                 # Get active window/app
#                 active_app = self.get_active_window()
                
#                 # Update app usage count
#                 if active_app and active_app != 'Unknown':
#                     self.app_usage[active_app] = self.app_usage.get(active_app, 0) + 1
                
#                 # Wait for interval
#                 time.sleep(self.interval)
        
#         except KeyboardInterrupt:
#             print("\nTracking stopped by user.")
        
#         finally:
#             self.save_app_usage()
    
#     def save_app_usage(self):
#         """
#         Save app usage data to JSON file
#         """
#         try:
#             # Prepare data
#             usage_data = {
#                 'timestamp': datetime.now().isoformat(),
#                 'duration': self.track_duration,
#                 'apps': self.app_usage
#             }
            
#             # Save to file
#             with open(self.log_file, 'w') as f:
#                 json.dump(usage_data, f, indent=4)
            
#             print(f"\nApp usage saved to {self.log_file}")
#             print("Tracked Apps:")
#             for app, count in sorted(self.app_usage.items(), key=lambda x: x[1], reverse=True):
#                 print(f"{app}: {count} times")
        
#         except Exception as e:
#             print(f"Error saving app usage: {e}")
    
#     def run(self):
#         """
#         Run the app tracker with signal handling
#         """
#         # Setup signal handler for graceful exit
#         signal.signal(signal.SIGINT, self.signal_handler)
        
#         # Start tracking
#         self.track_apps()
    
#     def signal_handler(self, signum, frame):
#         """
#         Handle Ctrl+C signal
#         """
#         print("\nReceived interrupt signal. Stopping tracking...")
#         self.stop_event.set()
#         self.save_app_usage()
#         sys.exit(0)

# def main():
#     # Create tracker instance
#     tracker = AppUsageTracker(track_duration=10)  # 10 minutes tracking
    
#     # Run the tracker
#     tracker.run()

# if __name__ == "__main__":
#     main()

import os
import json
import time
import psutil
import signal
import sys
import threading
from datetime import datetime

class UbuntuAppUsageTracker:
    def __init__(self, log_dir='app_logs', track_duration=10, interval=1):
        """
        Initialize App Usage Tracker for Ubuntu
        
        :param log_dir: Directory to store app logs
        :param track_duration: Duration to track apps in minutes
        :param interval: Interval between app checks in seconds
        """
        self.log_dir = log_dir
        self.track_duration = track_duration * 60  # Convert to seconds
        self.interval = interval
        self.stop_event = threading.Event()
        self.app_usage = {}
        
        # Create log directory if it doesn't exist
        os.makedirs(log_dir, exist_ok=True)
        
        # Log file path
        self.log_file = os.path.join(log_dir, f'app_usage_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json')
    
    def get_active_window_ubuntu(self):
        """
        Detect active window on Ubuntu using multiple methods
        """
        try:
            # Method 1: Using xdotool (most reliable for Ubuntu)
            import subprocess
            
            try:
                # Get active window ID
                window_id_output = subprocess.check_output(['xdotool', 'getactivewindow'], stderr=subprocess.DEVNULL)
                
                # Get window name
                window_name_output = subprocess.check_output(['xdotool', 'getwindowname', window_id_output.strip()], stderr=subprocess.DEVNULL)
                
                # Decode and clean the window name
                window_name = window_name_output.decode('utf-8').strip()
                
                return window_name
            except subprocess.CalledProcessError:
                pass
            
            # Method 2: Using ps and top processes
            try:
                # Get top processes with window information
                top_processes = subprocess.check_output(['ps', 'aux'], stderr=subprocess.DEVNULL)
                top_processes_decoded = top_processes.decode('utf-8').splitlines()
                
                # Find first process with a GUI-related name
                for process in top_processes_decoded:
                    if any(gui_app in process.lower() for gui_app in ['gnome', 'x11', 'desktop', 'chrome', 'firefox', 'terminal']):
                        return process.split()[-1]
            except subprocess.CalledProcessError:
                pass
            
            # Method 3: psutil process detection
            for proc in psutil.process_iter(['pid', 'name', 'exe']):
                try:
                    # Check for GUI-related processes
                    if proc.info['name'] and any(app in proc.info['name'].lower() for app in [
                        'gnome', 'x11', 'chrome', 'firefox', 'terminal', 'code', 'slack'
                    ]):
                        return proc.info['name']
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            return 'Unknown'
        
        except Exception as e:
            print(f"Error detecting active window: {e}")
            return 'Unknown'
    
    def track_apps(self):
        """
        Track app usage for specified duration
        """
        start_time = time.time()
        
        print(f"Starting app tracking for {self.track_duration/60} minutes. Press Ctrl+C to stop.")
        
        try:
            while not self.stop_event.is_set():
                # Check if tracking duration is exceeded
                if time.time() - start_time > self.track_duration:
                    print("\nTracking duration completed.")
                    break
                
                # Get active window/app
                active_app = self.get_active_window_ubuntu()
                
                # Update app usage count
                if active_app and active_app != 'Unknown':
                    # Clean and normalize app name
                    clean_app_name = active_app.split()[0] if active_app else 'Unknown'
                    self.app_usage[clean_app_name] = self.app_usage.get(clean_app_name, 0) + 1
                
                # Wait for interval
                time.sleep(self.interval)
        
        except KeyboardInterrupt:
            print("\nTracking stopped by user.")
        
        finally:
            self.save_app_usage()
    
    def save_app_usage(self):
        """
        Save app usage data to JSON file
        """
        try:
            # Prepare data
            usage_data = {
                'timestamp': datetime.now().isoformat(),
                'duration': self.track_duration,
                'apps': self.app_usage
            }
            
            # Save to file
            with open(self.log_file, 'w') as f:
                json.dump(usage_data, f, indent=4)
            
            print(f"\nApp usage saved to {self.log_file}")
            print("Tracked Apps:")
            for app, count in sorted(self.app_usage.items(), key=lambda x: x[1], reverse=True):
                print(f"{app}: {count} times")
        
        except Exception as e:
            print(f"Error saving app usage: {e}")
    
    def run(self):
        """
        Run the app tracker with signal handling
        """
        # Setup signal handler for graceful exit
        signal.signal(signal.SIGINT, self.signal_handler)
        
        # Start tracking
        self.track_apps()
    
    def signal_handler(self, signum, frame):
        """
        Handle Ctrl+C signal
        """
        print("\nReceived interrupt signal. Stopping tracking...")
        self.stop_event.set()
        self.save_app_usage()
        sys.exit(0)

def main():
    # Create tracker instance
    tracker = UbuntuAppUsageTracker(track_duration=10)  # 10 minutes tracking
    
    # Run the tracker
    tracker.run()

if __name__ == "__main__":
    main()