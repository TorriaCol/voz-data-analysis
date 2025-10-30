import os
import pandas as pd
import requests
from datetime import datetime, timedelta

import deployment_sets as sets
import my_setup as my

os.chdir(os.path.dirname(os.path.abspath(__file__)))
output_folder_path = my.raw_2023data_path()

def fetch_github_csv_files(repo_url, folder_path, target_filename=None, branch="main"):
    base_api_url = "https://api.github.com/repos"
    tree_url = f"{base_api_url}/{repo_url}/git/trees/{branch}?recursive=1"

    response = requests.get(tree_url)
    if response.status_code == 200:
        tree = response.json().get("tree", [])
        files = [
            file["path"] for file in tree
            if file["type"] == "blob" and file["path"].startswith(folder_path.strip("/"))
        ]

        if target_filename:
            if isinstance(target_filename, str):
                target_filename = [target_filename]
            files = [f for f in files if f.split("/")[-1] in target_filename]
        else:
            files = [f for f in files if f.endswith(".csv")]

        csv_files = [
            f"https://raw.githubusercontent.com/{repo_url}/{branch}/{file}"
            for file in files
        ]
        return csv_files
    else:
        print(f"Failed to fetch tree from {tree_url}")
        return []


def combine_csv_files_from_urls(csv_urls, output_file):
    dfs = []
    for url in csv_urls:
        try:
            df = pd.read_csv(url)
            dfs.append(df)
            print(f"Loaded {url}")
        except Exception as e:
            print(f"Failed to read {url}: {e}")
    combined_data = pd.concat(dfs, ignore_index=True)
    combined_data.to_csv(output_file, index=False)
    print(f"Saved combined data to {output_file}")


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
    output_combined_csv = "combined_data.csv"

    # ### Uncomment for use with moospmV3_daily folder
    folder_path = "moospmV3_daily"  

# ### Uncomment for use with moospmV3_cal 
#     # folder_path = "moospmV3_cal"  

    # Define start/end dates
    start_date = datetime.strptime("2023-06-07", "%Y-%m-%d")
    end_date = datetime.strptime("2023-06-07", "%Y-%m-%d")

# ### Uncomment for use with moospmV3_daily
    target_filename = [
        f"moospmV3_{(start_date + timedelta(days=i)).strftime('%Y-%m-%d')}.csv"
        for i in range((end_date - start_date).days + 1)
    ]

# ### Uncomment for use with moospmV3_cal
#     # target_filename = [
#     # f"moospmV3_cal_{(start_date + timedelta(days=i)).strftime('%Y-%m-%d')}T{hour:02d}.csv"
#     # for i in range((end_date - start_date).days + 1)
#     # for hour in range(24)
#     # ]

    # Pull list of URLs (but do NOT save them individually)
    csv_files = fetch_github_csv_files(github_repo_url, folder_path, target_filename)

    # Combine directly from GitHub URLs
    output_combined_file = os.path.join(output_folder_path, output_combined_csv)
    combine_csv_files_from_urls(csv_files, output_combined_file)

# ### 2023 DEPLOYMENT DEVICES
    devices = sets.devices_2023()

# ### 2025 DEPLOYMENT DEVICES
#     # devices = sets.devices_2025()

    # Split into per-device files
    segregate_by_device_id(output_combined_file, output_folder_path, devices)
