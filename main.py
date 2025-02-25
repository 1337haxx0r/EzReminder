# Importing necessary libraries
import ttkbootstrap as ttk  # Used for creating GUIs

# Importing the UpdateManager module. This module is used for managing updates to the application.
import UpdateManager

# Importing all classes, functions, and variables from the DatabaseManager module.
# This module is used for managing the database of the application.
from DatabaseManger import *

# Importing the UpdateManager module again. This is redundant as the module has already been imported above.
# It's generally a good practice to avoid duplicate imports.
from UpdateManager import *

# messagebox: used for displaying messages to the user,
# Listbox: used for creating a listbox widget,
# Toplevel: used for creating new windows
from tkinter import messagebox, Listbox, Toplevel, Menu, Label, Entry, Button

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

    db_manager.add_reminder_to_db(reminder_text, reminder_timestamp, frequency)  # Add the reminder to the database
    update_reminder_list()  # Update the reminder list after adding
    reminder_entry.delete(0, ttk.END)  # Clear the reminder text field after adding
    time_entry.delete(0, ttk.END)  # Clear the time widget after adding
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
        print(original_time)
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
    print(reminders)
    for reminder in reminders:
        reminder_time_str = time_module.strftime('%H:%M', time_module.localtime(reminder[3]))
        reminder_list.insert(ttk.END, f"{reminder[1]} at {reminder_time_str} ({reminder[2]})")
        # listen for double click
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
                    new_time = int(next_reminder[3]) + 24 * 3600
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


# edit reminder from the list by double-clicking which then opens a new window with the reminder details
def edit_reminder(event):
    selected_index = reminder_list.curselection()[0]
    reminders = db_manager.fetch_reminders(start_of_day, end_of_day)
    selected_id = reminders[selected_index][0]
    reminder_details = db_manager.get_reminder_by_id(selected_id)
    edit_window = Toplevel(root)
    edit_window.geometry("340x200")
    edit_window.title("Edit Reminder")
    edit_window.resizable(False, False)

    reminder_text_entry = ttk.Entry(edit_window, width=50)
    reminder_text_entry.grid(row=0, column=0, padx=10, pady=5)
    reminder_text_entry.insert(0, reminder_details[1])

    reminder_time_entry = ttk.Entry(edit_window)
    reminder_time_entry.grid(row=1, column=0, padx=10, pady=5)
    # format HH:MM
    reminder_time_entry.insert(0, time_module.strftime('%H:%M', time_module.localtime(reminder_details[3])))

    #date entry
    # Convert the reminder_date string to a datetime object
    reminder_date = datetime.strptime(time_module.strftime('%Y-%m-%d', time_module.localtime(reminder_details[3])),
                                      '%Y-%m-%d')
    reminder_calendar_entry = ttk.DateEntry(edit_window, style='success.TCalendar', width=15, startdate=reminder_date)
    reminder_calendar_entry.grid(row=2, column=0, padx=5)


    reminder_frequency_entry = ttk.StringVar(value=reminder_details[2])
    reminder_frequency_menu = ttk.Combobox(edit_window, textvariable=reminder_frequency_entry, values=['one-time', '24hr'],
                                  width=8)  # Create a dropdown menu for the frequency of the reminder
    reminder_frequency_menu.grid(row=3, column=0, padx=10, pady=5)  # Add the dropdown menu to the window

    def save_changes():
        # Get the updated details from the Entry widgets
        updated_text = reminder_text_entry.get()
        updated_time = reminder_time_entry.get()
        updated_frequency = reminder_frequency_entry.get()

        try:
            reminder_hour, reminder_minute = map(int, updated_time.split(':'))
        except ValueError:
            messagebox.showerror("Invalid Time Format", "Please enter the time in HH:MM format.")
            return

        # Fetch the date from the calendar widget
        reminder_date_str = reminder_calendar_entry.entry.get()

        # Parse the date string into a datetime.date object
        reminder_date = datetime.strptime(reminder_date_str, "%Y-%m-%d").date()

        # Combine the date and time into a datetime object
        reminder_datetime = datetime.combine(reminder_date, time(hour=reminder_hour, minute=reminder_minute))

        reminder_timestamp = int(reminder_datetime.timestamp())


        # Update the reminder in the database
        db_manager.update_reminder(selected_id, updated_text, reminder_timestamp, updated_frequency)

        # Update the reminder list in the GUI
        update_reminder_list()

        # Close the edit window
        edit_window.destroy()

    # Add a 'Save' button to the window
    save_button = ttk.Button(edit_window, text="Save", command=save_changes)
    save_button.grid(row=4, column=0, padx=10, pady=5)  # Use grid instead of pack


