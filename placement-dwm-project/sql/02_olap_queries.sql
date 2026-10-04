-- OLAP operations on the star schema. Run via: python src/03_olap.py  (or paste into any SQL client).

-- ROLL-UP: placement rate by CGPA band
-- name: rollup_cgpa
SELECT a.cgpa_band, COUNT(*) AS students, SUM(f.placement_status) AS placed,
       ROUND(100.0 * SUM(f.placement_status) / COUNT(*), 2) AS placement_rate_pct,
       ROUND(AVG(CASE WHEN f.placement_status = 1 THEN f.salary_package_lpa END), 2) AS avg_salary_lpa
FROM fact_placement f JOIN dim_academic a ON f.academic_key = a.academic_key
GROUP BY a.cgpa_band ORDER BY a.cgpa_band;

-- DRILL-DOWN: same, split by gender
-- name: drilldown_cgpa_gender
SELECT a.cgpa_band, s.gender, COUNT(*) AS students,
       ROUND(100.0 * SUM(f.placement_status) / COUNT(*), 2) AS placement_rate_pct
FROM fact_placement f
JOIN dim_academic a ON f.academic_key = a.academic_key
JOIN dim_student  s ON f.student_key  = s.student_key
GROUP BY a.cgpa_band, s.gender ORDER BY a.cgpa_band, s.gender;

-- SLICE: only students with 0 backlogs
-- name: slice_no_backlogs
SELECT a.cgpa_band, COUNT(*) AS students,
       ROUND(100.0 * SUM(f.placement_status) / COUNT(*), 2) AS placement_rate_pct
FROM fact_placement f JOIN dim_academic a ON f.academic_key = a.academic_key
WHERE a.backlogs = 0
GROUP BY a.cgpa_band ORDER BY a.cgpa_band;

-- DICE: internships >= 2 AND technical band = High
-- name: dice_internship_tech
SELECT e.internship_count, k.technical_band, COUNT(*) AS students,
       ROUND(100.0 * SUM(f.placement_status) / COUNT(*), 2) AS placement_rate_pct
FROM fact_placement f
JOIN dim_experience e ON f.experience_key = e.experience_key
JOIN dim_skill      k ON f.skill_key      = k.skill_key
WHERE e.internship_count >= 2 AND k.technical_band = 'High'
GROUP BY e.internship_count, k.technical_band ORDER BY e.internship_count;

-- PIVOT: CGPA band (rows) x internship count (columns), placement rate
-- name: pivot_cgpa_internships
SELECT a.cgpa_band,
  ROUND(100.0 * AVG(CASE WHEN e.internship_count = 0 THEN f.placement_status END), 1) AS intern_0,
  ROUND(100.0 * AVG(CASE WHEN e.internship_count = 1 THEN f.placement_status END), 1) AS intern_1,
  ROUND(100.0 * AVG(CASE WHEN e.internship_count = 2 THEN f.placement_status END), 1) AS intern_2,
  ROUND(100.0 * AVG(CASE WHEN e.internship_count = 3 THEN f.placement_status END), 1) AS intern_3,
  ROUND(100.0 * AVG(CASE WHEN e.internship_count = 4 THEN f.placement_status END), 1) AS intern_4
FROM fact_placement f
JOIN dim_academic   a ON f.academic_key   = a.academic_key
JOIN dim_experience e ON f.experience_key = e.experience_key
GROUP BY a.cgpa_band ORDER BY a.cgpa_band;
