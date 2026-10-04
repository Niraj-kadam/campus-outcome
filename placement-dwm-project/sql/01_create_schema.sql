-- Star schema for the placement data warehouse (SQLite syntax; works in MySQL with minor changes:
-- replace INTEGER PRIMARY KEY with INT PRIMARY KEY and TEXT with VARCHAR(50)).
DROP TABLE IF EXISTS fact_placement;
DROP TABLE IF EXISTS dim_student;
DROP TABLE IF EXISTS dim_academic;
DROP TABLE IF EXISTS dim_skill;
DROP TABLE IF EXISTS dim_experience;
DROP TABLE IF EXISTS dim_attendance;

CREATE TABLE dim_student (
    student_key      INTEGER PRIMARY KEY,
    gender           TEXT NOT NULL,
    extracurricular  TEXT NOT NULL            -- Yes / No
);

CREATE TABLE dim_academic (
    academic_key     INTEGER PRIMARY KEY,
    ssc_band         TEXT NOT NULL,
    hsc_band         TEXT NOT NULL,
    degree_band      TEXT NOT NULL,
    cgpa_band        TEXT NOT NULL,
    backlogs         INTEGER NOT NULL
);

CREATE TABLE dim_skill (
    skill_key        INTEGER PRIMARY KEY,
    technical_band   TEXT NOT NULL,
    soft_band        TEXT NOT NULL,
    entrance_band    TEXT NOT NULL
);

CREATE TABLE dim_experience (
    experience_key   INTEGER PRIMARY KEY,
    internship_count INTEGER NOT NULL,
    live_projects    INTEGER NOT NULL,
    work_exp_band    TEXT NOT NULL,
    certifications   INTEGER NOT NULL
);

CREATE TABLE dim_attendance (
    attendance_key   INTEGER PRIMARY KEY,
    attendance_band  TEXT NOT NULL
);

CREATE TABLE fact_placement (
    placement_key         INTEGER PRIMARY KEY,
    student_id            INTEGER NOT NULL,           -- degenerate dimension
    student_key           INTEGER NOT NULL REFERENCES dim_student(student_key),
    academic_key          INTEGER NOT NULL REFERENCES dim_academic(academic_key),
    skill_key             INTEGER NOT NULL REFERENCES dim_skill(skill_key),
    experience_key        INTEGER NOT NULL REFERENCES dim_experience(experience_key),
    attendance_key        INTEGER NOT NULL REFERENCES dim_attendance(attendance_key),
    -- measures
    cgpa                  REAL,
    degree_percentage     INTEGER,
    entrance_exam_score   INTEGER,
    technical_skill_score INTEGER,
    soft_skill_score      INTEGER,
    work_experience_months INTEGER,
    placement_status      INTEGER NOT NULL,           -- 1 = placed, 0 = not placed
    salary_package_lpa    REAL
);

CREATE INDEX idx_fact_student    ON fact_placement(student_key);
CREATE INDEX idx_fact_academic   ON fact_placement(academic_key);
CREATE INDEX idx_fact_skill      ON fact_placement(skill_key);
CREATE INDEX idx_fact_experience ON fact_placement(experience_key);
CREATE INDEX idx_fact_attendance ON fact_placement(attendance_key);
