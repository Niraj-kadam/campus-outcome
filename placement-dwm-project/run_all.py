"""Run the reproducible analytics pipeline from the project root."""
import argparse
import subprocess
import sys
from pathlib import Path

STEPS = ["01_build_warehouse.py", "02_preprocess.py", "03_olap.py", "04_eda.py",
         "05_decision_tree.py", "06_kmeans.py", "07_apriori.py", "08_export_powerbi.py"]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("k", nargs="?", type=int, default=4,
                        help="number of K-means clusters (default: 4)")
    args = parser.parse_args()
    root = Path(__file__).resolve().parent
    src = root / "src"
    raw = root / "data" / "raw" / "student_academic_placement_performance_dataset.csv"
    if not raw.is_file():
        parser.error(f"dataset not found: {raw}")
    for step in STEPS:
        print(f"\n{'=' * 12} {step} {'=' * 12}", flush=True)
        command = [sys.executable, str(src / step)]
        if step == "06_kmeans.py":
            command.append(str(args.k))
        subprocess.run(command, check=True, cwd=root)
    print("\nAll steps finished. See outputs/ and data/warehouse/.")


if __name__ == "__main__":
    main()
