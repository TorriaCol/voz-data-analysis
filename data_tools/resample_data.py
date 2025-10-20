import os
import pandas as pd

import deployment_sets as sets
import my_setup as my

os.chdir(os.path.dirname(os.path.abspath(__file__)))
input_folder_path = my.deployment_2023_path()

### 2023 DEPLOYMENT DEVICES
input_files = sets.files_2023()

### 2025 DEPLOYMENT DEVICES
# input_files = sets.files_2025()

for input_file in input_files:
    # Construct the full path to the CSV file
    input_path = os.path.join(input_folder_path, input_file)

    df = pd.read_csv(input_path)
    df['date_time'] = pd.to_datetime(df['unixtime'], unit='s')
    df.set_index('date_time', inplace=True)

    # Resample the dataset to 10-minute averages
    resampled_df = (
    df.resample('1H', label='right', closed='right')  # resample to 1-hour bins
      .mean(numeric_only=True)
      .shift(freq='-30min')  # move timestamps 30 minutes earlier
    )
    resampled_df.dropna(how='all', inplace=True)

    # Reset the index to include the 'date_time' column in the output
    resampled_df.reset_index(inplace=True)

    # Download data to same place
    output_path = os.path.join(input_folder_path, input_file)
    resampled_df.to_csv(output_path, index=False)
    print(f"Resampled dataset saved to '{output_path}'")
