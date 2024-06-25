import json
import ttkbootstrap as ttk
from tkinter import messagebox, Listbox, Toplevel
import time as time_module
from threading import Thread
from gtts import gTTS
import pygame
import mysql.connector
import io
from datetime import datetime, time


# Database connection
with open('config.json') as config_file:
    config = json.load(config_file)

# Database connection
db = mysql.connector.connect(
    host=config['database']['host'],
    user=config['database']['user'],
    password=config['database']['password'],
    database=config['database']['database'],
    charset=config['database']['charset']
)
cursor = db.cursor()
reminder_list_updated = True
# Function to fetch reminders from the database
def fetch_reminders():
    # Get the Unix timestamps for the start and end of the current day
    start_of_day = datetime.combine(datetime.today(), time.min).timestamp()
    end_of_day = datetime.combine(datetime.today(), time.max).timestamp()

    # Fetch reminders that are scheduled for today
    cursor.execute("SELECT id, text, frequency, time FROM reminders WHERE time >= %s AND time <= %s ORDER BY time ASC", (start_of_day, end_of_day))
    return cursor.fetchall()

# Function to add a reminder to the database
def add_reminder_to_db(reminder_text, reminder_time, frequency):
    cursor.execute("INSERT INTO reminders (text, frequency, time) VALUES (%s, %s, %s)",
                   (reminder_text, frequency, reminder_time))
    db.commit()

# Function to remove a reminder from the database
def remove_reminder_from_db(reminder_id):
    cursor.execute("DELETE FROM reminders WHERE id = %s", (reminder_id,))
    db.commit()

# Function to update reminder time in the database for 24hr frequency
def update_reminder_time(reminder_id, new_time):
    cursor.execute("UPDATE reminders SET time = %s WHERE id = %s", (new_time, reminder_id))
    db.commit()

# Function to set a reminder
def set_reminder():
    reminder_text = reminder_entry.get()
    reminder_time = time_entry.get()
    frequency = frequency_var.get()

    if not reminder_text:
        messagebox.showerror("Invalid Reminder", "Please enter a reminder text.")
        return

    try:
        reminder_hour, reminder_minute = map(int, reminder_time.split(':'))
        reminder_seconds = reminder_hour * 3600 + reminder_minute * 60
    except ValueError:
        messagebox.showerror("Invalid Time Format", "Please enter the time in HH:MM format.")
        return

    current_time = time_module.localtime()
    current_seconds = current_time.tm_hour * 3600 + current_time.tm_min * 60 + current_time.tm_sec

    delay = reminder_seconds - current_seconds
    if delay < 0:
        delay = 0  # If the reminder time is past, set the delay to 0

    # Convert the delay to a Unix timestamp
    reminder_timestamp = int(time_module.time()) + delay

    add_reminder_to_db(reminder_text, reminder_timestamp, frequency)
    update_reminder_list()
    reminder_entry.delete(0, ttk.END)  # Clear the reminder text field after adding
    time_entry.delete(0, ttk.END)
    time_entry.insert(0, time_module.strftime("%H:%M"))  # Set default time to current system time

# Function to play the reminder
def play_reminder(reminder_text, reminder_id, frequency):
    tts = gTTS(reminder_text, lang='en')
    mp3_fp = io.BytesIO()
    tts.write_to_fp(mp3_fp)
    mp3_fp.seek(0)

    pygame.mixer.init()
    pygame.mixer.music.load(mp3_fp, 'mp3')
    pygame.mixer.music.play(-1)  # Loop indefinitely

    show_alert(reminder_text)

    while pygame.mixer.music.get_busy():
        time_module.sleep(1)

    # After reminder is played
    if frequency == 'one-time':
        remove_reminder_from_db(reminder_id)
    elif frequency == '24hr':
        new_time = int(time_module.time()) + 24 * 3600
        update_reminder_time(reminder_id, new_time)

    hide_alert()
    update_reminder_list()  # Update the reminder list after playing the reminder

