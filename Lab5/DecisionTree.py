#!/usr/bin/env python3
"""Lab 5: Decision Tree Classification and Model Evaluation.

Uses the shared Campus Placement dataset. The target is status; sl_no and
salary are excluded from predictors to avoid identifier/target leakage.
"""
from __future__ import annotations

import argparse
import os
import sys
import time
from typing import Any

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.metrics import (
    ConfusionMatrixDisplay,
    accuracy_score,
    classification_report,
    confusion_matrix,
    precision_recall_fscore_support,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.tree import DecisionTreeClassifier, plot_tree

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_DIR = os.path.dirname(BASE_DIR)
DEFAULT_DATA = os.path.join(REPO_DIR, "datasets", "placement.csv")
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")
os.makedirs(OUTPUT_DIR, exist_ok=True)


def build_pipeline(X: pd.DataFrame, max_depth: int | None = 4) -> Pipeline:
    """Build preprocessing and decision-tree steps using training columns."""
    numeric_columns = X.select_dtypes(include=[np.number]).columns.tolist()
    categorical_columns = [
        column for column in X.columns if column not in numeric_columns
    ]
    numeric_pipeline = Pipeline(
        steps=[("imputer", SimpleImputer(strategy="median"))]
    )
    categorical_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("encoder", OneHotEncoder(handle_unknown="ignore")),
        ]
    )
    preprocessing = ColumnTransformer(
        transformers=[
            ("numeric", numeric_pipeline, numeric_columns),
            ("categorical", categorical_pipeline, categorical_columns),
        ]
    )
    classifier = DecisionTreeClassifier(
        criterion="gini",
        max_depth=max_depth,
        min_samples_leaf=3,
        random_state=42,
    )
    return Pipeline(
        steps=[("preprocessor", preprocessing), ("classifier", classifier)]
    )


def load_data(data_path: str) -> tuple[pd.DataFrame, pd.Series]:
    if not os.path.isfile(data_path):
        raise FileNotFoundError(
            f"Dataset not found: {data_path}. Run from the repository root or use --data."
        )
    frame = pd.read_csv(data_path)
    required = {"status", "sl_no", "salary"}
    missing = required.difference(frame.columns)
    if missing:
        raise ValueError(f"Dataset is missing required columns: {sorted(missing)}")
    y = frame["status"].astype(str)
    # Salary reveals placement outcome in this dataset and must not be a feature.
    X = frame.drop(columns=["status", "sl_no", "salary"])
    if X.empty or y.nunique() < 2:
        raise ValueError("Need predictor columns and at least two target classes.")
    return X, y


def save_visualizations(
    model: Pipeline,
    X_test: pd.DataFrame,
    y_test: pd.Series,
    predictions: np.ndarray,
) -> tuple[str, str]:
    labels = sorted(y_test.unique().tolist())
    matrix = confusion_matrix(y_test, predictions, labels=labels)
    matrix_path = os.path.join(OUTPUT_DIR, "confusion_matrix.svg")
    display = ConfusionMatrixDisplay(
        confusion_matrix=matrix, display_labels=labels
    )
    display.plot(cmap="Blues", values_format="d")
    plt.title("Decision Tree - Confusion Matrix")
    plt.tight_layout()
    plt.savefig(matrix_path, format="svg", bbox_inches="tight")
    plt.close()

    preprocessor = model.named_steps["preprocessor"]
    classifier = model.named_steps["classifier"]
    feature_names = preprocessor.get_feature_names_out()
    tree_path = os.path.join(OUTPUT_DIR, "decision_tree.svg")
    plt.figure(figsize=(18, 10))
    plot_tree(
        classifier,
        feature_names=feature_names,
        class_names=[str(label) for label in classifier.classes_],
        filled=True,
        rounded=True,
        fontsize=7,
    )
    plt.title("Campus Placement Decision Tree")
    plt.tight_layout()
    plt.savefig(tree_path, format="svg", bbox_inches="tight")
    plt.close()
    return matrix_path, tree_path


def run_experiment(
    data_path: str = DEFAULT_DATA, max_depth: int = 4
) -> dict[str, Any]:
    start = time.perf_counter()
    X, y = load_data(data_path)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    model = build_pipeline(X_train, max_depth=max_depth)
    model.fit(X_train, y_train)
    predictions = model.predict(X_test)
    elapsed = time.perf_counter() - start

    accuracy = accuracy_score(y_test, predictions)
    precision, recall, f1, _ = precision_recall_fscore_support(
        y_test, predictions, average="weighted", zero_division=0
    )
    matrix = confusion_matrix(y_test, predictions, labels=sorted(y.unique()))
    matrix_path, tree_path = save_visualizations(
        model, X_test, y_test, predictions
    )
    preprocessor = model.named_steps["preprocessor"]
    classifier = model.named_steps["classifier"]
    feature_names = preprocessor.get_feature_names_out()
    importance = pd.Series(
        classifier.feature_importances_, index=feature_names
    ).sort_values(ascending=False)

    print("=" * 72)
    print("LAB 5: DECISION TREE CLASSIFIER AND MODEL EVALUATION")
    print("=" * 72)
    print(f"Dataset: {os.path.basename(data_path)}")
    print(f"Samples: {len(X)} | Predictors: {X.shape[1]}")
    print(f"Training samples: {len(X_train)} | Test samples: {len(X_test)}")
    print("Excluded columns: sl_no (identifier), salary (target leakage)")
    print(f"Tree depth limit: {max_depth}")
    print("\nPerformance Metrics (weighted average):")
    print(f"Accuracy : {accuracy:.4f}")
    print(f"Precision: {precision:.4f}")
    print(f"Recall   : {recall:.4f}")
    print(f"F1-score : {f1:.4f}")
    print("\nClassification Report:")
    print(classification_report(y_test, predictions, zero_division=0))
    print("Confusion Matrix (actual rows, predicted columns):")
    print(matrix)
    print("\nTop Feature Importances:")
    for feature, value in importance.head(8).items():
        print(f"  {feature:<34} {value:.4f}")
    print(f"\nExecution time: {elapsed:.4f} seconds")
    print(f"Saved: {os.path.relpath(matrix_path, REPO_DIR)}")
    print(f"Saved: {os.path.relpath(tree_path, REPO_DIR)}")
    print("=" * 72)
    return {
        "model": model,
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "matrix": matrix,
        "report": classification_report(y_test, predictions, zero_division=0),
        "samples": len(X),
        "train_samples": len(X_train),
        "test_samples": len(X_test),
        "execution_time": elapsed,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Train and evaluate a placement decision tree."
    )
    parser.add_argument("--data", default=DEFAULT_DATA, help="Path to placement CSV.")
    parser.add_argument(
        "--max-depth", type=int, default=4, help="Maximum tree depth (default: 4)."
    )
    args = parser.parse_args()
    if args.max_depth < 1:
        parser.error("--max-depth must be at least 1")
    try:
        run_experiment(args.data, args.max_depth)
    except (FileNotFoundError, ValueError, KeyError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
