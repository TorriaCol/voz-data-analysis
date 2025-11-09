import numpy as np

def eliminate_outliers(data, column, z_threshold=5):
        z_scores = np.abs((data[column] - data[column].mean()) / data[column].std())
        filtered_data = data[(z_scores < z_threshold)]
        return filtered_data

def eliminate_waste_data_pm(data, sensor):
    desired = [
        'unixtime', sensor["pm2.5"], sensor['pm1'], sensor['pm10'],
        sensor['temp'], sensor['rh'], 'temp_C', 'rh',
        'lat', 'lon', 'reference'
    ]
    columns = [col for col in desired if col in data.columns]
    subset_cols = [col for col in columns if col != 'reference']
    cleaned_data = data.dropna(subset=subset_cols)
    return cleaned_data[columns]

def eliminate_waste_data_o3(data):
    desired = [
        'unixtime', 'temp_C', 'rh', 'o3',
        'lat', 'lon', 'reference'
    ]
    columns = [col for col in desired if col in data.columns]
    subset_cols = [col for col in columns if col != 'reference']
    cleaned_data = data.dropna(subset=subset_cols)
    return cleaned_data[columns]