# Function to mute the reminder sound
def mute_reminder():
    pygame.mixer.music.stop()
    hide_alert()
    update_reminder_list()  # Update the reminder list after muting the reminder

# Function to update the reminder list in the GUI
def update_reminder_list():
    global reminder_list_updated
    reminder_list.delete(0, ttk.END)
    reminders = fetch_reminders()
    for reminder in reminders:
        reminder_time_str = time_module.strftime('%H:%M', time_module.localtime(reminder[3]))
        reminder_list.insert(ttk.END, f"{reminder[1]} at {reminder_time_str} ({reminder[2]})")
    reminder_list_updated = True
# Function to monitor reminders
def monitor_reminders():
    global reminder_list_updated
    while True:
        if reminder_list_updated:
            reminders = fetch_reminders()
            reminder_list_updated = False  # Reset the flag after fetching the reminders
        if reminders:
            next_reminder = reminders[0]
            current_time_seconds = int(datetime.now().timestamp())  # Get current time in local timezone
            print(next_reminder[3], current_time_seconds)
            if next_reminder[3] <= current_time_seconds:
                play_reminder(next_reminder[1], next_reminder[0], next_reminder[2])
                if next_reminder[2] == 'one-time':
                    remove_reminder_from_db(next_reminder[0])
                elif next_reminder[2] == '24hr':
                    new_time = int(datetime.now().timestamp()) + 24 * 3600
                    update_reminder_time(next_reminder[0], new_time)
        time_module.sleep(1)  # Check every second

# Function to show alert message
def show_alert(reminder_text):
    global alert_window
    alert_window = Toplevel(root)
    alert_window.geometry(root.winfo_geometry())
    alert_window.configure(bg="red")
    alert_window.attributes("-topmost", True)
    alert_label = ttk.Label(alert_window, text=reminder_text, font=("Helvetica", 20), background="red", foreground="white", anchor="center")
    alert_label.pack(expand=True, fill="both")
    alert_window.bind("<Button-1>", lambda e: mute_reminder())
    alert_window.bind("<Destroy>", lambda e: mute_reminder())


# Function to hide alert message
def hide_alert():
    global alert_window
    if alert_window:
        alert_window.destroy()
        alert_window = None

# Function to update the date and time display
def update_datetime():
    current_time = time_module.strftime("%Y-%m-%d %H:%M:%S", time_module.localtime())
    datetime_label.config(text=current_time)
    root.after(1000, update_datetime)  # Update every second

# Creating the GUI
root = ttk.Window(themename="journal")
root.title("Reminder System")
root.geometry("620x300")  # Set the size of the window

alert_window = None  # Initialize alert window variable

datetime_label = ttk.Label(root, text="", font=("Helvetica", 16))
datetime_label.grid(row=0, column=0, columnspan=6, pady=10)

reminder_entry = ttk.Entry(root, width=30)
reminder_entry.grid(row=1, column=1, padx=10)

time_entry = ttk.Entry(root, width=10)
time_entry.grid(row=1, column=3, padx=10)
time_entry.insert(0, time_module.strftime("%H:%M")) # Set default time to current system time

frequency_var = ttk.StringVar(value='one-time')
frequency_menu = ttk.Combobox(root, textvariable=frequency_var, values=['one-time', '24hr'])
frequency_menu.grid(row=1, column=4, padx=10)

set_button = ttk.Button(root, text="Set Reminder", command=set_reminder)
set_button.grid(row=1, column=5, padx=10)

reminder_list = Listbox(root, width=100)
reminder_list.grid(row=2, column=1, columnspan=5, pady=10,padx=10)

update_reminder_list()

# Start monitoring reminders in a separate thread
monitor_thread = Thread(target=monitor_reminders, daemon=True)
monitor_thread.start()

# Start updating date and time
update_datetime()

root.mainloop()
