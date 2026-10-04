"""Experiment 5: exploratory data analysis -> outputs/figures"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from config import RAW_CSV, FIG_DIR, TABLE_DIR, TARGET

sns.set_theme(style="whitegrid")


def save(name):
    plt.tight_layout()
    plt.savefig(FIG_DIR / name, dpi=150)
    plt.close()


def main():
    df = pd.read_csv(RAW_CSV)
    df.describe().T.to_csv(TABLE_DIR / "eda_summary_stats.csv")

    # 1. class imbalance
    ax = df[TARGET].map({1: "Placed", 0: "Not placed"}).value_counts().plot.bar(color=["#c0504d", "#4f81bd"])
    ax.set_title("Placement distribution"); ax.set_ylabel("Students")
    save("eda_01_placement_distribution.png")

    # 2. correlation heatmap
    num = df.select_dtypes("number").drop(columns=["student_id"])
    plt.figure(figsize=(11, 9))
    sns.heatmap(num.corr(), annot=True, fmt=".2f", cmap="coolwarm", center=0, annot_kws={"size": 7})
    plt.title("Correlation heatmap")
    save("eda_02_correlation_heatmap.png")

    # 3. placement rate by key factors
    fig, axes = plt.subplots(2, 3, figsize=(15, 8))
    for ax, col in zip(axes.ravel(), ["backlogs", "internship_count", "certifications",
                                      "live_projects", "gender", "extracurricular_activities"]):
        (df.groupby(col)[TARGET].mean() * 100).plot.bar(ax=ax, color="#4f81bd")
        ax.set_title(f"Placement rate (%) by {col}"); ax.set_ylabel("%")
    save("eda_03_placement_rate_by_factor.png")

    # 4. numeric features: placed vs not placed
    cols = ["cgpa", "technical_skill_score", "soft_skill_score", "entrance_exam_score",
            "attendance_percentage", "degree_percentage"]
    fig, axes = plt.subplots(2, 3, figsize=(15, 8))
    for ax, col in zip(axes.ravel(), cols):
        sns.boxplot(data=df, x=TARGET, y=col, ax=ax)
        ax.set_xticks([0, 1]); ax.set_xticklabels(["Not placed", "Placed"])
        ax.set_title(col)
    save("eda_04_boxplots_by_placement.png")

    # 5. salary of placed students
    placed = df[df[TARGET] == 1]
    plt.figure(figsize=(7, 4))
    sns.histplot(placed["salary_package_lpa"], bins=25, kde=True)
    plt.title("Salary distribution (placed students only)"); plt.xlabel("LPA")
    save("eda_05_salary_distribution.png")

    # 6. placement rate by CGPA range
    rate = df.groupby(pd.cut(df.cgpa, [5, 6, 7, 8, 9, 10]), observed=True)[TARGET].mean() * 100
    rate.plot.bar(color="#4f81bd", figsize=(7, 4)); plt.title("Placement rate (%) by CGPA range")
    save("eda_06_placement_by_cgpa.png")
    print("EDA figures saved to", FIG_DIR)


if __name__ == "__main__":
    main()
