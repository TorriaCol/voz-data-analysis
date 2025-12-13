from os import environ

import pandas as pd
import requests

company_key = environ.get('X_COMPANY_KEY', '259c31ff-dd8d-4393-8531-5b85a3982f42')
device = 'AQLite-1578'

response = requests.get(
f'http://air.api.airqdb.com/v2/uploads/primary/time-series/{ device }',
headers={
'x-company-key': company_key
},
params={
"start": "2025-07-10T00:00:00Z",
"end": "2025-08-16T00:00:00Z",
"average": "0"
}
)
assert response.status_code == 200, 'Request was not successful'
data = response.json()
# print(json.dumps(data, indent=4))

# Extract relevant fields
# Define the keys you want to extract
keys = [
    "Ozone-1578:OZONE",
    "GPS:LAT",
    "GPS:LON"
    # "PAM-1385:TEMP",
    # "PAM-1385:RELHUM",
    # "PAM-1385:PM10",
    # "PAM-1385:PM2.5"
]

# Find the number of entries (assumes all lists are same length and aligned)
num_entries = len(data[keys[0]])

# Build list of rows
records = []
for i in range(num_entries):
    row = {}
    for key in keys:
        point = data[key][i].get("dataPoint", {})
        row[f"{key}_value"] = point.get("value")
        row[f"{key}_date"] = point.get("dateUploaded")
    records.append(row)

# Convert to DataFrame
df = pd.DataFrame(records)
df.to_csv("AQLite-2025-08-15validation.csv", index=False)
