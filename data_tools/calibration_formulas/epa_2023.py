import pandas as pd

class EPA2023Calibrator:
    def __init__(self):
        # Load parameters once
        self.low_params, self.mid_params, self.high_params = self.get_parameters()

    def get_parameters(self):
        EPALowValParams_df = pd.read_excel(r"../reference_files/2023rawdata/calibration_variables/EPALowValVars.xlsx")
        EPAMidValParams_df = pd.read_excel(r"../reference_files/2023rawdata/calibration_variables/EPAMidValVars.xlsx")
        EPAHighValParams_df = pd.read_excel(r"../reference_files/2023rawdata/calibration_variables/EPAHighValVars.xlsx")
        low = EPALowValParams_df.iloc[0].tolist() # Parameters for low PM
        mid = EPAMidValParams_df.iloc[0].tolist() # Parameters for mid PM
        high = EPAHighValParams_df.iloc[0].tolist() # Parameters for high PM
        return low,mid,high

    def low_val_calibration(self,PMlow, rh, calibration_params):
        return (PMlow * calibration_params[0]) + (rh * calibration_params[1]) + calibration_params[2]

    def mid_val_calibration(self,PMmid, rh, calibration_params):
        PMequation1 = PMmid/20-3/2
        PMequation2 = 1-PMequation1
        return ((PMequation1 * calibration_params[0]) + (PMequation2 * calibration_params[1])) * PMmid + (rh * calibration_params[2]) + calibration_params[3]

    def high_val_calibration(self,PMhigh, rh, calibration_params):
        return (PMhigh * calibration_params[0]) + (rh * calibration_params[1]) + calibration_params[2]

    def calibration(self,row):
        pm = row['m_PM25_ATM']
        
        if pm < 30:
            return self.low_val_calibration(
                pm,
                row['rh_pms'],
                self.low_params
            )
        elif 30 <= pm < 50:
            return self.mid_val_calibration(
                pm,
                row['rh_pms'],
                self.mid_params
            )
        else:  # pm >= 50
            return self.high_val_calibration(
                pm,
                row['rh_pms'],
                self.high_params
            )
        
    def calibrate(self, data):
        data['PM_calibrated_EPA_Piecewise'] = data.apply(self.calibration, axis=1)
        return data