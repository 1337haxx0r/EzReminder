import os
import sys
import zipfile
import requests
import time
from tkinter import messagebox
import json

def check_for_updates(config, progressbar, root):
    # Get the latest release from your GitHub repository
    response = requests.get('https://api.github.com/repos/1337haxx0r/EzReminder/releases/latest', stream=True)

    # Get the current version of your app
    current_version = config['version']

    # Check if the request was successful
    latest_release = response.json()

    # Get the tag name (version number) of the latest release
    latest_version = latest_release['tag_name']

    print("Checking for updates...")

    # Compare the latest version with your app's current version
    if latest_version > current_version:
        print("Update available!")

        # Get the download URL of the latest release
        download_url = latest_release['assets'][0]['browser_download_url']
        response = requests.get(download_url, stream=True)

        # Define the path of the new zip file
        new_zip_path = os.path.join(get_exe_directory(), f'ReminderApp-{latest_version}.zip')

        # Get the total file size
        file_size = int(response.headers.get('Content-Length', 0))

        # Initialize the progress bar
        progressbar['maximum'] = file_size

        # Download the update
        with open(new_zip_path, 'wb') as update_file:
            for data in response.iter_content(1024):
                # Write data read to the file
                update_file.write(data)

                # Update the progress bar
                progressbar['value'] += len(data)
                root.update()

        print("Update downloaded")

        # Define the path of the directory where the update will be unpacked
        unpack_dir = os.path.join(get_exe_directory(), f'ReminderApp-{latest_version}')

        # Create the directory if it does not exist
        os.makedirs(unpack_dir, exist_ok=True)

        # Unzip the update
        with zipfile.ZipFile(new_zip_path, 'r') as zip_ref:
            zip_ref.extractall(unpack_dir)
            print("Unzipped the update.")

        # Try to delete the zip file
        for _ in range(5):  # Retry up to 5 times
            try:
                os.remove(new_zip_path)
                print("Deleted the zip file.")
                break
            except PermissionError:
                print("Waiting for file to be released...")
                time.sleep(1)  # Wait for 1 second
        else:
            print("Failed to delete the zip file.")

        update_version_in_config(latest_version)
        progressbar.grid_forget()
        messagebox.showinfo("Update", "Update has been downloaded. Please replace all necessary files and restart the application.")

    elif latest_version == config['version']:
        messagebox.showinfo("Check updates", "You are already using the latest version: " + current_version)


def get_exe_directory():
    # Get the absolute path of the current .exe file
    current_exe_path = os.path.abspath(sys.argv[0])

    # Get the directory where the .exe file was run
    exe_directory = os.path.dirname(current_exe_path)

    return exe_directory

def update_version_in_config(latest_version):
    # Open the config.json file in read mode
    with open('config.json', 'r') as config_file:
        config_data = json.load(config_file)

    # Update the app.version value
    config_data['app']['version'] = latest_version

    # Open the config.json file in write mode
    with open('config.json', 'w') as config_file:
        json.dump(config_data, config_file, indent=4)
