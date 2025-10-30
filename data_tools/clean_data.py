import numpy as np

def clean(data, column):
    # Apply outlier elimination
    data = _eliminate_outliers(data, column)
    cleaned_data = data.dropna(how='all')
    return cleaned_data

def _eliminate_outliers(data, column, z_threshold=5):
        z_scores = np.abs((data[column] - data[column].mean()) / data[column].std())
        filtered_data = data[(z_scores < z_threshold)]
        return filtered_data

def eliminate_waste_data(data,sensor):
    desired = ['unixtime',sensor["pm2.5"],sensor['pm1'],sensor['pm10'],sensor['temp'],sensor['rh'],'temp_C','rh','lat','lon','reference']
    columns = [col for col in desired if col in data.columns]
    return data[columns]
