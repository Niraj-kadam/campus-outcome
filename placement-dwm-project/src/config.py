"""Shared paths and settings. Every script imports from here."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW_CSV = ROOT / "data/raw/student_academic_placement_performance_dataset.csv"
CLEAN_CSV = ROOT / "data/processed/clean_encoded.csv"
SCALED_CSV = ROOT / "data/processed/scaled_features.csv"
DB_PATH = ROOT / "data/warehouse/placement_dw.db"
SQL_DIR = ROOT / "sql"
FIG_DIR = ROOT / "outputs/figures"
TABLE_DIR = ROOT / "outputs/tables"
MODEL_DIR = ROOT / "outputs/models"
POWERBI_DIR = ROOT / "outputs/powerbi"

RANDOM_STATE = 42
TARGET = "placement_status"
# salary is 0 exactly when the student is unplaced, so it leaks the target.
LEAKY_COLUMNS = ["salary_package_lpa"]
ID_COLUMN = "student_id"

for d in (FIG_DIR, TABLE_DIR, MODEL_DIR, POWERBI_DIR, CLEAN_CSV.parent, DB_PATH.parent):
    d.mkdir(parents=True, exist_ok=True)
