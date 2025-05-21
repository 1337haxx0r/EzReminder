import requests
from tkinter import messagebox
from config.version import __version__

def check_for_updates(app_config, progressbar=None, root=None):
    try:
        response = requests.get("https://api.github.com/repos/1337haxx0r/EzReminder/releases/latest")
        data = response.json()
        latest_version = data["tag_name"].lstrip("v")

        if latest_version != __version__:
            download_url = data["html_url"]  # or assets[0]["browser_download_url"]
            messagebox.showinfo(
                "Update Available",
                f"A new version (v{latest_version}) is available.\nYou are using v{__version__}.\n\nVisit:\n{download_url}"
            )
        else:
            messagebox.showinfo("Up to Date", f"You are running the latest version (v{__version__}).")
    except Exception as e:
        messagebox.showerror("Update Error", f"Could not check for updates:\n{e}")
