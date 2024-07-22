
# EzReminder

EzReminder is a Python-based reminder system with a user interface that reads reminder texts aloud until muted. It stores reminders in a MySQL database and displays a list of reminders. Reminders can be one-time or recurring daily.

## Features

- **User Interface**: Displays a list of reminders and provides controls to mute them.
- **Text-to-Speech**: Reads reminders aloud until muted.
- **MySQL Integration**: Stores reminders in a MySQL database.
- **Frequency Options**: Supports one-time reminders and daily recurring reminders.
- **Choose reminder date and time**: Set the reminder time using and date using a date picker.

## Requirements

- Python 3.x
- PyQt5
- MySQL Server
- `pyttsx3` library for text-to-speech
- `mysql-connector-python` for MySQL database connection

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/1337haxx0r/EzReminder.git
   cd EzReminder
   ```

2. Install the required Python packages:
   ```bash
   pip install pyqt5 pyttsx3 mysql-connector-python
   ```

3. Set up the MySQL database:
   - Create a database named `reminders_db`.
   - Create the `reminders` table using the following schema:
     ```sql
     CREATE TABLE `reminders` (
       `id` int(11) NOT NULL AUTO_INCREMENT,
       `text` varchar(255) NOT NULL,
       `frequency` enum('one-time','24hr') NOT NULL,
       `time` bigint(20) NOT NULL,
       PRIMARY KEY (`id`)
     ) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8;
     ```

4. Update the MySQL connection settings in the `main.py` file:
   ```python
   db_config = {
       'user': 'your_username',
       'password': 'your_password',
       'host': 'localhost',
       'database': 'reminders_db',
       'charset': 'utf8'
   }
   ```

## Usage

Run the application:
```bash
python main.py
```

### Adding Reminders

1. Use the UI to add a new reminder.
2. Enter the reminder text.
3. Select the frequency (`one-time` or `24hr`).
4. Set the reminder time.

### Managing Reminders

- **Mute**: Mute the reminder when it goes off.
- **Delete**: One-time reminders are automatically removed after being muted. Daily reminders will go off at the same time the next day.

## Contributing

1. Fork the repository.
2. Create your feature branch:
   ```bash
   git checkout -b feature/your-feature
   ```
3. Commit your changes:
   ```bash
   git commit -m 'Add some feature'
   ```
4. Push to the branch:
   ```bash
   git push origin feature/your-feature
   ```
5. Open a pull request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [PyQt5](https://pypi.org/project/PyQt5/)
- [pyttsx3](https://pypi.org/project/pyttsx3/)
- [mysql-connector-python](https://pypi.org/project/mysql-connector-python/)

