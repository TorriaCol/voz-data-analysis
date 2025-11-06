import pandas as pd
import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
import my_setup

file_directory = my_setup.raw_2025data_path()
file = "TerraBella"

file1 = rf"{file_directory}{file}_bc.csv"
file2 = rf"{file_directory}{file}.csv"

# Read both CSVs
df1 = pd.read_csv(file1, parse_dates=['date_time'])
df2 = pd.read_csv(file2, parse_dates=['date_time'])

# Merge them on datetime (outer join keeps all times, inner keeps only overlap)
combined = pd.merge(df1, df2, on='date_time', how='outer')

# --- Overlap duplicate columns ---
for col in combined.columns:
    if col.endswith("_x"):
        base = col[:-2]
        alt = base + "_y"
        if alt in combined.columns:
            # Fill NaNs from df1 with values from df2
            combined[base] = combined[col].combine_first(combined[alt])
            combined.drop(columns=[col, alt], inplace=True)

# Sort by datetime for consistency
combined = combined.sort_values('date_time').reset_index(drop=True)

combined.to_csv(rf"{file_directory}{file}_combined.csv")
