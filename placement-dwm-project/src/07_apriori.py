"""Experiment 8 (optional): Apriori frequent pattern mining on binned attributes."""
import pandas as pd
from mlxtend.frequent_patterns import apriori, association_rules
from config import RAW_CSV, TABLE_DIR

MIN_SUPPORT = 0.03
MIN_CONFIDENCE = 0.3     # placement is only ~17% of data, so high confidence thresholds find nothing


def cut(s, bins, labels):
    return pd.cut(s, bins, labels=labels, include_lowest=True).astype(str)


def main():
    df = pd.read_csv(RAW_CSV)
    L3 = ["Low", "Mid", "High"]
    items = pd.DataFrame({
        "CGPA": cut(df.cgpa, [0, 6.5, 8, 10], L3),
        "Tech": cut(df.technical_skill_score, [0, 55, 75, 100], L3),
        "Soft": cut(df.soft_skill_score, [0, 55, 75, 100], L3),
        "Internships": cut(df.internship_count, [-1, 1, 2, 4], ["0-1", "2", "3-4"]),
        "Certs": cut(df.certifications, [-1, 1, 3, 5], ["0-1", "2-3", "4-5"]),
        "Backlogs": cut(df.backlogs, [-1, 0, 2, 5], ["0", "1-2", "3-5"]),
        "Projects": cut(df.live_projects, [-1, 1, 3, 5], ["0-1", "2-3", "4-5"]),
        "Placement": df.placement_status.map({1: "Placed", 0: "NotPlaced"}),
    })
    onehot = pd.get_dummies(items, prefix_sep="=").astype(bool)   # columns like "Backlogs=0"

    freq = apriori(onehot, min_support=MIN_SUPPORT, use_colnames=True)
    freq["itemset"] = freq["itemsets"].apply(lambda s: ", ".join(sorted(s)))
    freq.drop(columns="itemsets").sort_values("support", ascending=False).to_csv(
        TABLE_DIR / "apriori_frequent_itemsets.csv", index=False)

    rules = association_rules(freq, metric="confidence", min_threshold=MIN_CONFIDENCE)
    # keep rules whose consequent is exactly "Placed" (the useful ones for this project)
    rules = rules[rules["consequents"].apply(lambda s: s == frozenset({"Placement=Placed"}))]
    rules = rules.sort_values(["lift", "confidence"], ascending=False)
    out = rules.assign(antecedents=rules["antecedents"].apply(lambda s: ", ".join(sorted(s))))[
        ["antecedents", "support", "confidence", "lift"]].round(3)
    out.to_csv(TABLE_DIR / "apriori_rules_to_placed.csv", index=False)
    print(f"{len(freq)} frequent itemsets; {len(out)} rules -> Placed")
    print(out.head(10).to_string(index=False))
    if out.empty:
        print("No rules found: lower MIN_SUPPORT / MIN_CONFIDENCE.")


if __name__ == "__main__":
    main()
