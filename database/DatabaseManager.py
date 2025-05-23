import pymysql
from config.user_config import load_user_config


class DatabaseManager:
    def __init__(self):
        user_config = load_user_config()
        app_config = user_config['db']

        self.db = pymysql.connect(
            host=app_config["host"],
            user=app_config["user"],
            password=app_config["password"],
            database=app_config["database"],
            charset="utf8mb4"
        )
        self.cursor = self.db.cursor()
        print("✅ DatabaseManager is ready.")


    def add_reminder(self, text, timestamp, frequency):
        sql = "INSERT INTO reminders (text, frequency, time) VALUES (%s, %s, %s)"
        self.cursor.execute(sql, (text, frequency, timestamp))
        self.db.commit()

    def get_all_reminders(self):
        self.cursor.execute("SELECT id, text, frequency, time FROM reminders ORDER BY time ASC")
        return self.cursor.fetchall()

    def get_reminder_by_id(self, reminder_id):
        sql = "SELECT id, text, frequency, time FROM reminders WHERE id = %s"
        self.cursor.execute(sql, (reminder_id,))
        return self.cursor.fetchone()

    def update_reminder(self, reminder_id, new_text, new_time, new_frequency):
        sql = "UPDATE reminders SET text = %s, time = %s, frequency = %s WHERE id = %s"
        self.cursor.execute(sql, (new_text, new_time, new_frequency, reminder_id))
        self.db.commit()

    def delete_reminder(self, reminder_id):
        sql = "DELETE FROM reminders WHERE id = %s"
        self.cursor.execute(sql, (reminder_id,))
        self.db.commit()
