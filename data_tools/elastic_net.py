import numpy as np
import pandas as pd
from sklearn.linear_model import ElasticNet

def calibrate(reference, data, variables, output_path):
    if len(reference) != len(data):
        raise ValueError("Reference and data must have the same length.")

    data_selected_columns = data[variables]

    mask = np.isfinite(data_selected_columns).all(axis=1) & np.isfinite(reference)
    valid_samples = mask.sum()

    if valid_samples == 0:
        raise ValueError("No valid samples available for calibration. Check your cleaning steps.")

    print("Number of valid samples after cleaning:", valid_samples)

    X_cleaned = data_selected_columns[mask]
    y_cleaned = reference[mask]

    # Create and fit the ElasticNet regression model
    model = ElasticNet(max_iter=50000, alpha=0.3, l1_ratio=0.1)  # Adjust alpha and l1_ratio as needed
    model.fit(X_cleaned, y_cleaned)

    # Get the coefficients (slopes) and intercept
    slopes = model.coef_
    intercept = model.intercept_

    print("Coefficients (slopes):", slopes)
    print("Intercept (b0):", intercept)

    # Calibrate the data using the regression model
    calibrated_data = model.predict(data_selected_columns)

                 # Create a new DataFrame with calibrated values
    # Combine slopes and intercept
    params = list(slopes) + [intercept]
    labels = variables + ['intercept']

    # Transpose: one row, each column is a parameter
    params_df = pd.DataFrame([params], columns=labels)

    # Save to Excel
    params_df.to_csv(output_path, index=False)

    return calibrated_data, slopes, intercept