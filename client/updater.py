import os
import time
import sys
import requests
import shutil
import hashlib
import subprocess

UPDATE_SERVER_URL = "http://localhost:8000/check-update"
CURRENT_VERSION = "v1.0"
DOWNLOAD_PATH = "/tmp/new_version.zip"
BACKUP_PATH = "/tmp/backup.zip"

def check_for_updates():
    # Simulate checking for updates
    print("Checking for updates ...")
    time.sleep(3)
    try:
        # Contact the FastAPI server to get the latest version info
        response = requests.get("http://localhost:8000/check-update")
        response.raise_for_status()
        version_info = response.json()

        if version_info['version'] != CURRENT_VERSION:
            print("Downloading latest update...")
        else:
            print("Latest version running: ", CURRENT_VERSION)

    except requests.exceptions.RequestException as e:
        print(f"Failed to check for updates: {e}")

def get_latest_version_info():
    response = requests.get(UPDATE_SERVER_URL)
    if response.status_code == 200:
        return response.json()
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
    version_info = get_latest_version_info()
    if version_info and version_info['version'] > CURRENT_VERSION:
        download_update(version_info['download_url'])
        if validate_update(version_info['checksum']):
            apply_update()
        else:
            print("Update validation failed.")
    else:
        print("No updates available.")

if __name__ == "__main__":
    main()
