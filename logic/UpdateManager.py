import requests
from tkinter import messagebox
from packaging.version import Version, InvalidVersion
from config.version import __version__

RELEASES_API_URL = "https://api.github.com/repos/1337haxx0r/EzReminder/releases/latest"

def check_for_updates(app_config, progressbar=None, root=None):
    try:
        response = requests.get(RELEASES_API_URL, timeout=10)

        if response.status_code == 404:
            messagebox.showinfo(
                "Up to Date",
                f"You are running v{__version__}.\n\nNo published releases were found on GitHub yet."
            )
            return

        response.raise_for_status()
        data = response.json()

        latest_version = data["tag_name"].removeprefix("v")
        download_url = data["html_url"]

        try:
            is_newer = Version(latest_version) > Version(__version__)
        except InvalidVersion:
            is_newer = latest_version != __version__

        if is_newer:
            messagebox.showinfo(
                "Update Available",
                f"A new version (v{latest_version}) is available.\nYou are using v{__version__}.\n\nVisit:\n{download_url}"
            )
        else:
            messagebox.showinfo("Up to Date", f"You are running the latest version (v{__version__}).")
    except requests.RequestException as e:
        messagebox.showerror("Update Error", f"Could not reach GitHub:\n{e}")
    except (KeyError, ValueError) as e:
        messagebox.showerror("Update Error", f"Unexpected response from GitHub:\n{e}")
