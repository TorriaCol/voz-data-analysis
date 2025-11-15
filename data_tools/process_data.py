import pandas as pd
from . import handle_datetime

def ref_data(path):
    ref_data = pd.read_csv(path)
    ref_data = handle_datetime.create_utc_for_CARB(ref_data)
    ref_data['reference'] = ref_data['value']
    ref_data = ref_data[['reference']]
    return ref_data

def raw_voz_data(path):
    voz_data = pd.read_csv(path)
    voz_data = handle_datetime.create_utc_for_voz(voz_data)
    return voz_data

def aqlite_data(path):
    data = pd.read_csv(path)
    data = data.rename(columns={'Ozone-1578:OZONE_date': 'date_time', 'Ozone-1578:OZONE_value': 'o3'})
    data = data[['date_time', 'o3']]
    data = handle_datetime.create_standard_datetime(data)
    return data

def standard_data(path):
    data = pd.read_csv(path)
    data = handle_datetime.create_standard_datetime(data)
    return data