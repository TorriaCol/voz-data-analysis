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

def standard_data(path):
    data = pd.read_csv(path)
    data = handle_datetime.create_standard_datetime(data)
    return data