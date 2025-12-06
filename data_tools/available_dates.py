import os
import pandas as pd

# Gets one variable from each sensor to determine if sensor was working
# Assigns a 1 if yes and 0 if no
# Use these csvs for plotting a heatmap in the below function to determine data availability for all monitors
def generate_variable_working_csvs(path, files, datetime_col, vars_to_test):

    output_dir = os.path.join(path, "variable_working_status")
    os.makedirs(output_dir, exist_ok=True)

    for fname in files:
        print(f"Processing {fname}...")
        fpath = os.path.join(path, fname)
        df = pd.read_csv(fpath, parse_dates=[datetime_col])

        # New DataFrame containing datetime + tested variables
        status_df = pd.DataFrame()
        status_df[datetime_col] = df[datetime_col]

        # Create 0/1 status columns
        for var in vars_to_test:
            status_df[var] = df[var].apply(
                lambda x: 1 if (pd.notna(x) and 0 <= x < 200) else 0
            )

        # Save to CSV
        out_name = f"{os.path.splitext(fname)[0]}_status.csv"
        out_path = os.path.join(output_dir, out_name)
        status_df.to_csv(out_path, index=False)

        print(f"Saved → {out_path}")

import math
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap, BoundaryNorm

# This function creates a heatmap from the csvs located in the status_folder
# It plots green for a 1 and red for a 0 and no color for a missing datetime
# One heatmap is created for each monitor with the yticks indicating the sensor type and the x-axis being the date

def plot_status_heatmaps(status_folder, datetime_col, vars_to_test, sensor_names, start_date, end_date):
    # Get all *_status.csv files
    files = [f for f in os.listdir(status_folder) if f.endswith("_status.csv")]
    files.sort()
    
    n = len(files)
    cols = 2
    rows = math.ceil(n / cols)
    
    fig, axes = plt.subplots(rows, cols, figsize=(16, rows * 4), squeeze=False)
    
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)
    
    # Create full hourly datetime index at :30 minutes
    full_index = pd.date_range(start=start_date, end=end_date, freq='h') + pd.Timedelta(minutes=30)
    
    for i, fname in enumerate(files):
        ax = axes[i // cols][i % cols]
        
        # Load CSV
        df = pd.read_csv(os.path.join(status_folder, fname), parse_dates=[datetime_col])
        df_vars = df[[datetime_col] + vars_to_test].copy()
        df_vars.set_index(datetime_col, inplace=True)
        
        # Reindex to full hourly times, missing rows become NaN
        df_vars = df_vars.reindex(full_index)
        
        # Convert to numeric, so NaNs stay as NaN
        data = df_vars[vars_to_test].astype(float).T.values
        
        # Colormap: red=0, green=1, NaN=transparent
        cmap = ListedColormap(['red', 'green'])
        norm = BoundaryNorm([-0.5, 0.5, 1.5], cmap.N)  # 0 and 1
        
        im = ax.imshow(
            data,
            aspect='auto',
            interpolation='none',
            cmap=cmap,
            norm=norm
        )
        
        # Set title and y-axis
        ax.set_title(fname.replace("_status.csv", ""))
        ax.set_yticks(range(len(vars_to_test)))
        ax.set_yticklabels(sensor_names)

# ... after reindexing df_vars to full_index ...

        # Define tick datetimes
        month_starts = pd.date_range(start=start_date.replace(day=1), end=end_date, freq='MS')
        first_last = pd.DatetimeIndex([start_date, end_date])
        all_ticks = month_starts.union(first_last)

        # Convert datetime to integer positions for imshow
        tick_positions = df_vars.index.get_indexer(all_ticks, method='nearest')

        # Set ticks and labels
        ax.set_xticks(tick_positions)
        ax.set_xticklabels([d.strftime('%b %d') for d in all_ticks], rotation=45)

        # Optional: rotate for readability
        plt.xticks(rotation=45)

        fig.suptitle("Data Availability - 2025 Deployment", fontsize=18, y=1.02)
    # Hide unused subplots
    for j in range(i + 1, rows * cols):
        fig.delaxes(axes[j // cols][j % cols])

    plt.savefig(rf"../../2025DeploymentPlots/DataAvailability.jpg", format='jpg', dpi=300)
    
    plt.tight_layout()
    plt.show()
