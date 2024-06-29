import mysql.connector


class DataBaseManager:
    def __init__(self, config):
        self.db = mysql.connector.connect(
            host=config['host'],
            user=config['user'],
            password=config['password'],
            database=config['database'],
            charset=config['charset']
        )
        self.cursor = self.db.cursor()

    def fetch_reminders(self, start_of_day, end_of_day):

        self.cursor.execute("SELECT id, text, frequency, time FROM reminders WHERE time >= %s AND time <= %s ORDER BY time ASC",
                   (start_of_day, end_of_day))
        return self.cursor.fetchall()

    def get_reminder_by_id(self, reminder_id):
        self.cursor.execute("SELECT id, text, frequency, time FROM reminders WHERE id = %s", (reminder_id,))
        return self.cursor.fetchone()

    def add_reminder_to_db(self, reminder_text, reminder_time, frequency):
        self.cursor.execute("INSERT INTO reminders (text, frequency, time) VALUES (%s, %s, %s)",
                            (reminder_text, frequency, reminder_time))
        self.db.commit()

    def remove_reminder_from_db(self, reminder_id):
        self.cursor.execute("DELETE FROM reminders WHERE id = %s", (reminder_id,))
        self.db.commit()

    def update_reminder_time(self, reminder_id, new_time):
            self.cursor.execute("UPDATE reminders SET time = %s WHERE id = %s", (new_time, reminder_id))
            self.db.commit()