def show_about():
    """
    This function shows an "About" window with information about the application.

    It creates a new Toplevel window and configures it to be on top of all other windows.
    It creates a Label widget with the application name, version, and description and adds it to the window.
    The text of the label is displayed in black on a white background and is centered in the window.
    The function binds the left mouse button click event and the window destroy event to the 'close_about' function.
    This means that when the user clicks on the window or closes it, the window will be closed.

    Returns:
        None
    """
    about_window = Toplevel(root)
    about_window.geometry("300x200")
    about_window.title("About")
    about_window.attributes("-topmost", True)
    about_label = ttk.Label(about_window, text=f"{config['app']['title']} {config['app']['version']}",
                            font=("Helvetica", 12), background="white", foreground="black", anchor="center")
    about_label.pack(expand=True, fill="both")
    about_window.bind("<Button-1>", lambda e: about_window.destroy())
    about_window.bind("<Destroy>", lambda e: about_window.destroy())


def show_debug():
    debug_window = Toplevel(root)
    debug_window.geometry("800x600")
    debug_window.title("Debug Window with Tabs and Listboxes")
    debug_window.attributes("-topmost", True)

    notebook = ttk.Notebook(debug_window)
    notebook.pack(expand=True, fill="both")

    all_frame = ttk.Frame(notebook)
    expired_frame = ttk.Frame(notebook)
    notebook.add(all_frame, text="All")
    notebook.add(expired_frame, text="Expired")

    all_listbox = Listbox(all_frame, width=100)
    all_listbox.pack(padx=10, pady=10, fill="both", expand=True)
    expired_listbox = Listbox(expired_frame, width=100)
    expired_listbox.pack(padx=10, pady=10, fill="both", expand=True)

    all_reminder_records = []
    expired_reminder_records = []

    def update_debug():
        # Clear the listboxes and records
        all_listbox.delete(0, 'end')
        expired_listbox.delete(0, 'end')
        del all_reminder_records[:]
        del expired_reminder_records[:]

        # Fetch reminders and repopulate
        reminders = db_manager.get_all_reminders()
        current_time = int(time_module.time())
        for reminder in reminders:
            reminder_time_str = time_module.strftime('%Y-%m-%d %H:%M:%S', time_module.localtime(reminder[3]))
            display_text = f"{reminder[1]} | {reminder[2]} | {reminder_time_str}"
            all_listbox.insert("end", display_text)
            all_reminder_records.append(reminder)
            if reminder[3] < current_time:
                expired_listbox.insert("end", display_text)
                expired_reminder_records.append(reminder)

    update_debug()  # initial population

    def on_edit_all(event):
        selection = all_listbox.curselection()
        if selection:
            index = selection[0]
            selected_reminder = all_reminder_records[index]
            # Pass update_debug as a callback so that the debug window refreshes after editing.
            edit_reminder_debug(selected_reminder, refresh_callback=update_debug)

    def on_edit_expired(event):
        selection = expired_listbox.curselection()
        if selection:
            index = selection[0]
            selected_reminder = expired_reminder_records[index]
            edit_reminder_debug(selected_reminder, refresh_callback=update_debug)

    all_listbox.bind("<Double-Button-1>", on_edit_all)
    expired_listbox.bind("<Double-Button-1>", on_edit_expired)


def edit_reminder_debug(reminder, refresh_callback=None):
    selected_id = reminder[0]
    reminder_details = db_manager.get_reminder_by_id(selected_id)
    edit_window = Toplevel(root)
    edit_window.geometry("340x300")
    edit_window.title("Edit Reminder")
    edit_window.resizable(False, False)
    edit_window.attributes("-topmost", True)
    edit_window.grab_set()  # Optionally make it modal

    reminder_text_entry = ttk.Entry(edit_window, width=50)
    reminder_text_entry.grid(row=0, column=0, padx=10, pady=5)
    reminder_text_entry.insert(0, reminder_details[1])

    reminder_time_entry = ttk.Entry(edit_window)
    reminder_time_entry.grid(row=1, column=0, padx=10, pady=5)
    reminder_time_entry.insert(0, time_module.strftime('%H:%M', time_module.localtime(reminder_details[3])))

            reminder_date = datetime.strptime(time_module.strftime('%Y-%m-%d', time_module.localtime(reminder_details[3])),
                                              '%Y-%m-%d')
            reminder_calendar_entry = ttk.DateEntry(edit_window, style='success.TCalendar', width=15, startdate=reminder_date)
            reminder_calendar_entry.grid(row=2, column=0, padx=(70, 0), pady=5)

            def set_today():
                today_date = datetime.today().strftime('%Y-%m-%d')
                reminder_calendar_entry.entry.delete(0, 'end')
                reminder_calendar_entry.entry.insert(0, today_date)

            today_button = ttk.Button(edit_window, text="Today", command=set_today)
            today_button.grid(row=2, column=1, padx=(0, 50), pady=5)

    reminder_frequency_entry = ttk.StringVar(value=reminder_details[2])
    reminder_frequency_menu = ttk.Combobox(edit_window, textvariable=reminder_frequency_entry,
                                           values=['one-time', '24hr'], width=8)
    reminder_frequency_menu.grid(row=3, column=0, padx=10, pady=5)

    def save_changes():
        updated_text = reminder_text_entry.get()
        updated_time = reminder_time_entry.get()
        updated_frequency = reminder_frequency_entry.get()

        try:
            reminder_hour, reminder_minute = map(int, updated_time.split(':'))
        except ValueError:
            messagebox.showerror("Invalid Time Format", "Please enter the time in HH:MM format.")
            return

        reminder_date_str = reminder_calendar_entry.entry.get()
        reminder_date = datetime.strptime(reminder_date_str, "%Y-%m-%d").date()
        reminder_datetime = datetime.combine(reminder_date, time(hour=reminder_hour, minute=reminder_minute))
        reminder_timestamp = int(reminder_datetime.timestamp())

        db_manager.update_reminder(selected_id, updated_text, reminder_timestamp, updated_frequency)
        update_reminder_list()  # Optionally update your main list as well

        # Call the refresh callback to update the debug window if provided
        if refresh_callback:
            refresh_callback()

        edit_window.destroy()

    save_button = ttk.Button(edit_window, text="Save", command=save_changes)
    save_button.grid(row=4, column=0, padx=10, pady=5)
    delete_button = ttk.Button(edit_window, text="Delete",
                               command=lambda: delete_reminder_debug(selected_id, refresh_callback))
    delete_button.grid(row=5, column=0, padx=10, pady=5)


