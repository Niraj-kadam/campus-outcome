"""Experiment 9: export warehouse tables + one flat table for Power BI / Tableau / WEKA."""
import sqlite3
import pandas as pd
from config import DB_PATH, POWERBI_DIR, CLEAN_CSV


def main():
    with sqlite3.connect(DB_PATH) as con:
        for t in ["dim_student", "dim_academic", "dim_skill", "dim_experience", "dim_attendance", "fact_placement"]:
            pd.read_sql_query(f"SELECT * FROM {t}", con).to_csv(POWERBI_DIR / f"{t}.csv", index=False)
        flat = pd.read_sql_query("""
            SELECT f.placement_key, f.student_id, s.gender, s.extracurricular,
                   a.ssc_band, a.hsc_band, a.degree_band, a.cgpa_band, a.backlogs,
                   k.technical_band, k.soft_band, k.entrance_band,
                   e.internship_count, e.live_projects, e.work_exp_band, e.certifications,
                   t.attendance_band, f.cgpa, f.entrance_exam_score, f.placement_status, f.salary_package_lpa
            FROM fact_placement f
            JOIN dim_student s ON f.student_key = s.student_key
            JOIN dim_academic a ON f.academic_key = a.academic_key
            JOIN dim_skill k ON f.skill_key = k.skill_key
            JOIN dim_experience e ON f.experience_key = e.experience_key
            JOIN dim_attendance t ON f.attendance_key = t.attendance_key""", con)
    flat["placement_label"] = flat.placement_status.map({1: "Placed", 0: "Not placed"})
    flat.to_csv(POWERBI_DIR / "placement_flat.csv", index=False)
    # WEKA reads CSV/ARFF; the clean encoded file (without leaky salary) is the easiest input there
    pd.read_csv(CLEAN_CSV).drop(columns=["salary_package_lpa"]).to_csv(POWERBI_DIR / "weka_input.csv", index=False)
    print("Exported to", POWERBI_DIR)


if __name__ == "__main__":
    main()
