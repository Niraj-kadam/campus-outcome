"""Experiment 4: data pre-processing -> data/processed/*.csv"""
import pandas as pd
from sklearn.preprocessing import StandardScaler
from config import RAW_CSV, CLEAN_CSV, SCALED_CSV, TABLE_DIR, TARGET, LEAKY_COLUMNS, ID_COLUMN


def main():
    df = pd.read_csv(RAW_CSV)
    required = {ID_COLUMN, TARGET, *LEAKY_COLUMNS, "gender", "extracurricular_activities"}
    missing_columns = sorted(required - set(df.columns))
    if missing_columns:
        raise ValueError(f"Dataset is missing required columns: {missing_columns}")
    if df.empty:
        raise ValueError("Dataset contains no rows")
    report = []

    # 1. quality checks
    report.append(("rows", len(df)))
    report.append(("missing_values_total", int(df.isna().sum().sum())))
    report.append(("duplicate_rows", int(df.duplicated().sum())))
    report.append(("duplicate_student_ids", int(df[ID_COLUMN].duplicated().sum())))
    report.append(("columns", len(df.columns)))
    if df[TARGET].isna().any() or not set(df[TARGET].dropna().unique()).issubset({0, 1}):
        raise ValueError(f"{TARGET} must contain only 0 and 1, with no missing values")
    if df.isna().any().any():
        raise ValueError("Dataset has missing values; resolve them before preprocessing")
    df = df.drop_duplicates()

    # 2. outliers (IQR rule) - reported, not removed, since values are within valid ranges
    num = df.select_dtypes("number").drop(columns=[ID_COLUMN, TARGET])
    q1, q3 = num.quantile(0.25), num.quantile(0.75)
    iqr = q3 - q1
    outliers = ((num < q1 - 1.5 * iqr) | (num > q3 + 1.5 * iqr)).sum()
    for col, n in outliers.items():
        report.append((f"outliers_{col}", int(n)))

    # 3. encoding
    mappings = {"gender": {"Male": 1, "Female": 0},
                "extracurricular_activities": {"Yes": 1, "No": 0}}
    for column, mapping in mappings.items():
        values = set(df[column].dropna().unique())
        unknown = values - set(mapping)
        if unknown:
            raise ValueError(f"Unexpected values in {column}: {sorted(unknown)}")
        df[column] = df[column].map(mapping)

    # 4. drop identifier (carries no information)
    df = df.drop(columns=[ID_COLUMN])
    df.to_csv(CLEAN_CSV, index=False)

    # 5. scaling for distance-based algorithms (K-means). Leaky column excluded.
    features = df.drop(columns=[TARGET, *LEAKY_COLUMNS])
    scaled = pd.DataFrame(StandardScaler().fit_transform(features), columns=features.columns,
                          index=features.index)
    scaled[TARGET] = df[TARGET].values       # kept only to profile clusters afterwards
    scaled.to_csv(SCALED_CSV, index=False)

    rep = pd.DataFrame(report, columns=["check", "value"])
    rep.to_csv(TABLE_DIR / "preprocessing_report.csv", index=False)
    print(rep.to_string(index=False))
    print("\nSaved:", CLEAN_CSV.name, "and", SCALED_CSV.name)


if __name__ == "__main__":
    main()
