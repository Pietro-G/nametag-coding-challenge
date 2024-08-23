import os
import time
import sys
import requests
import shutil
import hashlib
import subprocess
import platform

# Base URL for the API server
API_BASE_URL = "http://localhost:8000"

# Endpoints
API_ENDPOINTS = {
    "check_update": f"{API_BASE_URL}/get-update",
    "check_version": f"{API_BASE_URL}/check-version"
}

VERSION_FILE = "version.txt"
DOWNLOAD_PATH = "/tmp/new_version.zip"
BACKUP_PATH = "/tmp/backup.zip"

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
    if os.path.exists(VERSION_FILE):
        with open(VERSION_FILE, 'r') as file:
            return file.read().strip()
    return None

def write_current_version(version):
    with open(VERSION_FILE, 'w') as file:
        file.write(version)

def check_for_updates():
    os_version = get_os_version()
    url = f"{API_ENDPOINTS['check_update']}?os_version={os_version}"
    
    print(f"Checking for updates for {os_version} ...")
    time.sleep(3)
    try:
        # Contact the FastAPI server to get the latest version info
        response = requests.get(url)
        response.raise_for_status()
        version_info = response.json()

        current_version = read_current_version()
        if version_info['version'] != current_version:
            print("Downloading latest update...")
            return version_info
        else:
            print("Latest version running: ", current_version)
            return None

    except requests.exceptions.RequestException as e:
        print(f"Failed to check for updates: {e}")
        return None

def download_update(download_url):
    response = requests.get(download_url, stream=True)
    with open(DOWNLOAD_PATH, 'wb') as file:
        for chunk in response.iter_content(chunk_size=8192):
            file.write(chunk)

def validate_update(expected_checksum):
    sha256_hash = hashlib.sha256()
    with open(DOWNLOAD_PATH, 'rb') as file:
        for byte_block in iter(lambda: file.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest() == expected_checksum

def apply_update():
    shutil.copyfile(sys.argv[0], BACKUP_PATH)  # Backup current version
    shutil.unpack_archive(DOWNLOAD_PATH, os.path.dirname(sys.argv[0]))
    os.remove(DOWNLOAD_PATH)
    subprocess.Popen([sys.executable] + sys.argv)  # Restart application
    sys.exit()

def main():
    try:
        version_info = check_for_updates()
        if version_info:
            download_update(version_info['download_url'])
            if validate_update(version_info['checksum']):
                apply_update()
                write_current_version(version_info['version'])
            else:
                print("Update validation failed.")
        else:
            print("No updates available.")
    except ValueError as e:
        print(e)
        sys.exit(1)

if __name__ == "__main__":
    main()
