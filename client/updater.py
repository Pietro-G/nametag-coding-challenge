import os
import sys
import requests
import hashlib
import base64
import platform

# Base URL for the API server
API_BASE_URL = "http://localhost:8000"

# Endpoints
API_ENDPOINTS = {
    "check_version": f"{API_BASE_URL}/check-version",
    "get_update": f"{API_BASE_URL}/get-update"
}

# Determine base directory for the updater
if getattr(sys, 'frozen', False):
    # If running from a frozen executable
    BASE_DIR = sys._MEIPASS
else:
    # If running from a script
    BASE_DIR = os.path.dirname(__file__)

VERSION_FILE = os.path.join(BASE_DIR, "version.txt")
DOWNLOAD_PATH = "/tmp/new_version.zip"
CHECKSUM_PATH = "/tmp/new_version.zip.sha256"

def get_os_version():
    system = platform.system()
    if system == "Linux":
        return "linux"
    elif system == "Darwin":
        return "macos"
    elif system == "Windows":
        return "windows"
    else:
        raise ValueError("Unsupported OS. Only Linux, macOS, and Windows are supported.")

def read_current_version():
    try:
        with open(VERSION_FILE, 'r') as file:
            version = file.read().strip()
            return version
    except FileNotFoundError:
        print("Version file not found.")
        return "Unknown version"

def write_current_version(version):
    with open(VERSION_FILE, 'w') as file:
        file.write(version)

def check_for_updates():
    os_version = get_os_version()
    url = f"{API_ENDPOINTS['check_version']}?os_version={os_version}"
    
    print(f"Checking for updates for {os_version} ...")
    try:
        # Contact the FastAPI server to get the latest version info
        response = requests.get(url)
        response.raise_for_status()
        version_info = response.json()

        current_version = read_current_version()
        if version_info['version'] != current_version:
            print("New version available.")
            return version_info
        else:
            print("No updates available.")
            return None

    except requests.exceptions.RequestException as e:
        print(f"Failed to check for updates: {e}")
        return None

def get_update_info():
    os_version = get_os_version()
    url = f"{API_ENDPOINTS['get_update']}?os_version={os_version}"
    
    print(f"Getting update info for {os_version} ...")
    try:
        response = requests.get(url)
        response.raise_for_status()
        update_info = response.json()
        return update_info

    except requests.exceptions.RequestException as e:
        print(f"Failed to get update info: {e}")
        return None

def save_file(base64_data, path):
    print(f"Saving file to {path} ...")
    try:
        file_data = base64.b64decode(base64_data)
        with open(path, 'wb') as file:
            file.write(file_data)
        
        # Verify if the file has been successfully saved
        if os.path.getsize(path) == 0:
            raise Exception(f"Saved file is empty: {path}")

        print(f"File successfully saved as {path}. Size: {os.path.getsize(path)} bytes")
    
    except Exception as e:
        print(f"Error saving file: {e}")
        raise

def download_update(download_base64, checksum_base64):
    save_file(download_base64, DOWNLOAD_PATH)
    save_file(checksum_base64, CHECKSUM_PATH)

def validate_update():
    with open(CHECKSUM_PATH, 'r') as file:
        # Read the line and split by space to get only the checksum part
        checksum_line = file.read().strip()
        expected_checksum = checksum_line.split()[0]  # Take only the checksum part
    
    sha256_hash = hashlib.sha256()
    with open(DOWNLOAD_PATH, 'rb') as file:
        for byte_block in iter(lambda: file.read(4096), b""):
            sha256_hash.update(byte_block)
    
    computed_checksum = sha256_hash.hexdigest()
    print(f"Expected checksum: {expected_checksum}")
    print(f"Computed checksum: {computed_checksum}")

    return computed_checksum == expected_checksum

def main():
    current_version = read_current_version()
    print(f"Current version: {current_version}")
    try:
        version_info = check_for_updates()
        if version_info:
            update_info = get_update_info()
            if update_info:
                download_update(update_info['download_zip'], update_info['checksum_zip'])
                if validate_update():
                    write_current_version(update_info['version'])
                    print(f"Update applied successfully. New version: {update_info['version']}")
                else:
                    print("Update validation failed.")
            else:
                print("Failed to get update info.")
        else:
            print("No updates available.")
    
    except ValueError as e:
        print(e)

if __name__ == "__main__":
    main()
