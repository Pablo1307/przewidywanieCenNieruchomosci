import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def analyze(frame, output):
    """EDA only on the training partition, including unused source columns."""
    counts, edges = np.histogram(frame.SalePrice, bins=24)
    correlations = frame.select_dtypes(include="number").drop(columns=["Id"], errors="ignore").corr()["SalePrice"].drop("SalePrice").dropna()
    q1, q3 = frame.SalePrice.quantile([0.25, 0.75])
    low, high = float(q1 - 1.5 * (q3 - q1)), float(q3 + 1.5 * (q3 - q1))
    outliers = frame[(frame.SalePrice < low) | (frame.SalePrice > high)]
    result = {
        "scope": "Wyłącznie część treningowa (80%). Odstających obserwacji nie usuwamy.",
        "rows": len(frame),
        "histogram": [{"price": round(float((edges[i] + edges[i + 1]) / 2)), "count": int(count)} for i, count in enumerate(counts)],
        "missing": [{"feature": col, "count": int(count)} for col, count in frame.isna().sum().sort_values(ascending=False).items() if count],
        "dtypes": {col: str(dtype) for col, dtype in frame.dtypes.items()},
        "correlations": [{"feature": col, "value": float(correlations[col])} for col in correlations.abs().sort_values(ascending=False).head(15).index],
        "outliers": {"method": "SalePrice: 1.5 × IQR", "lower": low, "upper": high, "count": len(outliers), "row_indices": outliers.index.tolist()},
    }
    output.mkdir(parents=True, exist_ok=True)
    fig, axes = plt.subplots(1, 3, figsize=(16, 5))
    axes[0].hist(frame.SalePrice, bins=24, color="#16766b")
    axes[0].set(title="SalePrice (train)", xlabel="USD", ylabel="Liczba domów")
    axes[1].boxplot(frame.SalePrice)
    axes[1].set(title="Obserwacje odstające", ylabel="USD")
    top = correlations.loc[correlations.abs().nlargest(12).index].sort_values()
    top.plot.barh(ax=axes[2], color="#16766b", title="Korelacje Pearsona")
    fig.tight_layout()
    fig.savefig(output / "eda.png", dpi=160)
    plt.close(fig)
    return result
