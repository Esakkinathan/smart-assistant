import subprocess
import time
import os
import webbrowser
import geocoder
import requests
from gtts import gTTS
from playsound import playsound
import re
import pyautogui
from datetime import datetime


def speak(text):
    tts = gTTS(text=text, lang="en", slow=False)
    tts.save("speech.mp3")
    playsound("speech.mp3",)
    os.remove("speech.mp3")

def time_display():
    command = "date"
    subprocess.run(['/usr/bin/gnome-terminal', '--', 'bash', '-c', f'echo "The command is {command}"; {command}; exec bash'])
    time.sleep(10)
    os.system("pkill gnome-terminal")

def web_search(site_name=None):
    site_name=site_name.replace(" ","+")
    web_url=f"https://www.google.com/search?q={site_name}"
    webbrowser.open(url)

def youtube_search(video_name=None):
    video_name=video_name.replace(' ','+')
    youtube_url=f'https://www.youtube.com/results?search_query={video_name}'
    webbrowser.open(youtube_url)
    
def spotify_search(song_name=None):
    song_name=song_name.replace(' ','%20')
    spotify_url=f"https://open.spotify.com/search/{song_name}"
    webbrowser.open(spotify_url)

def get_location():
    g = geocoder.ip('me')    
    if g.ok:
        latitude = g.latlng[0]
        longitude = g.latlng[1]
        return latitude, longitude
    else:
        return None,None

def get_weather():
    lat,long=get_location()
    if lat is None or long is None:
        out("Internet connection error")
    else:
        key="87c68cff3601c8697c22b25c7f2f6812"
        url=f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={long}&appid={key}&units=metric"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json() 
            out=f"Weather report in {data['name']}, todays temperature is {data['main']['temp']} celcius and weather is {data['weather'][0]['description']}"
            speak(out)
        else:
            speak("error occured try later")

def screenshot():
    save_dir = os.path.expanduser('~/Pictures/Screenshot')
    os.makedirs(save_dir, exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'screenshot_{timestamp}.png'
    file_path = os.path.join(save_dir, filename)
    screenshot = pyautogui.screenshot()r_update():

def get_current_volume():
    result = subprocess.run(["amixer", "get", "Master"], capture_output=True, text=True)
    volume = re.search(r'\[([0-9]+)%\]', result.stdout)
    if volume:
        return int(volume.group(1))
    return 0

def set_volume(level):
    level = max(0, min(100, level))
    if 0<=level<=100:
        subprocess.run(["amixer", "sset", "Master", f"{level}%"])

def increase_volume(step=20):
    current_volume = get_current_volume()
    new_volume = current_volume + step
    set_volume(new_volume)

def decrease_volume(step=20):
    current_volume = get_current_volume()
    new_volume = current_volume - step
    set_volume(new_volume)

def capture_screenshot():
    save_dir = os.path.expanduser('~/Pictures/Screenshot')
    os.makedirs(save_dir, exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'screenshot_{timestamp}.png'
    file_path = os.path.join(save_dir, filename)
    screenshot = pyautogui.screenshot()
    screenshot.save(file_path)

def command_execute(cmd):
    subprocess.run(['/usr/bin/gnome-terminal', '--', 'bash', '-c', f'echo "The command is {command}"; {command}; exec bash'])
