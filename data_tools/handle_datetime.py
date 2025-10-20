import pandas as pd

#Assumptions:
#   Data has been resampled to hourly
#   date_time is in UTC
def create_utc_for_voz(data):
    data['date_time'] = pd.to_datetime(data['date_time'])
    data.set_index('date_time',inplace=True)
    return data

# Works if data is in PST (as of now, all data downloaded from CARB is PST)
def create_utc_for_CARB(data):
    data['date_time'] = pd.to_datetime(
        data['date'].astype(str) + ' ' + data['start_hour'].astype(str) + ':30'
    )
    data['date_time'] = data['date_time'] + pd.Timedelta(hours=8)
    data.set_index('date_time', inplace=True)
    return data

def utc_to_CA(data):
    data.index = pd.to_datetime(data.index, utc=True)
    data.index = data.index.tz_convert('US/Pacific')
    data.index = data.index.tz_localize(None)
    return data

def create_standard_datetime(data):
    data['date_time'] = pd.to_datetime(data['date_time'])
    data.set_index('date_time', inplace=True)
    return data
    