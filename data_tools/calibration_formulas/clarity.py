import numpy as np
import pandas as pd

class ClarityCalibrator:
    def __init__(self):
        # Load parameters once
        self.low_params, self.high_params = self.get_parameters()

    def calc_dew_point(self, T, rh):
        a = 17.62
        b = 243.12
        gammaTrh = (a*T)/(b+T) + np.log(rh / 100.0)
        Td = (b * gammaTrh) / (a - gammaTrh)
        return Td

    def add_necessary_variables(self, data, sensor):
        data['dew_point'] = self.calc_dew_point(data[sensor["temp"]], data[sensor["rh"]])
        data['temp_minus_dew_point'] = data[sensor["temp"]] - data['dew_point']
        data['pm_rh_interaction'] = data[sensor["pm2.5"]] * data[sensor["rh"]]
        return data

    def get_parameters(self):
        low_df = pd.read_excel(r"../reference_files/2023rawdata/Plantower_calibration_variables/ClarityLowValVars.xlsx")
        low_params = low_df.iloc[0].tolist()
        high_df = pd.read_excel(r"../reference_files/2023rawdata/Plantower_calibration_variables/ClarityHighValVars.xlsx")
        high_params = high_df.iloc[0].tolist()
        return low_params, high_params

    # Calibration helper methods
    def low_val_calibration(self, rh, m_PM25_CF1, m_PM10_CF1, m_PM1_CF1, temp_minus_dew_point, pm_rh_interaction, calibration_params):
        return (rh * calibration_params[0]) + (m_PM25_CF1 * calibration_params[1]) + (m_PM10_CF1 * calibration_params[2]) + \
               (m_PM1_CF1 * calibration_params[3]) + (temp_minus_dew_point * calibration_params[4]) + \
               (pm_rh_interaction * calibration_params[5]) + calibration_params[6]

    def high_val_calibration(self, m_PM25_CF1, calibration_params):
        return m_PM25_CF1 * calibration_params[0]

    def transition_val_calibration(self, omega, PMlow, PMhigh):
        return omega * PMlow + (1 - omega) * PMhigh

    def calibration(self, row):
        pm = row['m_PM25_CF1']

        if pm < 100:
            return self.low_val_calibration(
                row['rh_pms'], row['m_PM25_CF1'], row['m_PM10_CF1'], row['m_PM1_CF1'],
                row['temp_minus_dew_point'], row['pm_rh_interaction'], self.low_params
            )
        elif 100 <= pm <= 300:
            pm_low = self.low_val_calibration(
                row['rh_pms'], row['m_PM25_CF1'], row['m_PM10_CF1'], row['m_PM1_CF1'],
                row['temp_minus_dew_point'], row['pm_rh_interaction'], self.low_params
            )
            pm_high = self.high_val_calibration(row['m_PM25_CF1'], self.high_params)
            return self.transition_val_calibration(row['omega'], pm_low, pm_high)
        else:
            return self.high_val_calibration(row['m_PM25_CF1'], self.high_params)

    def calibrate(self, data):
        data['omega'] = (100 - data["m_PM25_CF1"]) / 200
        data['pm_calibrated_clarity'] = data.apply(self.calibration, axis=1)
        return data
