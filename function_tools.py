import subprocess
import tkinter.messagebox as mb
import time
import ttkbootstrap as ttb
import socket


class MessageWindow:
    def __init__(self):
        self.root = None
        self.label = None
    def send_message(self,message):
        self.root = ttb.Window(themename="cyborg")
        self.root.title("DARLA")
        self.root.geometry("400x250")
        self.root.attributes('-topmost', True)

        # Center the window
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - 400) // 2
        y = (screen_height - 250) // 2
        self.root.geometry(f"400x250+{x}+{y}")

        # Configure the label
        self.label = ttb.Label(
            self.root,
            text=message,
            font=('Calibri', 16),
            background='black',
            foreground='white',
            wraplength=380,
            anchor='center',
            justify='center'
        )
        self.label.pack(expand=True, padx=10, pady=10)


        self.root.protocol("WM_DELETE_WINDOW", lambda:None)
        self.root.after(4000,self.on_close)
        self.root.mainloop()
    
    def on_close(self):
        if self.root:
            self.root.destroy()
            self.root = None



def get_wifi_details():
    try:
        # Run nmcli command to check Wi-Fi status
        result = subprocess.run(['nmcli', 'radio', 'wifi'], capture_output=True, text=True)
        wifi_status = result.stdout.strip()

        if wifi_status == 'enabled':
            return False
        elif wifi_status == 'disabled':
            return True
        else:
            print("Unable to determine Wi-Fi status.")
    except Exception as e:
        print(f"Error: {e}")

def is_internet_on():
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=3)
        return True
    except OSError:
        return False

def wifi_handler():
    win = MessageWindow()
    if get_wifi_details():
        ask_window = mb.askyesno("DARLA","Your wifi is disabled.\nshall i turn on the wifi")
        if ask_window:
            subprocess.run(['nmcli', 'radio', 'wifi','on'])
            win.send_message(message="I have turned on the wifi.\n You connect with your desired network\n I restart the app after 10 seconds")
            time.sleep(5)
            for _ in range(3):  
                if is_internet_on():
                    return  # Exit function if internet is on
                time.sleep(3)  # Wait before retrying
            win.send_message("Still no internet connection. Please restart after connecting.")
            exit()
        else:
            win.send_message(message="Please connect to the internet.\n After connected, restart the app")
            exit()
    else:
        win.send_message(message="Your system is not connected to the internet.\nPlease connect\n After connected, restart the app")
        exit()
