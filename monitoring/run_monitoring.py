import pandas as pd
from evidently.metrics import DataDriftPreset, RegressionPerformancePreset
from evidently.report import Report

# Load baseline and new data
baseline = pd.read_csv("data/monitoring/baseline.csv")
current = pd.read_csv("data/monitoring/current.csv")

# Create and run report
report = Report(
    metrics=[
        DataDriftPreset(),
        RegressionPerformancePreset(
            target_column="price", prediction_column="prediction"
        ),
    ]
)
report.run(reference_data=baseline, current_data=current)

# Save results
report.save_html("data/monitoring/reports/drift_report.html")
report.save_json("data/monitoring/reports/drift_metrics.json")
