# Student Placement Analytics: A Data Warehouse and Mining Approach
DWM course project. Dataset: `data/raw/student_academic_placement_performance_dataset.csv` (5,000 students, 18 columns, no missing values, ~17% placed).

**Problem statement:** Which academic, skill and experience factors decide whether a student gets placed, and can we predict it early enough to help weak students?

## Quick start
Run these commands from the `placement-dwm-project` directory (Python 3.10+):
```bash
pip install -r requirements.txt
python run_all.py          # runs experiments 1-9 in order
python run_all.py 4        # same pipeline, with K=4 for K-means
```
The pipeline reads the bundled CSV in `data/raw/`, rebuilds the SQLite warehouse, and refreshes generated files under `data/processed/` and `outputs/`. The warehouse needs no server. Run an individual script with `python src/05_decision_tree.py` (preprocessing must have run first for steps 5-7).

## Local dashboard
After running the pipeline once, start the included website from this folder:
```bash
python web/app.py
```
Open `http://127.0.0.1:8000` in a browser. The dashboard shows live summary numbers and placement rates, embeds the generated analysis figures, explores Apriori rules to placed outcomes, explains the decision tree metrics/rules/features, and offers an estimate form using the saved model. Keep the server running while using the page. Estimates are only a course-project demonstration because the dataset appears synthetic and rule-generated.

### Optional web scraping
The scraper is deliberately excluded from the standard run because it needs a site chosen by you. Check the site's terms and `robots.txt`, then run `python src/09_web_scraping.py https://example.org/page --selector 'table tr'`. It saves extracted table rows to `outputs/tables/scraped_data.csv`.

## Folder structure
```
placement-dwm-project/
├── data/
│   ├── raw/             original CSV (never edited)
│   ├── processed/       clean_encoded.csv, scaled_features.csv   (made by step 02)
│   └── warehouse/       placement_dw.db  (SQLite star schema)    (made by step 01)
├── sql/
│   ├── 01_create_schema.sql   star schema DDL (dimension + fact tables)
│   └── 02_olap_queries.sql    roll-up, drill-down, slice, dice, pivot
├── src/                 one script per experiment (config.py holds paths/settings)
├── notebooks/           optional: Jupyter versions of the scripts for screenshots
├── outputs/
│   ├── figures/         EDA + model plots (use these in the report)
│   ├── tables/          OLAP results, metrics, cluster profile, Apriori rules
│   ├── models/          saved decision tree
│   └── powerbi/         CSV exports for Power BI / Tableau / WEKA
├── powerbi/             put your .pbix file here + BUILD_GUIDE.md
├── report/              REPORT_OUTLINE.md - chapter skeleton with where each output goes
├── run_all.py
└── requirements.txt
```

## Experiment -> file map
| # | Experiment | Where | Main output |
|---|---|---|---|
| 1-2 | Star schema, dimension + fact tables | `sql/01_create_schema.sql`, `src/01_build_warehouse.py` | `data/warehouse/placement_dw.db` |
| 3 | OLAP operations | `sql/02_olap_queries.sql`, `src/03_olap.py` | `outputs/tables/olap_*.csv` |
| 4 | Pre-processing | `src/02_preprocess.py` | `data/processed/*`, `preprocessing_report.csv` |
| 5 | EDA | `src/04_eda.py` | `outputs/figures/eda_*.png` |
| 6 | Decision tree | `src/05_decision_tree.py` | metrics, tree plot, rules, feature importance |
| 7 | K-means | `src/06_kmeans.py` | elbow plot, cluster profile |
| 8 | Apriori (optional) | `src/07_apriori.py` | `apriori_rules_to_placed.csv` |
| 9 | Power BI / WEKA | `src/08_export_powerbi.py`, `powerbi/BUILD_GUIDE.md` | `outputs/powerbi/*.csv` |
| 10 | Web scraping (optional) | `src/09_web_scraping.py` (template) | `outputs/tables/scraped_data.csv` |

## Things to know before writing the report
- **Salary is excluded from model features.** `salary_package_lpa` is 0 exactly when a student is unplaced, so using it would leak the answer.
- **The data looks rule-generated (synthetic).** In this dataset, nobody is placed with 3+ backlogs, CGPA below 7, technical score below 60 or soft score below 55. So the decision tree scores ~1.00 on the test set. Do not present that as a great model. Say it plainly in the report: the tree recovered the placement rules hidden in the data, and that is why accuracy is perfect. The rules themselves (`outputs/tables/decision_tree_rules.txt`) are your real finding.
- **Pre-processing is light** because there are no nulls, duplicates or outliers in the numeric features (salary shows IQR "outliers" only because most values are 0). Report the checks, then justify encoding, scaling and binning.
- **K-means clusters are weak** (silhouette ~0.05-0.07): students do not form tight groups. Choose K from the elbow plot, but describe the clusters honestly. With K=4 they split mainly by technical vs soft skill level.
- **Apriori:** placement is only ~17% of rows, so use a modest `MIN_CONFIDENCE` (0.3 default) and sort by lift.
- **Web scraping** is only a template: set `URL` and the CSS selector for the site you pick, and check the site's robots.txt first.
