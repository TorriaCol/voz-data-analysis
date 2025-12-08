import numpy as np

def eliminate_outliers(data, column, z_threshold=8):
    # 1. Z-score for recorded values only (your existing method)
    data['z_recorded'] = (data[column] - data[column].mean()) / data[column].std()

    # 2. Compute residuals (difference between recorded and reference)
    data['residual'] = data[column] - data['reference']

    # 3. Z-score of residuals to catch misalignment outliers
    data['z_residual'] = (data['residual'] - data['residual'].mean()) / data['residual'].std()

    # 4. Keep rows where both z-scores are within threshold
    data_clean = data[(data['z_recorded'].abs() <= z_threshold) & (data['z_residual'].abs() <= z_threshold)]
    return data_clean

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
        'unixtime', 'temp_C', 'rh', 'o3', 'm_PM25_CF1', 'm_PM10_CF1',
        'lat', 'lon', 'reference', 'seasonal_bias', 'week'
    ]
    columns = [col for col in desired if col in data.columns]
    subset_cols = [col for col in columns if col != 'reference']
    cleaned_data = data.dropna(subset=subset_cols)
    cleaned_data = cleaned_data[cleaned_data['o3'] > 10]  # Assuming ozone values below 0 are outliers
    return cleaned_data[columns]
