import os
import glob
import json
from datetime import datetime, timedelta
from logger_config import *


class ZapAlertExporter:
    def __init__(self, file_path):
        self.file_path = file_path
        self.alerts = []

    def read_json_file(self):
        try:
            with open(self.file_path, "r") as file:
                json_data = file.read()
                if not json_data:
                    raise ValueError("Empty JSON data in file '{0}'".format(self.file_path))
                data = json.loads(json_data)
                sites = data.get("site", [])
                for site in sites:
                    alerts = site.get("alerts", [])
                    self.alerts.extend(alerts)
        except FileNotFoundError:
            logger.error("File '%s' not found.", self.file_path)
            raise
        except json.JSONDecodeError:
            logger.error("Invalid JSON data in file '%s'.", self.file_path)
            raise
        except ValueError as ve:
            logger.error(str(ve))
            raise
        except Exception as e:
            logger.error("An error occurred while reading the file: %s", str(e))
            raise
        return self.alerts

def get_creation_time(file_path):
    stat_info = os.stat(file_path)
    return stat_info.st_birthtime

def collect_newest_json_files(parent_folder):
    last_created_at_file = os.path.join(parent_folder, "lastCreatedAt.txt")
    current_time = datetime.now()

    if not os.path.exists(last_created_at_file):
        last_created_at = current_time.timestamp()
        with open(last_created_at_file, "w") as f:
            f.write(str(last_created_at))
    else:
        try:
            with open(last_created_at_file, "r") as f:
                last_created_at = float(f.read().strip())
        except (FileNotFoundError, ValueError):
            last_created_at = current_time.timestamp()

    # Calculate the minimum creation time based on last_created_at + 1 second
    min_creation_time = current_time - timedelta(seconds=(current_time.timestamp() - last_created_at + 1))

    website_folders = [name for name in os.listdir(parent_folder) if
                       os.path.isdir(os.path.join(parent_folder, name))]
    newest_files = []

    # Iterate over each website folder and collect the newest JSON files
    for website_folder in website_folders:
        website_path = os.path.join(parent_folder, website_folder)
        json_files = glob.glob(os.path.join(website_path, "*.json"))
        # Filter the files based on their creation time
        filtered_files = [file for file in json_files if
                          get_creation_time(file) >= min_creation_time.timestamp()]

        newest_file = max(filtered_files, key=get_creation_time, default=None)

        if newest_file:
            newest_files.append(newest_file)
            with open(last_created_at_file, "w") as f:
                f.write(str(current_time.timestamp()))
    if not newest_file:
        logger.info("No new JSON files")

    return newest_files
