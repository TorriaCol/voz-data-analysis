import pandas as pd

def get_parameters():
    EPA2021Params_df = pd.read_excel(r"../reference_files/2023rawdata/Plantower_calibration_variables/EPA2021Vars.xlsx")
    params = EPA2021Params_df.iloc[0].tolist() 
    return params

def calibration(PM, rh, calibration_params):
    return (PM * calibration_params[0]) + (rh * calibration_params[1]) + calibration_params[2]

def calibrate(data):
    params = get_parameters()
    data['pm_calibrated_epa_barkjohn'] = calibration(data['m_PM25_CF1'], data['rh_pms'], params)
    return data