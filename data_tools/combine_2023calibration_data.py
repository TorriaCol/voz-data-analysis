import pandas as pd
import numpy as np
import sys
import os

sys.path.append(os.path.abspath(".."))
from data_tools import process_data as process
from data_tools import handle_datetime

def for_calibration(pmdata, sensor_id, training_date):

    # Assuming you have loaded the first dataset and its reference data
    sensor_file = rf"../reference_files/2023rawdata/{sensor_id}.csv"
    reference_file_1 = rf"../reference_files/PM25HR_PICKDATA_2023-12-31-Fresno.csv"
    if sensor_id == "Tranquility":
        reference_file_2 = rf"../reference_files/PM25HR_PICKDATA_2023-12-31-Tranquility.csv"
    else:
        reference_file_2 = rf"../reference_files/PM25HR_PICKDATA_2023-12-31-Fresno.csv"

    reference_data = process.ref_data(reference_file_1)
    deployment_ref = process.ref_data(reference_file_2)
    PM25_data_1 = process.raw_voz_data(sensor_file)
    PM25_data_1 = PM25_data_1[(PM25_data_1.index >= training_date[0]) & (PM25_data_1.index <= training_date[1])]

    # Merge the datasets for the first dataset
    merged_data_1 = PM25_data_1.join(reference_data, how='inner')

    PM25_data_2 = process.raw_voz_data(sensor_file)
    PM25_data_2 = PM25_data_2[(PM25_data_2.index >= training_date[2]) & (PM25_data_2.index <= training_date[3])]

    # Merge the datasets for the second dataset
    if sensor_id == "Tranquility":
        merged_data_2 = PM25_data_2.join(deployment_ref, how='inner') # Use for Tranquility site
    else:
        merged_data_2 = PM25_data_2.join(reference_data, how='inner') # Use for all sites except Tranquility
    merged_data_combined = pd.concat([merged_data_1, merged_data_2])

    #Convert all data to Pacific Time for later use
    merged_data_combined = handle_datetime.utc_to_CA(merged_data_combined)
    reference_data = handle_datetime.utc_to_CA(reference_data)
    deployment_ref = handle_datetime.utc_to_CA(deployment_ref)

    merged_data_combined['day_counter'] = (merged_data_combined.index - merged_data_combined.index[0]).days+1
    merged_data_combined['month'] = merged_data_combined.index.month
    merged_data_combined['week'] = merged_data_combined.index.isocalendar().week

    # Function to eliminate outliers using Z-score
    def eliminate_outliers(data, column, z_threshold=3):
        z_scores = np.abs((data[column] - data[column].mean()) / data[column].std())
        filtered_data = data[(z_scores < z_threshold)]
        return filtered_data

    # Define the Z-score threshold for outlier removal
    z_threshold = 1

    # Apply outlier elimination to the 'o3' column in the merged data
    merged_data_combined = eliminate_outliers(merged_data_combined, pmdata, z_threshold)

    return merged_data_combined, deployment_ref, reference_data