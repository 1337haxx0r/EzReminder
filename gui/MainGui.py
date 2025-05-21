from ttkbootstrap import Window, Label, Entry, Button, Combobox, DateEntry, Progressbar
from tkinter import Menu, Listbox, StringVar, Toplevel, messagebox
from threading import Thread
from datetime import datetime, time as dt_time
import time as time_module

from database.DatabaseManager import DatabaseManager
from config.user_config import save_user_config, load_user_config
from logic.UpdateManager import check_for_updates
import platform

import json
import os

import io
from gtts import gTTS
import pygame

def launch_gui():

    # Check if the script is running MAC
    IS_MAC = platform.system() == "Darwin"

    print(platform.system())

    active_reminder = False
    alert_window = None

    user_config = load_user_config()
    app_config = user_config['app']

    db = None  # ✅ Make it accessible everywhere
    db_connected = False

    try:
        db = DatabaseManager()
        db_connected = True
    except Exception as e:
        print(f"❌ DB Connection failed: {e}")


    date_format = "%m/%d/%Y"

    def open_settings():
        settings_window = Toplevel(root)
        settings_window.title("Settings")
        settings_window.geometry("350x350")
        settings_window.resizable(False, False)

        current_config = load_user_config()

        entries = {}
        row = 0
        for section, fields in current_config.items():
            for key, value in fields.items():
                Label(settings_window, text=f"{section}.{key}").grid(row=row, column=0, sticky='w', padx=10, pady=5)
                entry = Entry(settings_window, width=30)
                entry.insert(0, value)
                entry.grid(row=row, column=1, padx=10, pady=5)

                if key == "version":
                    entry.config(state='disabled')  # Don't allow editing version

                entries[f"{section}.{key}"] = entry
                row += 1

        def save_changes():
            for full_key, entry in entries.items():
                section, key = full_key.split('.')
                current_config[section][key] = entry.get()

            save_user_config(current_config)

            # Try reconnecting the database
            nonlocal db, db_connected
            try:
                db = DatabaseManager()
                db_connected = True
                connection_banner.grid_remove()  # ✅ Hide banner once connected
                update_reminder_list()
                messagebox.showinfo("Settings", "Settings saved and database connection successful.")
                settings_window.destroy()

            except Exception as e:
                messagebox.showerror("Database Error", f"Connection failed:\n{e}")

        Button(settings_window, text="Save", command=save_changes).grid(row=row, column=0, columnspan=2, pady=10)


    def show_alert(text):
        global alert_window
        alert_window = Toplevel(root)
        alert_window.geometry(root.winfo_geometry())
        alert_window.configure(bg="red")
        alert_window.attributes("-topmost", True)
        label = Label(alert_window, text=text, font=("Helvetica", 20), background="red", foreground="white", anchor="center")
        label.pack(expand=True, fill="both")
        alert_window.bind("<Button-1>", lambda e: mute_reminder())
        alert_window.bind("<Destroy>", lambda e: mute_reminder())


    def hide_alert():
        global alert_window
        if alert_window:
            alert_window.destroy()
            alert_window = None



    def play_reminder(text, reminder_id, frequency):
        global active_reminder
        active_reminder = True

        tts = gTTS(text, lang='en')

        mp3_fp1 = io.BytesIO()
        mp3_fp2 = io.BytesIO()
        tts.write_to_fp(mp3_fp1)
        tts.write_to_fp(mp3_fp2)
        mp3_fp1.seek(0)
        mp3_fp2.seek(0)

        pygame.mixer.init()
        sound = pygame.mixer.Sound(mp3_fp2)
        length = round(sound.get_length())

        # Handle frequency
        if frequency == 'one-time':
            db.delete_reminder(reminder_id)
        else:
            next_time = {
                "24hr": 1,
                "weekly": 7,
                "monthly": 30
            }.get(frequency, 0)

            if next_time > 0:
                new_time = int(datetime.now().timestamp()) + next_time * 86400
                db.update_reminder(reminder_id, text, new_time, frequency)

        update_reminder_list()

        show_alert(text)
        mp3_bytes = mp3_fp1.getvalue()  # Get raw bytes once

        while active_reminder:
            buffer = io.BytesIO(mp3_bytes)  # Fresh buffer each loop
            pygame.mixer.music.load(buffer, 'mp3')
            pygame.mixer.music.play()
            time_module.sleep(length + 2)





    def mute_reminder():
        global active_reminder
        active_reminder = False
        pygame.mixer.music.stop()
        hide_alert()

    def update_reminder_list():
        reminder_list.delete(0, 'end')

        if not db:
            return  # don't do anything if db is not ready

        today = datetime.today()
        start_of_day = int(datetime(today.year, today.month, today.day, 0, 0, 1).timestamp())
        end_of_day = int(datetime(today.year, today.month, today.day, 23, 59, 59).timestamp())

        reminders = [r for r in db.get_all_reminders() if start_of_day <= r[3] <= end_of_day]

        for r in reminders:
            readable_time = datetime.fromtimestamp(r[3]).strftime(f"{date_format} %H:%M")
            reminder_list.insert('end', f"{r[1]} ({r[2]}) at {readable_time}")

    def set_reminder():
        text = reminder_entry.get()
        t_str = time_entry.get()
        date_str = calendar_entry.entry.get()
        freq = frequency_var.get()

        if not text or ":" not in t_str:
            messagebox.showerror("Input Error", "Please enter valid reminder text and time.")
            return

        # auto detect date format
        # todo: make once reusable function
        try:
            hour, minute = map(int, t_str.split(":"))
            reminder_date = datetime.strptime(date_str, date_format).date()


            reminder_datetime = datetime.combine(reminder_date, dt_time(hour=hour, minute=minute))
            timestamp = int(reminder_datetime.timestamp())
        except Exception as e:
            messagebox.showerror("Time Error", f"Failed to parse time: {e}")
            return

        db.add_reminder(text, timestamp, freq)
        update_reminder_list()

        # Reset fields
        reminder_entry.delete(0, 'end')
        time_entry.delete(0, 'end')
        time_entry.insert(0, time_module.strftime("%H:%M"))
        calendar_entry.entry.delete(0, 'end')
        calendar_entry.entry.insert(0, reminder_date.strftime(date_format))
        frequency_var.set('one-time')

        status_label.config(text=f"Reminder was added for {reminder_date.strftime(date_format)} at {t_str}", foreground="green")
        root.after(5000, lambda: status_label.config(text=""))

    def open_edit_window():
        selection = reminder_list.curselection()
        if not selection:
            return

        index = selection[0]
        all_reminders = db.get_all_reminders()
        reminder = all_reminders[index]
        reminder_id, text, frequency, ts = reminder

        # Convert timestamp to datetime components
        dt_obj = datetime.fromtimestamp(ts)
        reminder_time_str = dt_obj.strftime("%H:%M")
        reminder_date_str = dt_obj.strftime(date_format)

        # Create popup
        win = Toplevel(root)
        win.title("Edit Reminder")
        win.geometry("300x250")
        win.resizable(False, False)

        # Fields
        text_entry = Entry(win, width=40)
        text_entry.insert(0, text)
        text_entry.pack(pady=5)

        time_entry_popup = Entry(win, width=10)
        time_entry_popup.insert(0, reminder_time_str)
        time_entry_popup.pack(pady=5)

        calendar_popup = DateEntry(win, dateformat=date_format, width=12)
        calendar_popup.entry.delete(0, 'end')
        calendar_popup.entry.insert(0, reminder_date_str)
        calendar_popup.pack(pady=5)

        freq_var = StringVar(value=frequency)
        freq_menu = Combobox(win, textvariable=freq_var, values=["one-time", "24hr", "weekly", "monthly"], width=10)
        freq_menu.pack(pady=5)

        def save_changes():
            new_text = text_entry.get()
            new_time_str = time_entry_popup.get()
            new_date_str = calendar_popup.entry.get()
            new_freq = freq_var.get()

            try:
                hour, minute = map(int, new_time_str.split(":"))

                # todo: make once reusable function
                try:
                    new_date = datetime.strptime(new_date_str, date_format).date()
                except ValueError:
                    try:
                        new_date = datetime.strptime(new_date_str, "%Y-%m-%d").date()
                    except ValueError:
                        messagebox.showerror("Invalid Date", f"Unrecognized format: {new_date_str}")
                        return

                new_dt = datetime.combine(new_date, dt_time(hour=hour, minute=minute))
                new_ts = int(new_dt.timestamp())
            except Exception as e:
                messagebox.showerror("Invalid Time", str(e))
                return

            db.update_reminder(reminder_id, new_text, new_ts, new_freq)
            update_reminder_list()
            win.destroy()

        def delete_reminder():
            db.delete_reminder(reminder_id)
            update_reminder_list()
            win.destroy()

        Button(win, text="Save", command=save_changes, style='success.TButton').pack(pady=(10, 5))
        Button(win, text="Delete", command=delete_reminder, style='danger.TButton').pack()



    # GUI Init
    root = Window(themename="journal")

    # Set the window size based on the DPI
    dpi = root.winfo_fpixels('1i')
    scale = dpi / 96  # baseline DPI

    base_width, base_height = 750, 300
    scaled_width = int(base_width * scale)
    scaled_height = int(base_height * scale)
    root.geometry(f"{scaled_width}x{scaled_height}")

    root.title(f"{app_config['title']} | {app_config['version']}")
    root.resizable(False, False)



    # ----------------------------
    # Top Menu
    # ----------------------------
    top_menu = Menu(root)
    root.config(menu=top_menu)

    root.file_menu = Menu(top_menu, tearoff=0)
    top_menu.add_cascade(label='Application', menu=root.file_menu)
    root.file_menu.add_command(label='Settings', command=open_settings)
    root.file_menu.add_separator()
    root.file_menu.add_command(label='Exit', command=root.quit)

    root.help_menu = Menu(top_menu, tearoff=0)
    top_menu.add_cascade(label='Help', menu=root.help_menu)
    root.help_menu.add_command(label='About', command=lambda: messagebox.showinfo("About",
                                                                                  f"{app_config['title']} | {app_config['version']}"))
    root.help_menu.add_command(
        label='Check for updates',
        command=lambda: check_for_updates(app_config, progressbar, root)
    )

    root.help_menu.add_separator()
    root.help_menu.add_command(label='Debug', command=lambda: messagebox.showinfo("Debug", "To be added"))

    # ----------------------------
    # Widgets
    # ----------------------------
    datetime_label = Label(root, text="", font=("Helvetica", 16))
    datetime_label.grid(row=0, column=0, columnspan=6, pady=10)

    connection_banner = Label(root, text="", font=("Helvetica", 10), anchor="center", background="red",
                              foreground="white")
    connection_banner.grid(row=1, column=0, columnspan=7, sticky='we', pady=(0, 5))
    connection_banner.grid_remove()  # hidden by default

    reminder_entry = Entry(root, width=50)
    reminder_entry.grid(row=2, column=1, padx=10)

    time_entry = Entry(root, width=10)
    time_entry.grid(row=2, column=4, padx=5)
    time_entry.insert(0, time_module.strftime("%H:%M"))

    calendar_entry = DateEntry(root, dateformat=date_format, style='success.TCalendar', width=10)
    calendar_entry.grid(row=2, column=3, padx=5)

    frequency_var = StringVar(value='one-time')
    frequency_menu = Combobox(root, textvariable=frequency_var, values=['one-time', '24hr', 'weekly', 'monthly'], width=8)
    frequency_menu.grid(row=2, column=5)

    set_button = Button(root, text="Set Reminder", command=set_reminder, style='success.TButton')
    set_button.grid(row=2, column=6, padx=10)

    reminder_list = Listbox(root, width=120)
    reminder_list.bind("<Double-1>", lambda event: open_edit_window())
    reminder_list.grid(row=3, column=1, columnspan=7, pady=10, padx=10)

    status_label = Label(root, text="", font=("Helvetica", 10), anchor="center")
    status_label.grid(row=6, column=0, columnspan=7, pady=(0, 10))

    progressbar = Progressbar(root, length=200)
    progressbar.grid(row=5, column=0, columnspan=7, pady=10)
    progressbar.grid_remove()  # hides it until needed

    # ----------------------------
    # Dynamic Time Label
    # ----------------------------
    def update_datetime():
        current_time = time_module.strftime(date_format + " %H:%M:%S", time_module.localtime())
        datetime_label.config(text=current_time)
        root.after(1000, update_datetime)

    update_datetime()
    if db_connected:
        update_reminder_list()

    # ✅ Show settings only if DB failed
    if not db_connected:
        connection_banner.config(text="⚠️ Could not connect to the database. Please check your settings.")
        connection_banner.grid()
        root.after(100, open_settings)

    def monitor_reminders():
        while True:
            if db and not active_reminder:  # ✅ only run if DB is connected
                now = int(time_module.time())
                reminders = db.get_all_reminders()
                for r in reminders:
                    if r[3] <= now:
                        play_reminder(r[1], r[0], r[2])
                        break
            time_module.sleep(5)

    monitor_thread = Thread(target=monitor_reminders, daemon=True)
    monitor_thread.start()


    # Start GUI
    root.mainloop()
