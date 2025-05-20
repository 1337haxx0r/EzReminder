from database.DatabaseManager import DatabaseManager
import time
from datetime import datetime, timedelta

def run_reminder_loop():
    db = DatabaseManager()

    print("⏱️ Reminder loop started... (Ctrl+C to stop)")

    while True:
        now_ts = int(time.time())
        reminders = db.get_all_reminders()

        for reminder in reminders:
            id, text, frequency, remind_time = reminder

            if now_ts >= remind_time:
                print(f"🔔 Reminder: {text} (ID {id}, freq: {frequency})")

                if frequency == "one-time":
                    db.delete_reminder(id)

                elif frequency == "24hr":
                    next_time = remind_time + 24 * 3600
                    db.update_reminder(id, text, next_time, frequency)

                elif frequency == "weekly":
                    next_time = remind_time + 7 * 24 * 3600
                    db.update_reminder(id, text, next_time, frequency)

                elif frequency == "monthly":
                    next_datetime = datetime.fromtimestamp(remind_time) + timedelta(days=30)
                    db.update_reminder(id, text, int(next_datetime.timestamp()), frequency)

        time.sleep(5)
