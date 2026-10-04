"""Experiments 1-2: build dimension tables and the fact table from the raw CSV."""
import sqlite3
import pandas as pd
from config import RAW_CSV, DB_PATH, SQL_DIR


def band(s, cuts, labels):
    return pd.cut(s, bins=cuts, labels=labels, include_lowest=True).astype(str)


def make_dim(df, cols, key_name):
    dim = df[cols].drop_duplicates().reset_index(drop=True)
    dim.insert(0, key_name, dim.index + 1)
    return dim


def main():
    df = pd.read_csv(RAW_CSV)

    # --- bands (these make roll-up / drill-down meaningful) ---
    pct_cuts, pct_labels = [0, 60, 75, 100], ["Low (<60)", "Medium (60-75)", "High (75+)"]
    df["ssc_band"] = band(df.ssc_percentage, pct_cuts, pct_labels)
    df["hsc_band"] = band(df.hsc_percentage, pct_cuts, pct_labels)
    df["degree_band"] = band(df.degree_percentage, pct_cuts, pct_labels)
    df["cgpa_band"] = band(df.cgpa, [0, 6.5, 7.5, 8.5, 10], ["1: <6.5", "2: 6.5-7.5", "3: 7.5-8.5", "4: 8.5+"])
    sc_cuts, sc_labels = [0, 55, 75, 100], ["Low", "Medium", "High"]
    df["technical_band"] = band(df.technical_skill_score, sc_cuts, sc_labels)
    df["soft_band"] = band(df.soft_skill_score, sc_cuts, sc_labels)
    df["entrance_band"] = band(df.entrance_exam_score, sc_cuts, sc_labels)
    df["attendance_band"] = band(df.attendance_percentage, [0, 70, 85, 100],
                                 ["Low (<70)", "Medium (70-85)", "High (85+)"])
    df["work_exp_band"] = band(df.work_experience_months, [-1, 0, 12, 24],
                               ["None", "1-12 months", "13-24 months"])
    df = df.rename(columns={"extracurricular_activities": "extracurricular"})

    # --- dimensions: one row per unique combination, surrogate key added ---
    dims = {
        "dim_student": (["gender", "extracurricular"], "student_key"),
        "dim_academic": (["ssc_band", "hsc_band", "degree_band", "cgpa_band", "backlogs"], "academic_key"),
        "dim_skill": (["technical_band", "soft_band", "entrance_band"], "skill_key"),
        "dim_experience": (["internship_count", "live_projects", "work_exp_band", "certifications"], "experience_key"),
        "dim_attendance": (["attendance_band"], "attendance_key"),
    }
    dim_frames, fact = {}, df.copy()
    for name, (cols, key) in dims.items():
        dim_frames[name] = make_dim(df, cols, key)
        fact = fact.merge(dim_frames[name], on=cols, how="left")

    fact.insert(0, "placement_key", range(1, len(fact) + 1))
    fact = fact[["placement_key", "student_id", "student_key", "academic_key", "skill_key",
                 "experience_key", "attendance_key", "cgpa", "degree_percentage",
                 "entrance_exam_score", "technical_skill_score", "soft_skill_score",
                 "work_experience_months", "placement_status", "salary_package_lpa"]]

    # --- write to SQLite using the DDL ---
    with sqlite3.connect(DB_PATH) as con:
        con.executescript((SQL_DIR / "01_create_schema.sql").read_text())
        for name, frame in dim_frames.items():
            frame.to_sql(name, con, if_exists="append", index=False)
        fact.to_sql("fact_placement", con, if_exists="append", index=False)
        counts = {t: con.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0] for t in [*dims, "fact_placement"]}
    print("Warehouse built at", DB_PATH)
    for t, c in counts.items():
        print(f"  {t:16s} {c:5d} rows")


if __name__ == "__main__":
    main()
