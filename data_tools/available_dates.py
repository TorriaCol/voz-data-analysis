import os
import pandas as pd

def to_spreadsheet(path,files,datetime_col,start_date,end_date):
# Master date range
    all_dates = pd.date_range(start=start_date, end=end_date, freq="D")

    # Start with an empty DataFrame
    present_df = pd.DataFrame()

    for fname in files:
        filepath = os.path.join(path, fname)
        df = pd.read_csv(filepath, parse_dates=[datetime_col])
        df["date"] = df[datetime_col].dt.normalize()

        # Keep only dates in the master range
        present = df["date"].unique()
        present = pd.to_datetime(present)
        present = pd.Series(sorted(set(present).intersection(all_dates)), name=fname)

        # Append as a new column (aligns automatically)
        present_df = pd.concat([present_df, present], axis=1)

    # Save result
    output_path = os.path.join(path, "present_dates.xlsx")
    present_df.to_excel(output_path, index=False)

    print(f"Saved results to {output_path}")
