from __future__ import annotations

from pathlib import Path

import pandas as pd
from sklearn.ensemble import (
    GradientBoostingClassifier,
    RandomForestClassifier,
)
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    precision_recall_fscore_support,
)
from sklearn.tree import DecisionTreeClassifier


# ---------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------

INPUT_PATH = Path(
    "data/validation/risk_inference_results.csv"
)

METRICS_OUTPUT = Path(
    "data/validation/ml_scenario_holdout_metrics.csv"
)

CONFUSION_OUTPUT = Path(
    "data/validation/ml_scenario_holdout_confusion_matrices.csv"
)

SUMMARY_OUTPUT = Path(
    "data/validation/ml_scenario_holdout_summary.csv"
)

FEATURES = [
    "mean_temp",
    "max_temp",
    "min_visibility",
    "max_co_ppm",
    "mean_smoke_velocity",
    "mean_temp_rate",
    "mean_soft_sensor_index",
    "mean_distance_to_fire_m",
]

TARGET = "risk_level_reference"

LABELS = [
    "baixo",
    "moderado",
    "alto",
]

SCENARIOS = [
    "S1",
    "S2",
    "S3",
]


def build_models():
    """
    Return the supervised classifiers evaluated in the study.

    Hyperparameters reproduce the baseline model definitions used
    in app/ml/run_ml.py.
    """
    return {
        "logistic_regression": LogisticRegression(
            max_iter=2000,
            random_state=42,
        ),
        "decision_tree": DecisionTreeClassifier(
            max_depth=6,
            random_state=42,
        ),
        "random_forest": RandomForestClassifier(
            n_estimators=200,
            random_state=42,
            max_depth=8,
            min_samples_leaf=2,
        ),
        "gradient_boosting": GradientBoostingClassifier(
            random_state=42,
        ),
    }


def validate_dataset(df: pd.DataFrame) -> None:
    """
    Validate the minimum schema required for scenario-wise holdout.
    """
    required_columns = (
        FEATURES
        + [
            TARGET,
            "scenario",
        ]
    )

    missing = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing:
        raise KeyError(
            "Required columns missing from dataset: "
            f"{missing}"
        )

    available_scenarios = set(
        df["scenario"].dropna().astype(str).unique()
    )

    missing_scenarios = (
        set(SCENARIOS) - available_scenarios
    )

    if missing_scenarios:
        raise ValueError(
            "Expected scenarios not found in dataset: "
            f"{sorted(missing_scenarios)}"
        )


def class_distribution(
    y: pd.Series,
) -> dict[str, int]:
    """
    Return counts for every reference class, including absent classes.
    """
    counts = y.value_counts()

    return {
        label: int(counts.get(label, 0))
        for label in LABELS
    }


def run_scenario_holdout(
    df: pd.DataFrame,
) -> tuple[
    pd.DataFrame,
    pd.DataFrame,
]:
    """
    Perform leave-one-scenario-out evaluation.

    For each fold:
        train = two complete FDS scenarios
        test  = one complete unseen FDS scenario

    Four classifiers are independently trained and evaluated.
    """

    metrics_rows = []
    confusion_rows = []

    for test_scenario in SCENARIOS:

        train_df = df[
            df["scenario"] != test_scenario
        ].copy()

        test_df = df[
            df["scenario"] == test_scenario
        ].copy()

        X_train = (
            train_df[FEATURES]
            .fillna(0)
        )

        y_train = (
            train_df[TARGET]
            .astype(str)
        )

        X_test = (
            test_df[FEATURES]
            .fillna(0)
        )

        y_test = (
            test_df[TARGET]
            .astype(str)
        )

        train_distribution = class_distribution(
            y_train
        )

        test_distribution = class_distribution(
            y_test
        )

        print("\n" + "=" * 72)
        print(
            f"HELD-OUT SCENARIO: {test_scenario}"
        )
        print(
            "TRAIN SCENARIOS:",
            sorted(
                train_df["scenario"]
                .unique()
                .tolist()
            ),
        )

        print("\nTraining class distribution:")
        print(y_train.value_counts())

        print("\nTest class distribution:")
        print(y_test.value_counts())

        models = build_models()

        for model_name, model in models.items():

            model.fit(
                X_train,
                y_train,
            )

            y_pred = model.predict(
                X_test
            )

            accuracy = accuracy_score(
                y_test,
                y_pred,
            )

            (
                precision_macro,
                recall_macro,
                f1_macro,
                _,
            ) = precision_recall_fscore_support(
                y_test,
                y_pred,
                labels=LABELS,
                average="macro",
                zero_division=0,
            )

            cm = confusion_matrix(
                y_test,
                y_pred,
                labels=LABELS,
            )

            metrics_rows.append(
                {
                    "test_scenario": test_scenario,
                    "train_scenarios": "+".join(
                        sorted(
                            train_df[
                                "scenario"
                            ]
                            .unique()
                            .tolist()
                        )
                    ),
                    "model": model_name,
                    "accuracy": accuracy,
                    "precision_macro": (
                        precision_macro
                    ),
                    "recall_macro": (
                        recall_macro
                    ),
                    "f1_macro": f1_macro,
                    "n_train": len(train_df),
                    "n_test": len(test_df),
                    "train_low": (
                        train_distribution[
                            "baixo"
                        ]
                    ),
                    "train_moderate": (
                        train_distribution[
                            "moderado"
                        ]
                    ),
                    "train_high": (
                        train_distribution[
                            "alto"
                        ]
                    ),
                    "test_low": (
                        test_distribution[
                            "baixo"
                        ]
                    ),
                    "test_moderate": (
                        test_distribution[
                            "moderado"
                        ]
                    ),
                    "test_high": (
                        test_distribution[
                            "alto"
                        ]
                    ),
                }
            )

            for true_index, true_label in enumerate(
                LABELS
            ):
                for pred_index, pred_label in enumerate(
                    LABELS
                ):
                    confusion_rows.append(
                        {
                            "test_scenario": (
                                test_scenario
                            ),
                            "model": model_name,
                            "true_label": (
                                true_label
                            ),
                            "predicted_label": (
                                pred_label
                            ),
                            "count": int(
                                cm[
                                    true_index,
                                    pred_index,
                                ]
                            ),
                        }
                    )

            print(
                f"\nModel: {model_name}"
            )
            print(
                f"Accuracy : {accuracy:.4f}"
            )
            print(
                "Precision: "
                f"{precision_macro:.4f}"
            )
            print(
                f"Recall   : {recall_macro:.4f}"
            )
            print(
                f"F1 macro : {f1_macro:.4f}"
            )
            print("Confusion matrix:")
            print(cm)

    metrics_df = pd.DataFrame(
        metrics_rows
    )

    confusion_df = pd.DataFrame(
        confusion_rows
    )

    return (
        metrics_df,
        confusion_df,
    )


