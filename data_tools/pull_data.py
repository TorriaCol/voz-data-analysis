import os
import pandas as pd
import requests
from datetime import datetime, timedelta

import deployment_sets as sets
import my_setup as my

output_folder_path = my.outputpath()

def fetch_github_csv_files(repo_url, folder_path, target_filename=None, branch="main"):
    """
    Fetch CSV file download URLs from a GitHub repo using the tree API (works for large folders).
    
    repo_url: e.g. "QuinnResearch/carbVoz_data"
    folder_path: e.g. "moospmV3_cal"
    target_filename: list of filenames to filter (optional)
    branch: branch name (default = "main")
    """
    base_api_url = "https://api.github.com/repos"
    tree_url = f"{base_api_url}/{repo_url}/git/trees/{branch}?recursive=1"

    response = requests.get(tree_url)
    if response.status_code == 200:
        tree = response.json().get("tree", [])
        
        # Get all files inside folder_path
        files = [
            file["path"] for file in tree
            if file["type"] == "blob" and file["path"].startswith(folder_path.strip("/"))
        ]

        if target_filename:
            if isinstance(target_filename, str):
                target_filename = [target_filename]
            # Keep only exact matches
            files = [f for f in files if f.split("/")[-1] in target_filename]
        else:
            # Keep only CSVs
            files = [f for f in files if f.endswith(".csv")]

        # Convert paths into raw download URLs
        csv_files = [
            f"https://raw.githubusercontent.com/{repo_url}/{branch}/{file}"
            for file in files
        ]

        return csv_files
    else:
        print(f"Failed to fetch tree from {tree_url}")
        return []


def download_and_save_csv(url, output_folder):
    response = requests.get(url)
    if response.status_code == 200:
        file_name = url.split("/")[-1]  # Extract the file name from the URL
        output_file = os.path.join(output_folder, file_name)
        with open(output_file, "w") as f:
            f.write(response.text)
        print(f"Downloaded {file_name}")
    else:
        print(f"Failed to download {url}")

def combine_csv_files(csv_files, input_folder, output_file):
    try:
        combined_data = pd.concat([pd.read_csv(os.path.join(input_folder, file.split("/")[-1])) for file in csv_files], ignore_index=True)
        combined_data.to_csv(output_file, index=False)
        print(f"Combined {len(csv_files)} CSV files into {output_file}")
    except Exception as e:
        print(f"Error during data combination: {e}")

def segregate_by_device_id(combined_file, output_folder, devices=None):
    try:
        combined_data = pd.read_csv(combined_file)
        for device_id, data in combined_data.groupby("coreid"):
            if devices and device_id in devices:
                device_name = devices[device_id]
            else:
                device_name = f"device_{device_id}"
            output_file = os.path.join(output_folder, f"{device_name}.csv")
            data.to_csv(output_file, index=False)
            print(f"Saved data for device {device_id} ({device_name}) to {output_file}")
    except Exception as e:
        print(f"Error during data segregation: {e}")

if __name__ == "__main__":
    github_repo_url = "QuinnResearch/carbVoz_data" 

### Uncomment for use with moospmV3_daily folder
#    folder_path = "moospmV3_daily"  

### Uncomment for use with moospmV3_cal 
    folder_path = "moospmV3_cal"  

    output_combined_csv = "combined_data.csv" 

# Define start and end dates
    start_date = datetime.strptime("2025-07-19", "%Y-%m-%d")
    end_date = datetime.strptime("2025-07-20", "%Y-%m-%d")

### Uncomment for use with moospmV3_daily
    # target_filename = [
    #     f"moospmV3_{(start_date + timedelta(days=i)).strftime('%Y-%m-%d')}.csv"
    #     for i in range((end_date - start_date).days + 1)
    # ]

### Uncomment for use with moospmV3_cal
    target_filename = [
    f"moospmV3_cal_{(start_date + timedelta(days=i)).strftime('%Y-%m-%d')}T{hour:02d}.csv"
    for i in range((end_date - start_date).days + 1)
    for hour in range(24)
    ]

# Fetch CSV files from GitHub and download them
    csv_files = fetch_github_csv_files(github_repo_url, folder_path, target_filename)
    for file_url in csv_files:
        download_and_save_csv(file_url, output_folder_path)

# Combine downloaded CSV files and save the result
    output_combined_file = os.path.join(output_folder_path, output_combined_csv)
    combine_csv_files(csv_files, output_folder_path, output_combined_file)

### 2023 DEPLOYMENT DEVICES
    # devices = sets.files_2023()

### 2025 DEPLOYMENT DEVICES
    devices = sets.devices_2025()
    segregate_by_device_id(output_combined_file, output_folder_path, devices)

