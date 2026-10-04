# Power BI build guide (Experiment 9)

1. Home > Get data > Text/CSV. Load from `outputs/powerbi/`: `fact_placement.csv` and the five `dim_*.csv` files
   (or just `placement_flat.csv` for a quick dashboard).
2. Model view: create one-to-many relationships dim -> fact on the matching `*_key` columns
   (student_key, academic_key, skill_key, experience_key, attendance_key).
3. Measures (Modeling > New measure):
   - `Total Students = COUNTROWS(fact_placement)`
   - `Placed = CALCULATE(COUNTROWS(fact_placement), fact_placement[placement_status] = 1)`
   - `Placement Rate = DIVIDE([Placed], [Total Students])`
   - `Avg Salary (LPA) = CALCULATE(AVERAGE(fact_placement[salary_package_lpa]), fact_placement[placement_status] = 1)`
4. Visuals: KPI cards (Total Students, Placement Rate, Avg Salary); column chart of Placement Rate by `cgpa_band`;
   column chart by `internship_count`; matrix `cgpa_band` x `internship_count`; donut Placed vs Not placed.
5. Slicers: gender, extracurricular, backlogs, attendance_band.
6. Save as `powerbi/placement_dashboard.pbix` and take screenshots for the report.

WEKA alternative: open `outputs/powerbi/weka_input.csv` > Preprocess > Classify > J48 (set the class to placement_status,
convert it to nominal with the NumericToNominal filter) and compare with your Python decision tree.
