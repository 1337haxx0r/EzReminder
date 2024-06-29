# Importing necessary libraries
import json  # Used for parsing and manipulating JSON data
import ttkbootstrap as ttk  # Used for creating GUIs

import UpdateManager
from DatabaseManger import *
from UpdateManager import *

# messagebox: used for displaying messages to the user,
# Listbox: used for creating a listbox widget,
# Toplevel: used for creating new windows
from tkinter import messagebox, Listbox, Toplevel, Menu

import time as time_module  # Used for handling time-related tasks
from threading import Thread  # Used for creating and managing new threads
from gtts import gTTS  # Google Text-to-Speech: used for converting text into speech
import pygame  # Used for playing sounds
import mysql.connector  # Used for connecting to and interacting with MySQL databases
import io  # Used for handling the I/O operations

# datetime: used for manipulating dates and times,
# time: used for encapsulating
from datetime import datetime, time, timedelta

# config file
with open('config.json') as config_file:
    config = json.load(config_file)

db_manager = DataBaseManager(config['database'])
start_of_day = datetime.combine(datetime.today(), time.min).timestamp()
end_of_day = datetime.combine(datetime.today(), time.max).timestamp()

# A flag to indicate whether the reminder list has been updated.
# This is used in the 'monitor_reminders' function to check if it needs to fetch the reminders from the database again.
# It is initially set to True so that the reminders are fetched when the program starts.
reminder_list_updated = True

# A flag to indicate whether a reminder is currently being played.
# This is used in the 'play_reminder' and 'mute_reminder' functions to control the playing of the reminder sound.
# It is initially set to False as no reminder is being played when the program starts.
active_reminder = False

current_date = datetime.today().date()


# Function to set a reminder
def set_reminder():
    """
    This function sets a new reminder.

    It first retrieves the reminder text, time, and frequency from the respective entry fields in the GUI.
    If the reminder text is empty, it shows an error message and returns.
    It then tries to parse the reminder time as hours and minutes. If the parsing fails, it shows an error message and returns.
    It calculates the delay until the reminder time in seconds. If the reminder time is in the past, it sets the delay to 0.
    It converts the delay to a Unix timestamp and adds the new reminder to the database.
    After adding the reminder, it updates the reminder list in the GUI and clears the reminder text and time fields.

    Returns:
        None
    """
    reminder_text = reminder_entry.get()
    reminder_time = time_entry.get()
    frequency = frequency_var.get()

    if not reminder_text:
        messagebox.showerror("Invalid Reminder", "Please enter a reminder text.")
        return

    try:
        reminder_hour, reminder_minute = map(int, reminder_time.split(':'))
    except ValueError:
        messagebox.showerror("Invalid Time Format", "Please enter the time in HH:MM format.")
        return

    # Fetch the date from the calendar widget
    reminder_date_str = calendar_entry.entry.get()

    # Parse the date string into a datetime.date object
    reminder_date = datetime.strptime(reminder_date_str, "%Y-%m-%d").date()

    # Combine the date and time into a datetime object
    reminder_datetime = datetime.combine(reminder_date, time(hour=reminder_hour, minute=reminder_minute))

    # Check if the reminder time is in the past for 24hr frequency and add 24 hours to the reminder time
    if frequency == '24hr' and reminder_datetime < datetime.now():
        reminder_datetime += timedelta(days=1)

    # Convert the datetime object to a Unix timestamp
    reminder_timestamp = int(reminder_datetime.timestamp())

    db_manager.add_reminder_to_db(reminder_text, reminder_timestamp, frequency)
    update_reminder_list()
    reminder_entry.delete(0, ttk.END)  # Clear the reminder text field after adding
    time_entry.delete(0, ttk.END)
    time_entry.insert(0, time_module.strftime("%H:%M"))  # Set default time to current system time
    calendar_entry.entry.delete(0, ttk.END)  # Clear the calendar widget after adding
    calendar_entry.entry.insert(0, time_module.strftime("%Y-%m-%d"))  # Set default date to current system date

    # Create a new label underneath the datetime_label
    message_label = ttk.Label(root, text=f"Reminder was successfully added for {reminder_date} at {reminder_time}",
                              font=("Helvetica", 10), foreground="white", background="green", anchor="center")
    message_label.grid(row=4, column=1, columnspan=6, pady=10)

    # Schedule a function to destroy the label after 5 seconds (5000 milliseconds)
    root.after(5000, message_label.destroy)