def open_settings():
    # Create a new window
    settings_window = Toplevel(root)
    settings_window.title('Settings')

    # Create an Entry widget for each field in the config dictionary
    entries = {}
    row = 0  # Initialize row counter
    for section, section_config in config.items():
        for key, value in section_config.items():
            Label(settings_window, text=f"{section}.{key}").grid(row=row, column=0)
            entry = Entry(settings_window)
            entry.insert(0, value)
            entry.grid(row=row, column=1, padx=10, pady=5)

            # Disable the 'version' field
            if key == 'version':
                entry.config(state='disabled')

            entries[f"{section}.{key}"] = entry
            row += 1  # Increment row counter for each key in the section

    # Function to save changes
    def save_changes():
        # Update the config dictionary with the current values from the Entry widgets
        for key, entry in entries.items():
            section, field = key.split('.')
            config[section][field] = entry.get()

        # Write the updated config dictionary back to the config.json file
        with open('config.json', 'w') as f:
            json.dump(config, f, indent=4)

            # if settings are saved, show a message
            messagebox.showinfo("Settings",
                                "Settings have been saved successfully. Please reload the application for changes to take effect.")

        settings_window.destroy()

    # Add a "Save" button
    Button(settings_window, text="Save", command=save_changes).grid(row=row, column=0, columnspan=2, pady=10)


# Creating the GUI
root = ttk.Window(themename="journal")  # Create a new window with the "journal" theme
root.title(
    config['app']['title'] + ' | ' + config['app']['version'])  # Set the title of the window to "Reminder System"
root.geometry("750x300")  # Set the size of the window to 700x300 pixels
root.resizable(False, False)  # Disable resizing of the window

# Creating a top-level menu for the application window
top_menu = Menu(root)

# Configuring the created menu to be the menu of the root window
root.config(menu=top_menu)

# Creating a submenu for the 'Application' menu item
root.file_menu = Menu(top_menu)

# Adding the 'Application' submenu to the top-level menu
top_menu.add_cascade(label='Application', menu=root.file_menu)

# Adding a 'Settings' command to the 'Application' submenu, which calls the 'open_settings' function when clicked
root.file_menu.add_command(label='Settings', command=open_settings)

# Adding a separator to the 'Application' submenu
root.file_menu.add_separator()

# Adding an 'Exit' command to the 'Application' submenu, which quits the application when clicked
root.file_menu.add_command(label='Exit', command=root.quit)

# Creating a submenu for the 'Help' menu item
root.help_menu = Menu(top_menu)

# Adding the 'Help' submenu to the top-level menu
top_menu.add_cascade(label='Help', menu=root.help_menu)

# Adding an 'About' command to the 'Help' submenu, which calls the 'show_about' function when clicked
root.help_menu.add_command(label='About', command=show_about)

# Adding a 'Check for updates' command to the 'Help' submenu, which checks for updates when clicked
root.help_menu.add_command(label='Check for updates',
                           command=lambda: UpdateManager.check_for_updates(config['app'], progressbar, root))

root.help_menu.add_separator()

root.help_menu.add_command(label='debug', command=show_debug)

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
reminder_list.bind("<Double-1>", edit_reminder)

update_reminder_list()  # Update the list of reminders

# Start monitoring reminders in a separate thread
monitor_thread = Thread(target=monitor_reminders, daemon=True)  # Create a new thread to monitor reminders
monitor_thread.start()  # Start the thread

# Start updating date and time
update_datetime()  # Update the date and time display

progressbar = ttk.Progressbar(root, length=200)
progressbar.grid(row=5, column=0, columnspan=7, pady=10)  # Adjust row and column as needed

root.mainloop()  # Start the main event loop of the window
