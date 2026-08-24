from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


METRICS_PATH = Path(
    "data/validation/ml_scenario_holdout_metrics.csv"
)

INPUT_DATA_PATH = Path(
    "data/validation/risk_inference_results.csv"
)

OUTPUT_DIR = Path("docs/figures")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


MODEL_LABELS = {
    "logistic_regression": "Logistic Regression",
    "decision_tree": "Decision Tree",
    "random_forest": "Random Forest",
    "gradient_boosting": "Gradient Boosting",
}


def plot_macro_f1_by_scenario(metrics: pd.DataFrame) -> None:
    pivot = metrics.pivot(
        index="test_scenario",
        columns="model",
        values="f1_macro",
    )

    pivot = pivot[
        [
            "logistic_regression",
            "decision_tree",
            "random_forest",
            "gradient_boosting",
        ]
    ]

    pivot.columns = [
        MODEL_LABELS[column]
        for column in pivot.columns
    ]

    ax = pivot.plot(
        kind="bar",
        figsize=(8.0, 4.8),
        width=0.8,
    )

    ax.set_xlabel("Held-out FDS scenario")
    ax.set_ylabel("Macro-F1 score")
    ax.set_ylim(0.0, 1.0)

    ax.legend(
        title="Classifier",
        fontsize=8,
        title_fontsize=8,
    )

    ax.grid(
        axis="y",
        alpha=0.25,
    )

    plt.xticks(rotation=0)
    plt.tight_layout()

    plt.savefig(
        OUTPUT_DIR / "ml_macro_f1_by_heldout_scenario.pdf",
        bbox_inches="tight",
    )

    plt.savefig(
        OUTPUT_DIR / "ml_macro_f1_by_heldout_scenario.png",
        dpi=300,
        bbox_inches="tight",
    )

    plt.close()


def plot_class_distribution(df: pd.DataFrame) -> None:
    class_order = [
        "baixo",
        "moderado",
        "alto",
    ]

    scenario_order = [
        "S1",
        "S2",
        "S3",
    ]

    counts = pd.crosstab(
        df["scenario"],
        df["risk_level_reference"],
    )

    counts = counts.reindex(
        index=scenario_order,
        columns=class_order,
        fill_value=0,
    )

    counts.columns = [
        "Low",
        "Moderate",
        "High",
    ]

    ax = counts.plot(
        kind="bar",
        figsize=(7.2, 4.6),
        width=0.75,
    )

    ax.set_xlabel("FDS scenario")
    ax.set_ylabel("Number of samples")

    ax.legend(
        title="Reference risk class",
        fontsize=8,
        title_fontsize=8,
    )

    ax.grid(
        axis="y",
        alpha=0.25,
    )

    plt.xticks(rotation=0)
    plt.tight_layout()

    plt.savefig(
        OUTPUT_DIR / "risk_class_distribution_by_scenario.pdf",
        bbox_inches="tight",
    )

    plt.savefig(
        OUTPUT_DIR / "risk_class_distribution_by_scenario.png",
        dpi=300,
        bbox_inches="tight",
    )

    plt.close()


def main() -> None:
    if not METRICS_PATH.exists():
        raise FileNotFoundError(
            f"Metrics file not found: {METRICS_PATH}"
        )

    if not INPUT_DATA_PATH.exists():
        raise FileNotFoundError(
            f"Input dataset not found: {INPUT_DATA_PATH}"
        )

    metrics = pd.read_csv(METRICS_PATH)
    df = pd.read_csv(INPUT_DATA_PATH)

    plot_macro_f1_by_scenario(metrics)
    plot_class_distribution(df)

    print("[OK] Figures generated in:")
    print(f"     {OUTPUT_DIR}")

    for path in sorted(OUTPUT_DIR.iterdir()):
        print(f"     {path}")


if __name__ == "__main__":
    main()
