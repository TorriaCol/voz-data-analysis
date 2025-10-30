import numpy as np
import pandas as pd
from sklearn.linear_model import ElasticNet

all_calibrations = []

def calibrate(training_data, variables, output_path):
    """
    Piecewise calibration using columns from a training DataFrame.
    - training_data: DataFrame containing training data
    - variables: list of predictor column names
    - output_path: path to save calibration coefficients
    Returns: dict of trained models per range
    """
    models = {}
    all_calibrations.clear()

    # Define piecewise ranges
    ranges = [
        # (lambda x: x <= 10, "10 and under"),
        # (lambda x: (x > 3) & (x <= 10), "5 - 15"),
        (lambda x: x >=0, "10+")
    ]

    labels = ["range"] + variables + ["intercept"]

    for condition_func, range_label in ranges:
        subset_mask = condition_func(training_data[variables[0]])
        subset_data = training_data.loc[subset_mask]

        if subset_data.empty:
            print(f"No data in range '{range_label}', skipping...")
            continue

        model = run_calibration(subset_data, variables, range_label)
        models[range_label] = model

    # # Save calibration coefficients
    # params_df = pd.DataFrame(all_calibrations, columns=labels)
    # params_df.to_csv(output_path, index=False)
    # print(f"Calibration coefficients saved to {output_path}")

    return models


def run_calibration(subset_data, variables, range_label):
    """
    Fit ElasticNet on a subset of training data.
    """
    X = subset_data[variables]
    y = subset_data["reference"]

    # Fit model
    model = ElasticNet(max_iter=50000, alpha=0.3, l1_ratio=0.1)
    model.fit(X, y)

    slopes = model.coef_
    intercept = model.intercept_

    print(f"Range '{range_label}' | Coefficients: {slopes} | Intercept: {intercept}")

    # Store coefficients
    all_calibrations.append([range_label] + list(slopes) + [intercept])

    return model


def apply_calibration(models, test_data, variables, new_column):
    """
    Apply piecewise calibration models to a separate dataset.
    - models: dict of trained models per range
    - test_data: DataFrame to apply calibration to
    - variables: list of predictor column names
    - new_column: name for calibrated output column
    """
    test_data[new_column] = np.nan

    # Define same piecewise ranges
    ranges = [
        # (lambda x: x <= 10, "10 and under"),
        # (lambda x: (x > 3) & (x <= 10), "5 - 15"),
        (lambda x: x >= 0, "10+")
    ]

    for condition_func, range_label in ranges:
        if range_label not in models:
            print(f"No trained model for range '{range_label}', skipping...")
            continue

        subset_mask = condition_func(test_data[variables[0]])
        subset_data = test_data.loc[subset_mask]

        if subset_data.empty:
            print(f"No data in test set for range '{range_label}', skipping...")
            continue

        model = models[range_label]
        predictions = model.predict(subset_data[variables])
        test_data.loc[subset_data.index, new_column] = predictions

    print(f"Applied calibration models; results stored in '{new_column}'")
    return test_data
