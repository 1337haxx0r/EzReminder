import mysql.connector


class DataBaseManager:
    """
    A class used to manage the database operations.

    ...

    Attributes
    ----------
    db : mysql.connector.connect
        a MySQL connection object
    cursor : mysql.connector.cursor
        a cursor object associated with the MySQL connection

    Methods
    -------
    fetch_reminders(start_of_day, end_of_day)
        Fetches the reminders for a given day.
    get_reminder_by_id(reminder_id)
        Fetches a specific reminder by its ID.
    add_reminder_to_db(reminder_text, reminder_time, frequency)
        Adds a new reminder to the database.
    remove_reminder_from_db(reminder_id)
        Removes a specific reminder from the database by its ID.
    update_reminder_time(reminder_id, new_time)
        Updates the time of a specific reminder.
    """

    def __init__(self, config):
        """
        Constructs all the necessary attributes for the DataBaseManager object.

        Parameters
        ----------
            config : dict
                a dictionary containing the database configuration parameters
        """
        self.db = mysql.connector.connect(
            host=config['host'],
            user=config['user'],
            password=config['password'],
            database=config['database'],
            charset=config['charset']
        )
        self.cursor = self.db.cursor()

    def fetch_reminders(self, start_of_day, end_of_day):
        """
        Fetches the reminders for a given day.

        Parameters
        ----------
            start_of_day : datetime
                the start of the day
            end_of_day : datetime
                the end of the day

        Returns
        -------
            list
                a list of reminders
        """
        self.cursor.execute(
            "SELECT id, text, frequency, time FROM reminders WHERE time >= %s AND time <= %s ORDER BY time ASC",
            (start_of_day, end_of_day))
        return self.cursor.fetchall()

    def get_reminder_by_id(self, reminder_id):
        """
        Fetches a specific reminder by its ID.

        Parameters
        ----------
            reminder_id : int
                the ID of the reminder

        Returns
        -------
            tuple
                a tuple containing the reminder details
        """
        self.cursor.execute("SELECT id, text, frequency, time FROM reminders WHERE id = %s", (reminder_id,))
        return self.cursor.fetchone()

    def add_reminder_to_db(self, reminder_text, reminder_time, frequency):
        """
        Adds a new reminder to the database.

        Parameters
        ----------
            reminder_text : str
                the text of the reminder
            reminder_time : datetime
                the time of the reminder
            frequency : str
                the frequency of the reminder
        """
        self.cursor.execute("INSERT INTO reminders (text, frequency, time) VALUES (%s, %s, %s)",
                            (reminder_text, frequency, reminder_time))
        self.db.commit()

    def remove_reminder_from_db(self, reminder_id):
        """
        Removes a specific reminder from the database by its ID.

        Parameters
        ----------
            reminder_id : int
                the ID of the reminder
        """
        self.cursor.execute("DELETE FROM reminders WHERE id = %s", (reminder_id,))
        self.db.commit()

    def update_reminder_time(self, reminder_id, new_time):
        """
        Updates the time of a specific reminder.

        Parameters
        ----------
            reminder_id : int
                the ID of the reminder
            new_time : datetime
                the new time of the reminder
        """
        self.cursor.execute("UPDATE reminders SET time = %s WHERE id = %s", (new_time, reminder_id))
        self.db.commit()
