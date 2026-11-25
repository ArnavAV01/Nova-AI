import os
import time
import shutil
from datetime import datetime

def move_todays_downloaded_pdf(destination_dir = None):
    # Default Downloads directory
    downloads_dir = os.path.expanduser("~/Downloads")

    # Destination directory (default path)
    if destination_dir is None:
        destination_dir = destination_dir

    # Ensure the destination directory exists
    try:
        if not os.path.exists(destination_dir):
            os.makedirs(destination_dir)
    except Exception as e:
        return f"Failed to create destination directory: {destination_dir}. Error: {e}"

    # Get the current date in YYYY-MM-DD format
    today_date = datetime.now().date()

    # Get a list of all files in the Downloads directory
    files = os.listdir(downloads_dir)

    # Get the full path for each file
    full_paths = [os.path.join(downloads_dir, file) for file in files]

    # Filter to include only PDF files downloaded today
    pdf_files_today = [
        file for file in full_paths
        if os.path.isfile(file) and file.lower().endswith('.pdf') and
        datetime.fromtimestamp(os.path.getmtime(file)).date() == today_date
    ]

    # Ensure there is at least one PDF downloaded today
    if not pdf_files_today:
        return "No PDF files downloaded today."

    # Move the first PDF file to the destination directory
    pdf_to_move = pdf_files_today[0]

    # Build the destination path
    destination_path = os.path.join(destination_dir, os.path.basename(pdf_to_move))

    try:
        shutil.move(pdf_to_move, destination_path)
    except Exception as e:
        return f"Failed to move file: {pdf_to_move} to {destination_path}. Error: {e}"

    return f"Moved: {pdf_to_move} to {destination_path}"


def wait_for_download_completion(timeout=120):
    print("Waiting for today's download to complete...")
    download_directory = os.path.expanduser("~/Downloads")  # Adjust if downloads are saved in a different directory
    today = datetime.now().date()  # Get today's date
    start_time = time.time()
    downloaded_file = None
    stable_file_detected = False

    while time.time() - start_time <= timeout:
        # Get the list of files in the directory
        files = os.listdir(download_directory)
        # Filter files for today's downloads and ignore temporary extensions
        completed_files = [
            file for file in files
            if not file.endswith((".crdownload", ".part", ".tmp")) and
            datetime.fromtimestamp(os.path.getmtime(os.path.join(download_directory, file))).date() == today
        ]

        # If any non-temporary file is detected, check its stability
        if completed_files:
            downloaded_file = os.path.join(download_directory, completed_files[0])
            initial_size = os.path.getsize(downloaded_file)
            time.sleep(2)  # Wait to check if the file size changes
            current_size = os.path.getsize(downloaded_file)

            if initial_size == current_size:  # File size is stable
                stable_file_detected = True
                break
            else:
                print(f"File size still changing for: {completed_files[0]}")
        else:
            # print("No completed files detected yet for today...")
            pass
        
        time.sleep(1)  # Check every second

    if stable_file_detected:
        print(f"Download completed for: {downloaded_file}")
        return True
    else:
        print("Download did not complete in the expected time.")
        return False
