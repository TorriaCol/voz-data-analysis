import pandas as pd

from . import handle_datetime
from . import process_data as process

def from_combined(combined_file, device_names, output_file, decimal_threshold=0.2):
    try:
        df = process.raw_voz_data(combined_file)
        df = handle_datetime.utc_to_CA(df)
        df = df.dropna(how='any')

        df.sort_values(['coreid'], inplace=True)
        df.sort_index(inplace=True)

        summary_rows = []

        for device_id, group in df.groupby('coreid'):
            name = device_names.get(device_id, f"Device_{device_id[:6]}")
            if("Device" in name):
                continue
            last_lat, last_lon = None, None

            for pos, (i, row) in enumerate(group.iterrows()):
                try:
                    lat = float(row.get('lat', 0))
                    lon = float(row.get('lon', 0))
                except ValueError:
                    continue  # skip bad values

                if pd.isna(lat) or pd.isna(lon) or abs(lat) <= 5 or abs(lon) <= 5:
                    continue

                # First row - Always document first location
                if pos == 0:
                    summary_rows.append({
                        "name": name,
                        "device_id": device_id,
                        "latitude": lat,
                        "longitude": lon,
                        "timestamp": i
                    })
                    last_lat, last_lon = lat, lon

                # Last row - Always document last location
                elif pos == len(group) - 1:
                    lasttime = i

                # Middle rows - Check for significant movements
                else:
                    if last_lat is not None and last_lon is not None:
                        if abs(lat - last_lat) >= decimal_threshold or abs(lon - last_lon) >= decimal_threshold:
                            summary_rows.append({
                                "name": device_names.get(device_id, f"Device_{device_id[:6]}"),
                                "device_id": device_id,
                                "latitude": lat,
                                "longitude": lon,
                                "timestamp": i
                            })
                            last_lat, last_lon = lat, lon

            summary_rows.append({
                    "name": device_names.get(device_id, f"Device_{device_id[:6]}"),
                    "device_id": device_id,
                    "latitude": last_lat,
                    "longitude": last_lon,
                    "timestamp": lasttime
                })
            
        summary_df = pd.DataFrame(summary_rows)
        summary_df.to_csv(output_file, index=False)
        print(f"Saved significant movement summary to {output_file}")
        
    except Exception as e:
        print(f"Error during summary extraction: {e}")
