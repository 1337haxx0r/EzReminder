
# EzReminder

> 🕒 A modern, cross-platform reminder system with voice alerts, persistent configuration, and a clean GUI — now update-safe and auto-repairing.

---

## ✨ Features

- ✅ **Create reminders** with specific date, time, and repeat frequency (`one-time`, `24hr`, `weekly`, `monthly`)
- 🔊 **Voice alerts** via Google Text-to-Speech
- 🔁 **Repeats until muted** — no silent dismissals
- 💬 **In-app status banner** for DB connection issues
- ⚙️ **Settings window** to configure DB and app options
- 📅 **Today-only reminder filtering**
- 🔐 **User config stored safely outside app folder** — survives updates
- 📦 Ready for future packaging as `.exe` or `.app`
- 🔁 GitHub release-based update check (manual or automatic)

---

## 🚀 Getting Started

### 1. Clone the Repo

```bash
git clone https://github.com/your-username/ezreminder.git
cd ezreminder
````

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

Or manually:

```bash
pip install pymysql gTTS pygame ttkbootstrap platformdirs python-dotenv
```

### 3. Create the Database

Create a MySQL database named `reminders` and a table with:

```sql
CREATE TABLE reminders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    text VARCHAR(255),
    frequency ENUM('one-time', '24hr', 'weekly', 'monthly'),
    time BIGINT
);
```

### 4. Run the App

```bash
python main.py
```

---

## 📂 Configuration

Settings are stored in your OS-specific config folder:

* **Windows:** `%APPDATA%/EzReminder/config.json`
* **macOS:** `~/Library/Application Support/EzReminder/config.json`

Update database credentials or app metadata from the **Settings** window in the app.

---
