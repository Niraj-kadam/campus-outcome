"""Experiment 7: K-means clustering of students into profiles.  Usage: python 06_kmeans.py [K]"""
import sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score
from config import SCALED_CSV, CLEAN_CSV, FIG_DIR, TABLE_DIR, TARGET, RANDOM_STATE

K_FINAL = int(sys.argv[1]) if len(sys.argv) > 1 else 4


def main():
    scaled = pd.read_csv(SCALED_CSV)
    X = scaled.drop(columns=[TARGET])
    if not 2 <= K_FINAL < len(X):
        raise ValueError(f"K must be between 2 and {len(X) - 1}; received {K_FINAL}")

    # elbow + silhouette to choose K
    ks, inertia, sil = list(range(2, min(8, len(X) - 1) + 1)), [], []
    for k in ks:
        km = KMeans(n_clusters=k, n_init=10, random_state=RANDOM_STATE).fit(X)
        inertia.append(km.inertia_)
        sil.append(silhouette_score(X, km.labels_, sample_size=2000, random_state=RANDOM_STATE))
    fig, ax = plt.subplots(1, 2, figsize=(11, 4))
    ax[0].plot(ks, inertia, "o-"); ax[0].set_title("Elbow method"); ax[0].set_xlabel("K"); ax[0].set_ylabel("Inertia")
    ax[1].plot(ks, sil, "o-", color="green"); ax[1].set_title("Silhouette score"); ax[1].set_xlabel("K")
    plt.tight_layout(); plt.savefig(FIG_DIR / "km_elbow_silhouette.png", dpi=150); plt.close()
    print("Silhouette by K:", {k: round(s, 3) for k, s in zip(ks, sil)})

    # final model
    km = KMeans(n_clusters=K_FINAL, n_init=10, random_state=RANDOM_STATE).fit(X)
    clean = pd.read_csv(CLEAN_CSV)
    clean["cluster"] = km.labels_
    profile = clean.groupby("cluster").agg(
        students=(TARGET, "size"), placement_rate=(TARGET, "mean"), avg_cgpa=("cgpa", "mean"),
        avg_tech=("technical_skill_score", "mean"), avg_soft=("soft_skill_score", "mean"),
        avg_internships=("internship_count", "mean"), avg_backlogs=("backlogs", "mean"),
        avg_certs=("certifications", "mean"), avg_attendance=("attendance_percentage", "mean")).round(2)
    profile.to_csv(TABLE_DIR / "kmeans_cluster_profile.csv")
    clean.to_csv(TABLE_DIR / "students_with_clusters.csv", index=False)
    print(f"\nK = {K_FINAL}\n", profile.to_string())

    pts = PCA(n_components=2, random_state=RANDOM_STATE).fit_transform(X)
    plt.figure(figsize=(7, 5))
    plt.scatter(pts[:, 0], pts[:, 1], c=km.labels_, cmap="tab10", s=8)
    plt.title(f"K-means clusters (PCA view, K={K_FINAL})"); plt.xlabel("PC1"); plt.ylabel("PC2")
    plt.tight_layout(); plt.savefig(FIG_DIR / "km_clusters_pca.png", dpi=150); plt.close()


if __name__ == "__main__":
    main()
