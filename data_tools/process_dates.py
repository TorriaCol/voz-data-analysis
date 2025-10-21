import pandas as pd

def training(sensor_id):
    # Read date_file
    dates = read_date_file(sensor_id)

    # Assign training dates
    training_dates = [
        dates['newprestart'],
        dates['newpreend'],
        dates['newpoststart'],
        dates['newpostend']
    ]

    return training_dates

def testing(sensor_id):
    # Read date_file
    dates = read_date_file(sensor_id)

    # Assign testing dates
    testing_dates = [
        dates['Trial1Start'],
        dates['Trial1End'],
        dates['Trial2Start'],
        dates['Trial2End'],
    ]

    return testing_dates

def read_date_file(sensor_id):
    date_file = rf"../reference_files/2023_deployment_dates.xlsx"
    all_dates = pd.read_excel(date_file, sheet_name=1)
    dates = all_dates.loc[all_dates['sensor_id'] == sensor_id].squeeze()
    date_columns = [col for col in dates.index if col not in ['sensor_id', 'PreNumDays', 'PostNumDays', 'WithFEM']]
    dates[date_columns] = pd.to_datetime(dates[date_columns])
    return dates