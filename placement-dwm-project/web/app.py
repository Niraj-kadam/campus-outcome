"""Local web dashboard for Student Placement Analytics (stdlib HTTP server)."""
from __future__ import annotations

import json
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlparse

import joblib
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from config import CLEAN_CSV, MODEL_DIR, RAW_CSV, TABLE_DIR, TARGET  # noqa: E402

WEB_DIR = Path(__file__).resolve().parent
FEATURES = ["gender", "ssc_percentage", "hsc_percentage", "degree_percentage", "cgpa",
            "entrance_exam_score", "technical_skill_score", "soft_skill_score",
            "internship_count", "live_projects", "work_experience_months", "certifications",
            "attendance_percentage", "backlogs", "extracurricular_activities"]


def dashboard_data():
    df = pd.read_csv(RAW_CSV)
    placed = df[df[TARGET] == 1]
    rates = (df.groupby("backlogs", sort=True)[TARGET].mean() * 100).round(1)
    cgpa_rates = (df.assign(cgpa_band=pd.cut(df.cgpa, [0, 6.5, 7.5, 8.5, 10],
                                               labels=["<6.5", "6.5–7.5", "7.5–8.5", "8.5+"]))
                    .groupby("cgpa_band", observed=True)[TARGET].mean() * 100).round(1)
    return {
        "students": int(len(df)), "placed": int(df[TARGET].sum()),
        "placement_rate": round(float(df[TARGET].mean() * 100), 1),
        "avg_salary": round(float(placed.salary_package_lpa.mean()), 2),
        "backlog_labels": [str(x) for x in rates.index], "backlog_rates": rates.tolist(),
        "cgpa_labels": [str(x) for x in cgpa_rates.index], "cgpa_rates": cgpa_rates.tolist(),
    }


def mining_data():
    rules_path = TABLE_DIR / "apriori_rules_to_placed.csv"
    importance_path = TABLE_DIR / "decision_tree_feature_importance.csv"
    metrics_path = TABLE_DIR / "decision_tree_metrics.csv"
    text_path = TABLE_DIR / "decision_tree_rules.txt"
    rules = pd.read_csv(rules_path).fillna("").to_dict(orient="records") if rules_path.is_file() else []
    importance = pd.read_csv(importance_path, index_col=0).iloc[:, 0] if importance_path.is_file() else pd.Series(dtype=float)
    metrics = pd.read_csv(metrics_path, index_col=0) if metrics_path.is_file() else pd.DataFrame()
    accuracy = float(metrics.loc["accuracy"].iloc[0]) if "accuracy" in metrics.index else None
    placed = metrics.loc["Placed"] if "Placed" in metrics.index else pd.Series(dtype=float)
    return {
        "apriori": {"rules": rules, "support": 0.03, "confidence": 0.30},
        "tree": {"accuracy": accuracy,
                 "placed_precision": float(placed.get("precision")) if not placed.empty else None,
                 "placed_recall": float(placed.get("recall")) if not placed.empty else None,
                 "importance": [{"feature": str(k), "importance": round(float(v), 4)}
                                for k, v in importance.head(10).items()],
                 "rules_text": text_path.read_text(encoding="utf-8") if text_path.is_file() else "Run python run_all.py to generate the model outputs."},
    }


class Handler(BaseHTTPRequestHandler):
    def send_bytes(self, content: bytes, content_type: str, status: int = 200):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def send_json(self, data, status: int = 200):
        self.send_bytes(json.dumps(data).encode("utf-8"), "application/json; charset=utf-8", status)

    def do_GET(self):
        path = unquote(urlparse(self.path).path)
        if path == "/api/summary":
            return self.send_json(dashboard_data())
        if path == "/api/mining":
            return self.send_json(mining_data())
        if path == "/":
            target = WEB_DIR / "index.html"
        elif path.startswith("/figures/"):
            target = ROOT / "outputs" / "figures" / Path(path).name
        else:
            target = WEB_DIR / Path(path.lstrip("/"))
        if not target.is_file() or (WEB_DIR not in target.parents and ROOT / "outputs" / "figures" not in target.parents):
            return self.send_bytes(b"Not found", "text/plain", 404)
        content_type = "text/html; charset=utf-8" if target.suffix == ".html" else "text/css; charset=utf-8"
        if target.suffix == ".png":
            content_type = "image/png"
        return self.send_bytes(target.read_bytes(), content_type)

    def do_POST(self):
        if urlparse(self.path).path != "/api/predict":
            return self.send_json({"error": "Not found"}, 404)
        try:
            length = min(int(self.headers.get("Content-Length", "0")), 16_384)
            payload = json.loads(self.rfile.read(length))
            clean = pd.read_csv(CLEAN_CSV)
            X = clean.drop(columns=[TARGET, "salary_package_lpa"])
            row = {column: float(payload[column]) for column in FEATURES}
            frame = pd.DataFrame([row], columns=X.columns)
            model = joblib.load(MODEL_DIR / "decision_tree.joblib")
            probability = float(model.predict_proba(frame)[0][1])
            return self.send_json({"probability": round(probability * 100, 1),
                                   "prediction": "Likely placed" if probability >= 0.5 else "Needs support"})
        except (ValueError, TypeError, KeyError, json.JSONDecodeError, FileNotFoundError) as exc:
            return self.send_json({"error": str(exc)}, 400)

    def log_message(self, fmt, *args):
        print("[web] " + fmt % args)


def main():
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", default=8000, type=int)
    args = parser.parse_args()
    if not RAW_CSV.is_file():
        parser.error(f"Dataset not found: {RAW_CSV}")
    print(f"Placement dashboard: http://{args.host}:{args.port}")
    print("Press Ctrl+C to stop.")
    ThreadingHTTPServer((args.host, args.port), Handler).serve_forever()


if __name__ == "__main__":
    main()
