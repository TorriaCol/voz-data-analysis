import pandas as pd

"""
Removes rows from a CSV file where a specified header's value matches a given value.

Args:
    input_csv_path (str): The path to the input CSV file.
    output_csv_path (str): The path to save the modified CSV file.
    header_name (str): The name of the header (column) to check.
    value_to_remove: The value in the specified header that, if matched,
                        will cause the row to be removed.
"""
# Read the CSV file into a pandas DataFrame
path = "./VOZ_Box_Avenal_mod_calibrated.csv"
df = pd.read_csv(path)

# Filter out rows where the specified header's value matches value_to_remove
# This creates a new DataFrame containing only the rows that do NOT match the condition
df_filtered = df[['date_time','unixtime','m_PM25_CF1','m_PM25_ATM','tempC_pms','rh_pms','temp_C','rh','lat','lon','PM_calibrated_ClarityRemake','PM_calibrated_Basic','omega','PM_calibrated_Clarity','PM_calibrated_EPA_Piecewise','PM_calibrated_EPA_Barkjohn']]

# Save the filtered DataFrame back to a new CSV file
df_filtered.to_csv(path, index=False)
print(f"Rows removed successfully. Modified CSV saved to: {path}")