# Function to play the reminder
def play_reminder(reminder_text, reminder_id, frequency):
    """
    This function plays the reminder sound and shows an alert window with the reminder text.

    It takes three parameters: the text of the reminder, the id of the reminder, and the frequency of the reminder.
    It uses Google Text-to-Speech to convert the reminder text into speech and pygame to play the speech.
    It shows an alert window with the reminder text. The alert window can be closed by clicking on it.
    If the frequency of the reminder is 'one-time', it removes the reminder from the database after playing it.
    If the frequency of the reminder is '24hr', it updates the time of the reminder to the same time on the next day.

    Parameters:
        reminder_text (str): The text of the reminder.
        reminder_id (int): The id of the reminder.
        frequency (str): The frequency of the reminder. Can be 'one-time' or '24hr'.

    Returns:
        None
    """
    global active_reminder
    active_reminder = True
    tts = gTTS(reminder_text, lang='en')
    mp3_fp1 = io.BytesIO()
    mp3_fp2 = io.BytesIO()
    tts.write_to_fp(mp3_fp1)
    tts.write_to_fp(mp3_fp2)
    mp3_fp1.seek(0)
    mp3_fp2.seek(0)

    pygame.mixer.init()
    pygame.mixer.music.load(mp3_fp1, 'mp3')
    sound = pygame.mixer.Sound(mp3_fp2)  # Create a Sound object
    length = round(sound.get_length())
    show_alert(reminder_text)

    if frequency == 'one-time':
        db_manager.remove_reminder_from_db(reminder_id)
        update_reminder_list()  # Update the reminder list after playing the reminder
    elif frequency == '24hr':
        # Fetch the original time of the reminder from the database
        fetch_reminder = db_manager.get_reminder_by_id(reminder_id)
        original_time = fetch_reminder[3]

        # Convert the original time to a datetime object
        original_datetime = datetime.fromtimestamp(original_time)

        # Add 24 hours to the original datetime
        new_datetime = original_datetime + timedelta(hours=24)

        # Convert the new datetime back to a Unix timestamp
        new_time = int(new_datetime.timestamp())

        db_manager.update_reminder_time(reminder_id, new_time)
        update_reminder_list()  # Update the reminder list after playing the reminder

    while active_reminder:
        pygame.mixer.music.play()  # Play the reminder once
        time_module.sleep(length + 3)

    hide_alert()  # do I need this?


# Function to mute the reminder sound
def mute_reminder():
    """
    This function mutes the currently playing reminder.

    It sets the global variable 'active_reminder' to False, which stops the reminder sound from playing in the 'play_reminder' function.
    It then stops the pygame mixer music and hides the alert window.

    Returns:
        None
    """
    global active_reminder
    active_reminder = False
    pygame.mixer.music.stop()
    hide_alert()


# Function to update the reminder list in the GUI
def update_reminder_list():
    """
    This function updates the reminder list in the GUI.

    It first deletes all items from the reminder list.
    It then fetches the reminders that are scheduled for the current day from the database.
    For each reminder, it formats the time as a string in HH:MM format and inserts the reminder into the reminder list.
    The reminder is inserted as a string in the format "reminder text at reminder time (reminder frequency)".
    After updating the reminder list, it sets the global variable 'reminder_list_updated' to True.

    Returns:
        None
    """
    global reminder_list_updated
    reminder_list.delete(0, ttk.END)
    reminders = db_manager.fetch_reminders(start_of_day, end_of_day)
    for reminder in reminders:
        reminder_time_str = time_module.strftime('%H:%M', time_module.localtime(reminder[3]))
        reminder_list.insert(ttk.END, f"{reminder[1]} at {reminder_time_str} ({reminder[2]})")
    reminder_list_updated = True


# Function to monitor reminders
def monitor_reminders():
    """
    This function continuously monitors the reminders.

    It runs in an infinite loop, checking for updates to the reminder list and playing reminders when their time comes.
    If the reminder list has been updated, it fetches the reminders that are scheduled for the current day from the database.
    It then resets the 'reminder_list_updated' flag to False.
    If there are any reminders, it gets the next reminder (the one with the earliest time).
    It checks if the time of the next reminder is less than or equal to the current time. If it is, it plays the reminder.
    If the frequency of the reminder is 'one-time', it removes the reminder from the database after playing it.
    If the frequency of the reminder is '24hr', it updates the time of the reminder to the same time on the next day.
    The function sleeps for 1 second after each iteration of the loop.

    Returns:
        None
    """
    global reminder_list_updated
    while True:
        if reminder_list_updated:
            reminders = db_manager.fetch_reminders(start_of_day, end_of_day)
            reminder_list_updated = False  # Reset the flag after fetching the reminders
        if reminders:
            next_reminder = reminders[0]
            current_time_seconds = int(datetime.now().timestamp())  # Get current time in local timezone
            if next_reminder[3] <= current_time_seconds:
                play_reminder(next_reminder[1], next_reminder[0], next_reminder[2])
                if next_reminder[2] == 'one-time':
                    db_manager.remove_reminder_from_db(next_reminder[0])
                elif next_reminder[2] == '24hr':
                    new_time = int(datetime.now().timestamp()) + 24 * 3600
                    db_manager.update_reminder_time(next_reminder[0], new_time)
        time_module.sleep(1)  # Check every second


