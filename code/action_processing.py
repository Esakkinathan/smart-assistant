import subprocess
import time
import os
import webbrowser
import geocoder
import re
import pyautogui
from datetime import datetime
import random
import requests
import re
import psutil

class ActionProcessor:
    TIME_TEMPLATES = [
    "The current time is {hour_24} hour, {minute} minutes, and {second} seconds",
    "It is now {hour_24} hours and {minute} minutes",
    "The time is {hour_12} {am_pm}, and {minute} minutes past the hour",
    "Right now, it is {hour_12} {am_pm}",
    "It's about {hour_12} {am_pm}, with {minute} minutes past",
    "The clock says {hour_12} {am_pm} and {minute} minutes",
    "Currently, it is {hour_12} hours and {minute} minutes in the {am_pm_lower}",
    "We are at {hour_12} {am_pm}, and the time is {minute} minutes past",
    "The exact time is {hour_12} {am_pm}, {minute} minutes, and {second} seconds",
    "Good {greeting}, the time is {hour_12} {am_pm} and {minute} minutes"
    ]
    DATE_TEMPLATES = [
    "{month_name} {day_of_month}, {year_simple}",
    "The {day_of_month} of {month_name}, {year_conversational}",
    "{day_of_month} {month_name}, {year_simple}",
    "The date is {month_name} {day_of_month}, {year_conversational}",
    "{month_name} {day_of_month} in the year {year_simple}",
    ]
    DAY_TEMPLATES = [
    "Today is {day_name}.",
    "It's a beautiful {day_name}.",
    "The day today is {day_name}.",
    "It's {day_name}, a great day!",
    "Today we are on {day_name}.",
    ]
    TIMER_TEMPLATES = [
    'notify-send "Timer Done" "Your timer is up!" && paplay /usr/share/sounds/freedesktop/stereo/complete.oga',
    'notify-send "Alert" "Time is up!" && paplay /usr/share/sounds/freedesktop/stereo/complete.oga',
    'notify-send "Time Completed" "Your duration ended" && paplay /usr/share/sounds/freedesktop/stereo/complete.oga',
    'notify-send "Reminder" "Your time is done!" && paplay /usr/share/sounds/freedesktop/stereo/complete.oga',
    'notify-send "Time Up" "The timer has ended" && paplay /usr/share/sounds/freedesktop/stereo/complete.oga',
    'notify-send "Notification" "Your time is over!" && paplay /usr/share/sounds/freedesktop/stereo/complete.oga',
    'notify-send "Alert" "Timer complete!" && paplay /usr/share/sounds/freedesktop/stereo/complete.oga',
    'notify-send "Done!" "The timer is up!" && paplay /usr/share/sounds/freedesktop/stereo/complete.oga',
    'notify-send "Time Alert" "Your timer has finished!" && paplay /usr/share/sounds/freedesktop/stereo/complete.oga',
    'notify-send "Timer Notification" "Time is over, task completed!" && paplay /usr/share/sounds/freedesktop/stereo/complete.oga'
    ]
    def __init__(self):
        self.api_token = "aab6c3009986b4f93b84c771da042250"
        self.weather_key = "87c68cff3601c8697c22b25c7f2f6812"
        self.pipe_file = "./terminal_pipe"

        self.ACTION_MAP = {
        "weather": self.get_weather,
        "time": self.tell_time,
        "date": self.tell_date,
        "day": self.tell_day,
        "news": self.get_news,
        "volume-up": self.increase_volume,
        "volume-down": self.decrease_volume,
        "volume-mute": lambda: self.set_volume(0),
        "volume-unmute": lambda: self.set_volume(100),
        "brightness-up": self.brightness_up,
        "brightness-down": self.brightness_down,
        "brightness-maximum": self.maximum_brightness,
        "lock-screen": self.lock_system,
        "minimize-all-window": self.minimize_all_window,
        "restart": self.restart_system,
        "shutdown": self.shutdown_system,
        "set-theme-dark": self.set_theme_dark,
        "set-theme-light": self.set_theme_light,
        "bluetooth-on": self.set_bluetooth_on,
        "bluetooth-off": self.set_bluetooth_off,
        "turn-night-light-on": self.night_light_on,
        "turn-night-light-off": self.night_light_off,
        }


    def predict_action(self,query):
        if query in self.ACTION_MAP:
            return self.ACTION_MAP[query]()
        if "set-volume" in query:
            return self.set_volume(int(query[11:]))
        if "set-brightness" in query:
            return self.set_brightness(query[19:])
        if "set-timer" in query:            
            return self.set_timer(query)
        if "spotify" in query:
            return self.spotify_search(query[8:])
        if "youtube" in query:
            return self.youtube_search(query[8:])
        if "browser" in query:
            return self.web_search(query[8:])
        if "screenshot" in query:
            return self.capture_screenshot()
        if "sudo snap install" in query:
            self.command_execute(query + ' --classic')
            return "Action executed"
        elif "apt install" in query:
            self.command_execute(query + ' -y')
            return "Action executed"
        else:
            self.command_execute(query)
            return "Action executed"

    def web_search(self,site_name=None):
        site_name=site_name.replace(" ","+")
        web_url=f"https://www.google.com/search?q={site_name}"
        webbrowser.open(web_url)
        return "Search complete. Here’s what I found"

    def youtube_search(self,video_name=None):
        video_name=video_name.replace(' ','+')
        youtube_url=f'https://www.youtube.com/results?search_query={video_name}'
        webbrowser.open(youtube_url)
        return "YouTube is now open. It’s like Netflix, but with more conspiracy theories."
        
    def spotify_search(self,song_name=None):
        song_name=song_name.replace(' ','%20')
        spotify_url=f"https://open.spotify.com/search/{song_name}"
        webbrowser.open(spotify_url)
        return f"{song_name} has been found in the Spotify matrix."
    
    def get_location(self):
        g = geocoder.ip('me')    
        if g.ok:
            latitude = g.latlng[0]
            longitude = g.latlng[1]
            return latitude, longitude
        else:
            return None,None

    def get_weather(self):
        lat, long = self.get_location() 
        if lat is None or long is None:
            return "Internet connection error"
        else:
            key = "87c68cff3601c8697c22b25c7f2f6812"
            url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={long}&appid={key}&units=metric"
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()             
                out = f"Here's the weather report for {data['name']}: Today's temperature is {data['main']['temp']}°C, and the weather is {data['weather'][0]['description']}."
                return out 
            else:
                return "An error occurred, please try again later."

    def get_current_volume(self):
        result = subprocess.run(["amixer", "get", "Master"], capture_output=True, text=True)
        volume = re.search(r'\[([0-9]+)%\]', result.stdout)
        if volume:
            return int(volume.group(1))
        return 0

    def set_volume(self,level):
        level = max(0, min(100, level))
        if 0<=level<=100:
            subprocess.run(["amixer", "sset", "Master", f"{level}%"])
        return f"{level}% volume. Time to crank it up or chill out—your call!"

    def increase_volume(self,step=20):
        current_volume = self.et_current_volume()
        new_volume = current_volume + step
        self.set_volume(new_volume)
        return "All set! The volume is raised to your preference."

    def decrease_volume(self,step=20):
        current_volume = self.get_current_volume()
        new_volume = current_volume - step
        self.set_volume(new_volume)
        return "Got it! The volume is now softer."

    def brightness_up(self):
        subprocess.run(['sudo', 'brightnessctl', 's', '+10%'])
        return "Brightness boosted. Enjoy the clearer screen!"

    def brightness_down(self):
        subprocess.run(['sudo', 'brightnessctl', 's', '10%-'])
        return "Done. The brightness is now lower."

    def set_brightness(self,level):
        subprocess.run(['sudo', 'brightnessctl', 's', f'{level}%'])
        return f"Adjusted the brightness to {level}%."

    def maximum_brightness(self,level):
        subprocess.run(['sudo', 'brightnessctl', 's', '100%'])
        return "The screen brightness is on full now."

    def capture_screenshot(self):
        save_dir = os.path.expanduser('~/Pictures/Screenshot')
        os.makedirs(save_dir, exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'screenshot_{timestamp}.png'
        file_path = os.path.join(save_dir, filename)
        screenshot = pyautogui.screenshot()
        screenshot.save(file_path)
        return "Screenshot successfully taken."
    
    def shutdown_system(self):
        os.system('sudo shutdown')
        return "Your system is shutting down. See you next time."

    def restart_system(self):
        os.system('sudo reboot')
        return "The system is restarting. Hang tight!"

    def lock_system(self):
        os.system('gnome-screensaver-command -l')
        return "Screen locked. Safe and sound, just like your secrets."


    def minimize_all_window(self):
        subprocess.run(["wmctrl", "-k", "on"])
        return "Everything’s minimized. Your desktop’s looking sleek now!"

    def show_desktop(self):
        os.system("xdg-open ~/Downloads")

    def set_theme_dark(self):
        subprocess.run(["gsettings", "set", "org.gnome.desktop.interface", "gtk-theme", "Yaru-dark"])
        subprocess.run(["gsettings", "set", "org.gnome.desktop.interface", "icon-theme", "Yaru-dark"])
        subprocess.run(["gsettings", "set", "org.gnome.desktop.interface", "cursor-theme", "Yaru-dark"])
        subprocess.run(["gsettings", "set", "org.gnome.desktop.interface", "color-scheme", "prefer-dark"])
        return "Engaging the dark theme. The shadows have taken over."


    def set_theme_light(self):
        subprocess.run(["gsettings", "set", "org.gnome.desktop.interface", "gtk-theme", "Yaru-light"])
        subprocess.run(["gsettings", "set", "org.gnome.desktop.interface", "icon-theme", "Yaru-light"])
        subprocess.run(["gsettings", "set", "org.gnome.desktop.interface", "cursor-theme", "Yaru-light"])
        subprocess.run(["gsettings", "set", "org.gnome.desktop.interface", "color-scheme", "prefer-light"])
        return "The theme is now light. Your screen is now as bright as a savior of the city."

    def night_light_on(self):
        os.system("gsettings set org.gnome.settings-daemon.plugins.color night-light-enabled true")
        return"Turning on night light. It’s like your screen just switched to “chill mode.”"

    def night_light_off(self):
        os.system("gsettings set org.gnome.settings-daemon.plugins.color night-light-enabled false")
        return "Night light’s gone. It’s back to that crisp, clear screen we all know."

    def set_wifi_on(self):
        subprocess.run(["nmcli", "radio", "wifi", 'on'])
        return "Your Wi-Fi’s active. Let’s explore the code, shall we?"

    def set_wifi_off(self):
        subprocess.run(["nmcli", "radio", "wifi", 'off'])
        return "I’ve switched off Wi-Fi. You’re offline, agent."

    def set_bluetooth_on(self):
        subprocess.run(['rfkill', 'unblock', 'bluetooth'])
        return "The signal is active. Bluetooth is on and ready to connect."

    def set_bluetooth_off(self):
        subprocess.run(['rfkill', 'block', 'bluetooth'])
        return "Bluetooth deactivated. The link to the outside world is severed."

    def tell_time(self):
        now = datetime.now()
        time_context = {
            "hour_24": now.strftime("%H"),
            "hour_12": now.strftime("%I"),
            "minute": now.strftime("%M"),
            "second": now.strftime("%S"),
            "am_pm": now.strftime("%p"),
            "am_pm_lower": now.strftime("%p").lower(),
            "greeting": "morning" if int(now.strftime("%H")) < 12 else "afternoon" if int(now.strftime("%H")) < 18 else "evening",
        }
        selected_template = random.choice(ActionProcessor.TIME_TEMPLATES)
        text = selected_template.format(**time_context)
        return text

    def tell_date(self):
        # Get the current date
        now = datetime.now()
        date_context = {
            "month_name": now.strftime("%B"), 
            "day_of_month": now.strftime("%d").lstrip('0'), 
            "year_simple": now.strftime("%Y"),
            "year_conversational": f"{now.year // 100} {now.year % 100}",
        }
        selected_format = random.choice(ActionProcessor.DATE_TEMPLATES)
        text = selected_format.format(**date_context)
        return text

    def tell_day(self):
        now = datetime.now()
        day_context = {
            "day_name": now.strftime("%A"),
        }
        selected_format = random.choice(ActionProcessor.DAY_TEMPLATES)
        text = selected_format.format(**day_context)
        return text
        
    def get_news(self):
        url = f"https://gnews.io/api/v4/top-headlines?country=in&lang=en&apikey={self.api_token}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            articles = data.get('articles', [])
            if articles:
                tts_format = "Here are the top headlines for today in India. "
                for idx, article in enumerate(articles[:5]):
                    headline = article['title']
                    if idx == 0:
                        tts_format += f"First, {headline}."
                    elif idx < 4:
                        tts_format += f"Next, {headline}."
                    else:
                        tts_format += f"And finally, {headline}."
                tts_format += "Stay updated with the latest news from India!"
                return tts_format
            else:
                return "Sorry, no news articles are available at the moment."
        else:
            return "Sorry, there was an error fetching the news."

    def parse_time(self,input_text):
        time_pattern = r"(\d+)\s*(second|minute|hour)s?"
        matches = re.findall(time_pattern, input_text)
        time_units = {
            "second": 1,
            "minute": 60,
            "hour": 3600
        }
        total_seconds = 0
        for value, unit in matches:
            total_seconds += int(value) * time_units[unit]
        return total_seconds

    def set_timer(self,input_text):
        time_second=self.parse_time(input_text)
        selected_template = random.choice(ActionProcessor.TIMER_TEMPLATES)
        command = f"sleep {time_second} && {selected_template}"
        subprocess.run(['/usr/bin/gnome-terminal', '--', 'bash', '-c', f'echo "timer set for {time_second} seconds"; {command}; exec bash'])
        return 'Your timer has been set up.'
    
    def check_terminal_process(self):
        """Checks if the terminal process is still running."""
        try:
            # Get all running processes
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                # Check if any process matches terminal-related names like 'gnome-terminal', 'xterm', etc.
                if any(cmd for cmd in proc.info['cmdline'] if 'gnome-terminal' in cmd or 'xterm' in cmd or 'konsole' in cmd):
                    return True
            return False
        except psutil.NoSuchProcess:
            return False

    def command_execute(self,command):
        if not self.terminal_running() or not os.path.exists(self.pipe_file):
            if os.path.exists(self.pipe_file):
                os.remove(self.pipe_file)
            os.mkfifo(self.pipe_file)
            subprocess.Popen(
                ['gnome-terminal', '--', 'bash', '-c', 
                f"tail -f {self.pipe_file} | bash"]
            )
            print("Terminal window opened.")
            time.sleep(1)
        else:
            print("Reusing existing terminal.")
        with open(self.pipe_file, 'w') as pipe:
            pipe.write(f'echo "The command is {command}"; {command};' + '\n')
            print(f"Command sent: {command}")
    def terminal_running(self):
        try:
            result = subprocess.check_output(['ps', '-A', '-o', 'pid,command'])
            if 'tail -f /tmp/terminal_pipe' in result.decode('utf-8'):
                return True
            return False
        except subprocess.CalledProcessError:
            return False

    def cleanup_pipe(self):
        if os.path.exists(self.pipe_file):
            os.remove(self.pipe_file)

ap=ActionProcessor()
ap.predict_action("youtube minutes mystery alien")