def build_summary(
    metrics_df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Compute mean performance across held-out scenarios.

    These averages summarize inter-scenario generalization.
    """
    summary_df = (
        metrics_df
        .groupby(
            "model",
            as_index=False,
        )
        .agg(
            mean_accuracy=(
                "accuracy",
                "mean",
            ),
            mean_precision_macro=(
                "precision_macro",
                "mean",
            ),
            mean_recall_macro=(
                "recall_macro",
                "mean",
            ),
            mean_f1_macro=(
                "f1_macro",
                "mean",
            ),
        )
        .sort_values(
            "mean_f1_macro",
            ascending=False,
        )
    )

    return summary_df


def main() -> None:

    if not INPUT_PATH.exists():
        raise FileNotFoundError(
            f"Input dataset not found: "
            f"{INPUT_PATH}"
        )

    df = pd.read_csv(
        INPUT_PATH
    )

    validate_dataset(df)

    print(
        f"[ML-HOLDOUT] Dataset: "
        f"{INPUT_PATH}"
    )

    print(
        f"[ML-HOLDOUT] Samples: "
        f"{len(df)}"
    )

    print(
        "\n[ML-HOLDOUT] Global class "
        "distribution:"
    )

    print(
        df[TARGET].value_counts()
    )

    metrics_df, confusion_df = (
        run_scenario_holdout(df)
    )

    summary_df = build_summary(
        metrics_df
    )

    METRICS_OUTPUT.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    metrics_df.to_csv(
        METRICS_OUTPUT,
        index=False,
    )

    confusion_df.to_csv(
        CONFUSION_OUTPUT,
        index=False,
    )

    summary_df.to_csv(
        SUMMARY_OUTPUT,
        index=False,
    )

    print("\n" + "=" * 72)
    print(
        "SCENARIO-WISE HOLDOUT SUMMARY"
    )
    print("=" * 72)

    print(
        metrics_df[
            [
                "test_scenario",
                "model",
                "accuracy",
                "precision_macro",
                "recall_macro",
                "f1_macro",
            ]
        ]
        .sort_values(
            [
                "test_scenario",
                "f1_macro",
            ],
            ascending=[
                True,
                False,
            ],
        )
        .to_string(index=False)
    )

    print(
        "\nMEAN PERFORMANCE ACROSS "
        "HELD-OUT SCENARIOS"
    )

    print(
        summary_df.to_string(
            index=False
        )
    )

    print(
        "\n[OK] Metrics saved to:"
    )
    print(
        f"     {METRICS_OUTPUT}"
    )

    print(
        "[OK] Confusion matrices saved to:"
    )
    print(
        f"     {CONFUSION_OUTPUT}"
    )

    print(
        "[OK] Summary saved to:"
    )
    print(
        f"     {SUMMARY_OUTPUT}"
    )


if __name__ == "__main__":
    main()
