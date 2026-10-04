"""Experiment 6: Decision tree classifier for placement_status."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import joblib
from sklearn.metrics import classification_report, ConfusionMatrixDisplay, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier, export_text, plot_tree
from config import CLEAN_CSV, FIG_DIR, TABLE_DIR, MODEL_DIR, TARGET, LEAKY_COLUMNS, RANDOM_STATE


def main():
    df = pd.read_csv(CLEAN_CSV)
    X = df.drop(columns=[TARGET, *LEAKY_COLUMNS])        # salary removed: it leaks the answer
    y = df[TARGET]
    X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.2, stratify=y, random_state=RANDOM_STATE)

    model = DecisionTreeClassifier(max_depth=5, min_samples_leaf=20,
                                   class_weight="balanced", random_state=RANDOM_STATE)
    model.fit(X_tr, y_tr)
    pred = model.predict(X_te)

    names = ["Not placed", "Placed"]
    report = classification_report(y_te, pred, target_names=names, output_dict=True)
    pd.DataFrame(report).T.to_csv(TABLE_DIR / "decision_tree_metrics.csv")
    print(classification_report(y_te, pred, target_names=names))
    print("ROC-AUC:", round(roc_auc_score(y_te, model.predict_proba(X_te)[:, 1]), 3))

    ConfusionMatrixDisplay.from_predictions(y_te, pred, display_labels=names, cmap="Blues")
    plt.title("Decision tree - confusion matrix"); plt.tight_layout()
    plt.savefig(FIG_DIR / "dt_confusion_matrix.png", dpi=150); plt.close()

    plt.figure(figsize=(22, 10))
    plot_tree(model, feature_names=list(X.columns), class_names=names, filled=True, fontsize=7, max_depth=3)
    plt.savefig(FIG_DIR / "dt_tree.png", dpi=150); plt.close()

    imp = pd.Series(model.feature_importances_, index=X.columns).sort_values(ascending=False)
    imp.to_csv(TABLE_DIR / "decision_tree_feature_importance.csv", header=["importance"])
    imp.head(10)[::-1].plot.barh(figsize=(7, 5), color="#4f81bd"); plt.title("Top feature importances")
    plt.tight_layout(); plt.savefig(FIG_DIR / "dt_feature_importance.png", dpi=150); plt.close()
    print("\nTop features:\n", imp.head(8).round(3).to_string())

    (TABLE_DIR / "decision_tree_rules.txt").write_text(export_text(model, feature_names=list(X.columns)))
    joblib.dump(model, MODEL_DIR / "decision_tree.joblib")


if __name__ == "__main__":
    main()