# Function to show alert message
def show_alert(reminder_text):
    """
    This function shows an alert window with the reminder text.

    It takes one parameter: the text of the reminder.
    It creates a new Toplevel window and configures it to be on top of all other windows and have a red background.
    It creates a Label widget with the reminder text and adds it to the alert window.
    The text of the label is displayed in white on a red background and is centered in the window.
    The function binds the left mouse button click event and the window destroy event to the 'mute_reminder' function.
    This means that when the user clicks on the alert window or closes it, the reminder sound will be muted.

    Parameters:
        reminder_text (str): The text of the reminder.

    Returns:
        None
    """
    global alert_window
    alert_window = Toplevel(root)
    alert_window.geometry(root.winfo_geometry())
    alert_window.configure(bg="red")
    alert_window.attributes("-topmost", True)
    alert_label = ttk.Label(alert_window, text=reminder_text, font=("Helvetica", 20), background="red",
                            foreground="white", anchor="center")
    alert_label.pack(expand=True, fill="both")
    alert_window.bind("<Button-1>", lambda e: mute_reminder())
    alert_window.bind("<Destroy>", lambda e: mute_reminder())


# Function to hide alert message
def hide_alert():
    """
    This function hides the currently displayed alert window.

    It first checks if the global variable 'alert_window' is not None, which means that an alert window is currently displayed.
    If an alert window is displayed, it destroys the window and sets 'alert_window' to None.

    Returns:
        None
    """
    global alert_window
    if alert_window:
        alert_window.destroy()
        alert_window = None


# Function to update the date and time display
def update_datetime():
    """
    This function updates the date and time display in the GUI.

    It gets the current date and time, formats it as a string in "YYYY-MM-DD HH:MM:SS" format, and sets the text of the 'datetime_label' to this string.
    It then schedules itself to be called again after 1000 milliseconds (1 second), creating a loop that updates the date and time display every second.

    Returns:
        None
    """
    global current_date
    current_time = time_module.strftime("%Y-%m-%d %H:%M:%S", time_module.localtime())
    datetime_label.config(text=current_time)

    # Check if the date has changed
    new_date = datetime.today().date()
    if new_date != current_date:
        update_reminder_list()
        current_date = new_date

    root.after(1000, update_datetime)  # Update every second


# Creating the GUI
root = ttk.Window(themename="journal")  # Create a new window with the "journal" theme
root.title(config['app']['title'])  # Set the title of the window to "Reminder System"
root.geometry("750x300")  # Set the size of the window to 700x300 pixels



top_menu = Menu(root)
root.config(menu=top_menu)


root.file_menu = Menu(top_menu)
top_menu.add_cascade(label='Application', menu=root.file_menu)
root.file_menu.add_command(label='Settings')
root.file_menu.add_command(label='Change Theme')
root.file_menu.add_separator()
root.file_menu.add_command(label='Exit', command=root.quit)

root.help_menu = Menu(top_menu)
top_menu.add_cascade(label='Help', menu=root.help_menu)
root.help_menu.add_command(label='About')
root.help_menu.add_command(label='Check for updates', command=lambda: UpdateManager.check_for_updates(config['app'], progressbar, root))




# check if icon file is present in the directory
# if not, set the default icon
try:
    root.iconbitmap("icon/" + config['app']['icon'])  # Set the icon of the window to "icon.ico"
except:
    pass

alert_window = None  # Initialize the alert window variable to None. This will be used to store the alert window
# object when a reminder is played.

datetime_label = ttk.Label(root, text="", font=("Helvetica", 16))  # Create a label to display the current date and time
datetime_label.grid(row=0, column=0, columnspan=6, pady=10)  # Add the label to the window

reminder_entry = ttk.Entry(root, width=50)  # Create an entry field for the reminder text
reminder_entry.grid(row=2, column=1, padx=10)  # Add the entry field to the window

time_entry = ttk.Entry(root, width=10)  # Create an entry field for the reminder time
time_entry.grid(row=2, column=4, padx=5)  # Add the entry field to the window
time_entry.insert(0,
                  time_module.strftime("%H:%M"))  # Set the default value of the entry field to the current system time

calendar_entry = ttk.DateEntry(root, style='success.TCalendar', width=10)  # Create a calendar widget
calendar_entry.grid(row=2, column=3, padx=5)  # Add the calendar widget to the window

frequency_var = ttk.StringVar(value='one-time')  # Create a variable to store the frequency of the reminder
frequency_menu = ttk.Combobox(root, textvariable=frequency_var, values=['one-time', '24hr'],
                              width=8)  # Create a dropdown menu for the frequency of the reminder
frequency_menu.grid(row=2, column=5, )  # Add the dropdown menu to the window

set_button = ttk.Button(root, text="Set Reminder", command=set_reminder)  # Create a button to set a new reminder
set_button.grid(row=2, column=6, padx=10)  # Add the button to the window

reminder_list = Listbox(root, width=120)  # Create a listbox to display the list of reminders
reminder_list.grid(row=3, column=1, columnspan=7, pady=10, padx=10)  # Add the listbox to the window

update_reminder_list()  # Update the list of reminders

# Start monitoring reminders in a separate thread
monitor_thread = Thread(target=monitor_reminders, daemon=True)  # Create a new thread to monitor reminders
monitor_thread.start()  # Start the thread

# Start updating date and time
update_datetime()  # Update the date and time display

root.mainloop()  # Start the main event loop of the window
