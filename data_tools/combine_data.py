import pandas as pd
import numpy as np
import sys
import os

sys.path.append(os.path.abspath(".."))
from data_tools import process_data as process
from data_tools import handle_datetime
from data_tools import clean_data


class CreateTrainingandTestData:
    def __init__(self):
        self.variable = ""
        self.sensor_id = ""
        self.voz_data = None

    def set_calibration_parameters(self,variable,sensor_id,voz_data):
        self.variable = variable
        self.sensor_id = sensor_id
        self.voz_data = voz_data

    def get_combined_data(self,training_date,testing_date,calibration_reference,deployment_reference):
        training = self._get_training_data(training_date,calibration_reference,deployment_reference)
        testing = self._get_testing_data(testing_date,deployment_reference,self.voz_data)
        all = self._get_all_data(testing,training)
        return training,all

    def _get_training_data(self,training_date, calibration_reference, deployment_reference):
        precal_voz_data = self.voz_data[(self.voz_data.index >= training_date[0]) & (self.voz_data.index <= training_date[1])]

        # Merge the datasets for the first dataset
        precal_all_data = precal_voz_data.join(calibration_reference, how='inner')
        
        postcal_voz_data = self.voz_data[(self.voz_data.index >= training_date[2]) & (self.voz_data.index <= training_date[3])]

        # Merge the datasets for the second dataset
        if self.sensor_id == "Tranquility":
            postcal_all_data = postcal_voz_data.join(deployment_reference, how='inner') # Use for Tranquility site
        else:
            postcal_all_data = postcal_voz_data.join(calibration_reference, how='inner') # Use for all sites except Tranquility
        all_training_data = pd.concat([precal_all_data, postcal_all_data])

        # all_training_data['day_counter'] = (all_training_data.index - all_training_data.index[0]).days+1
        # all_training_data['month'] = all_training_data.index.month
        # all_training_data['week'] = all_training_data.index.isocalendar().week
        
        all_training_data = clean_data.clean(all_training_data,self.variable)

        return all_training_data

    def _get_testing_data(self,testing_date,deployment_reference,voz_data):
        voz_test1 = voz_data[(voz_data.index >= testing_date[0]) & (voz_data.index <= testing_date[1])] #Trial 1 Period
        voz_test2 = voz_data[(voz_data.index >= testing_date[2]) & (voz_data.index <= testing_date[3])] #Trial 2 Period
        voz_testing_data = pd.concat([voz_test1, voz_test2])
        
        all_testing_data = voz_testing_data.join(deployment_reference, how='inner')
        # all_testing_data = clean_data.clean(all_testing_data,self.variable)

        return all_testing_data

    def _get_all_data(self,all_testing_data,all_training_data):
        all_data = pd.concat([all_testing_data,all_training_data]).sort_index()
        return all_data
    
    # Cuts data into subsections as specified by dates. 
    # Dates should be ordered as following: [start_date_1, end_date_1, start_date_2, end_date_2,...] so on
    def subsection(self,data,dates):
        if len(dates) % 2 != 0:
            raise ValueError("Dates list must contain pairs of start and end dates.")

        cut_sections = []
        for i in range(0, len(dates), 2):
            start, end = pd.to_datetime(dates[i]), pd.to_datetime(dates[i + 1])
            section = data[(data.index >= start) & (data.index <= end)]
            cut_sections.append(section)

        # Combine all sections
        subsection_data = pd.concat(cut_sections).sort_index()
        return subsection_data
    
    