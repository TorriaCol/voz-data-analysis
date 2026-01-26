import numpy as np

def eliminate_outliers(data, column, z_threshold=3):
    data = data.copy()

    # 0. Hard bounds backup filter
    in_physical_range = data[column].between(0, 100)

    # 1. Compute residuals where possible
    data['residual'] = data[column] - data['reference']

    # 2. Z-score of residuals (NaNs ignored)
    data['z_residual'] = (data['residual'] - data['residual'].mean()) / data['residual'].std()

    # 3. Mask for rows with reference
    has_ref = data['reference'].notna()

    # 4. Combine rules:
    #    - must be in physical range
    #    - and either:
    #         * no reference (skip z test)
    #         * or z_residual within threshold
    data_clean = data[
        in_physical_range &
        ( (~has_ref) | (data['z_residual'].abs() <= z_threshold) )
    ]

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
