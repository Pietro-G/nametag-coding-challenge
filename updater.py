import os
import sys
import requests
import hashlib
import base64
import platform
import zipfile
import shutil
import stat
import io

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

VERSION_FILE = os.path.join(BASE_DIR, "client/version.txt")
EXTRACTED_DIR = os.path.join(BASE_DIR, "client/dist")

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
            sys.exit(0)  # Exit with code 0 to indicate no updates

    except requests.exceptions.RequestException as e:
        print(f"Failed to check for updates: {e}")
        sys.exit(1)

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
        sys.exit(1)

def validate_update(file_data, expected_checksum):
    sha256_hash = hashlib.sha256()
    for byte_block in iter(lambda: file_data.read(4096), b""):
        sha256_hash.update(byte_block)
    
    computed_checksum = sha256_hash.hexdigest()
    print(f"Expected checksum: {expected_checksum}")
    print(f"Computed checksum: {computed_checksum}")

    return computed_checksum == expected_checksum

def download_update(download_base64, checksum_base64):
    print(f"Downloading update ...")
    file_data = base64.b64decode(download_base64)
    checksum_data = base64.b64decode(checksum_base64).decode()

    expected_checksum = checksum_data.strip().split()[0]
    
    if validate_update(io.BytesIO(file_data), expected_checksum):
        print("Checksum validation successful.")
        return io.BytesIO(file_data)
    else:
        print("Checksum validation failed.")
        sys.exit(1)

def extract_zip(file_data):
    print(f"Extracting update to dist directory ({EXTRACTED_DIR}) ...")
    try:
        # Clear the dist directory before extraction
        if os.path.isdir(EXTRACTED_DIR):
            shutil.rmtree(EXTRACTED_DIR)
        os.makedirs(EXTRACTED_DIR)

        with zipfile.ZipFile(file_data, 'r') as zip_ref:
            zip_ref.extractall(EXTRACTED_DIR)
        
        print(f"Update extracted successfully to dist directory ({EXTRACTED_DIR}).")

        # Make extracted files executable based on OS
        os_version = get_os_version()
        for root, dirs, files in os.walk(EXTRACTED_DIR):
            for file in files:
                file_path = os.path.join(root, file)
                if os_version == "linux" or os_version == "macos":
                    st = os.stat(file_path)
                    os.chmod(file_path, st.st_mode | stat.S_IEXEC)
                elif os_version == "windows":
                    pass  # Windows handles executability differently

    except Exception as e:
        print(f"Error extracting zip file: {e}")
        sys.exit(1)

def main():
    current_version = read_current_version()
    print(f"Current version: {current_version}")
    try:
        version_info = check_for_updates()
        if version_info:
            update_info = get_update_info()
            if update_info:
                file_data = download_update(update_info['download_zip'], update_info['checksum_zip'])
                extract_zip(file_data)
                write_current_version(update_info['version'])
                print("Update has been applied!")
            else:
                print("Failed to get update info.")
                sys.exit(1)
    except ValueError as e:
        print(e)
        sys.exit(1)

if __name__ == "__main__":
    main()
