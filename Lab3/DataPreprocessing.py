#!/usr/bin/env python3
"""
Lab 3: AI Programming Frameworks & Data Preparation Pipeline.

Course : Artificial Intelligence Laboratory (IC-703 C / IC-709D)
Unit   : Unit 3 - Data Preparation, EDA & Feature Engineering (CO2, CO5)
Author : Jayesh Solanki (Roll No: IC-2K23-45)

Covers all Unit 3 Laboratory Activities:
  1. Dataset Loading (Campus Placement dataset)
  2. Exploratory Data Analysis (EDA) & Summary Statistics
  3. Data Cleaning & Domain Missing Value Imputation
  4. Categorical Encoding (Label Encoding & One-Hot Encoding)
  5. Feature Scaling (StandardScaler vs MinMaxScaler)
  6. Feature Selection (ANOVA F-test & Mutual Information)
  7. Leak-Free Train-Test Split Modeling Pipeline
  8. Data Visualizations (Saved to outputs/)
"""

from typing import Tuple

import os
import sys
import matplotlib
matplotlib.use("Agg")  # Headless rendering
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.feature_selection import f_classif, mutual_info_classif
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, MinMaxScaler, StandardScaler

LINE_WIDTH = 74
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.abspath(os.path.join(BASE_DIR, "..", "datasets", "placement.csv"))
OUT_DIR = os.path.join(BASE_DIR, "outputs")
os.makedirs(OUT_DIR, exist_ok=True)


def print_banner(title: str) -> None:
    print("=" * LINE_WIDTH)
    print(f" {title}")
    print("=" * LINE_WIDTH)


def load_dataset() -> pd.DataFrame:
    if not os.path.exists(DATA_PATH):
        raise FileNotFoundError(f"Missing placement dataset at: {DATA_PATH}")
    df = pd.read_csv(DATA_PATH)
    print(f"Loaded dataset: {df.shape[0]} rows, {df.shape[1]} columns.\n")
    return df


def perform_eda(df: pd.DataFrame) -> None:
    print_banner("1. EXPLORATORY DATA ANALYSIS (EDA)")
    print("Dataset Info:")
    print(df.info())
    print("\nStatistical Summary (Numerical Features):")
    print(df.describe().round(2))

    print("\nClass Distribution (Target: 'status'):")
    status_counts = df["status"].value_counts()
    for st, count in status_counts.items():
        print(f"  {st:<12}: {count:>3} ({count/len(df)*100:.1f}%)")
    print()


def clean_and_impute(df: pd.DataFrame) -> pd.DataFrame:
    print_banner("2. DATA CLEANING & DOMAIN IMPUTATION")
    df_clean = df.copy()

    # Drop non-predictive identifier column
    if "sl_no" in df_clean.columns:
        df_clean.drop(columns=["sl_no"], inplace=True)
        print("Dropped identifier: 'sl_no'")

    # Domain-specific missing value handling for 'salary'
    # In placement data, unplaced candidates naturally have NaN salary
    null_salary = df_clean["salary"].isnull().sum()
    print(f"Missing values in 'salary': {null_salary} (Unplaced candidates)")
    df_clean["salary"] = df_clean["salary"].fillna(0)
    print("Imputed unplaced candidates salary with 0.0\n")

    return df_clean


def encode_features(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.Series]:
    print_banner("3. CATEGORICAL ENCODING & PIPELINE SPLITTING")
    df_encoded = df.copy()

    # Encode target: Placed -> 1, Not Placed -> 0
    target_le = LabelEncoder()
    y = pd.Series(target_le.fit_transform(df_encoded["status"]), name="status")
    df_encoded.drop(columns=["status", "salary"], inplace=True)  # Exclude salary from predictors

    # Binary columns: gender, ssc_b, hsc_b, workex
    binary_cols = ["gender", "ssc_b", "hsc_b", "workex"]
    for col in binary_cols:
        le = LabelEncoder()
        df_encoded[col] = le.fit_transform(df_encoded[col])
        print(f"Label Encoded binary feature: '{col}' -> {list(le.classes_)}")

    # Multi-class nominal columns: hsc_s, degree_t, specialisation
    multi_cols = ["hsc_s", "degree_t", "specialisation"]
    df_encoded = pd.get_dummies(df_encoded, columns=multi_cols, drop_first=True)
    print(f"One-Hot Encoded nominal features: {multi_cols}")
    print(f"Predictor feature matrix shape: {df_encoded.shape}\n")

    return df_encoded, y


def feature_selection_and_scaling(
    X: pd.DataFrame, y: pd.Series
) -> None:
    print_banner("4. LEAK-FREE SPLIT, FEATURE SELECTION & SCALING")

    # 1. Leak-free train-test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    print(f"Training set: {X_train.shape[0]} samples | Test set: {X_test.shape[0]} samples")

    # 2. ANOVA F-score Feature Selection (Strictly on Training set)
    f_scores, p_values = f_classif(X_train, y_train)
    mi_scores = mutual_info_classif(X_train, y_train, random_state=42)

    stats_df = pd.DataFrame({
        "Feature": X_train.columns,
        "ANOVA_F": f_scores,
        "p_value": p_values,
        "Mutual_Info": mi_scores
    }).sort_values(by="ANOVA_F", ascending=False)

    print("\nFeature Importance Ranking (ANOVA F-Test & Mutual Information):")
    print(f"  {'Feature':<28} {'ANOVA F':<12} {'p-value':<12} {'Mutual Info':<10}")
    print("  " + "-" * (LINE_WIDTH - 2))
    for _, r in stats_df.iterrows():
        print(f"  {r['Feature']:<28} {r['ANOVA_F']:<12.2f} {r['p_value']:<12.4e} {r['Mutual_Info']:<10.3f}")
    print()

    # 3. Scaling comparison: StandardScaler vs MinMaxScaler
    num_cols = ["ssc_p", "hsc_p", "degree_p", "etest_p", "mba_p"]
    std_scaler = StandardScaler()
    minmax_scaler = MinMaxScaler()

    X_train_std = std_scaler.fit_transform(X_train[num_cols])
    X_train_mm = minmax_scaler.fit_transform(X_train[num_cols])

    print("Scaling Comparison (Academic Percentages):")
    print(f"  StandardScaler -> Mean: {X_train_std.mean(axis=0).round(2)}, Std: {X_train_std.std(axis=0).round(2)}")
    print(f"  MinMaxScaler   -> Min: {X_train_mm.min(axis=0).round(2)}, Max: {X_train_mm.max(axis=0).round(2)}\n")


def generate_visualizations(df: pd.DataFrame) -> None:
    print_banner("5. GENERATING DATA VISUALIZATIONS")

    # Visual 1: Academic Scores Distribution by Placement Status
    plt.figure(figsize=(9, 5))
    sns.boxplot(x="status", y="ssc_p", data=df, palette="Blues")
    plt.title("Secondary School Percentage (ssc_p) vs Placement Status", fontsize=13)
    plt.xlabel("Placement Status")
    plt.ylabel("Percentage (%)")
    plt.tight_layout()
    p1 = os.path.join(OUT_DIR, "placement_status_distribution.png")
    plt.savefig(p1, dpi=200)
    plt.close()
    print("Saved visualization:", os.path.basename(p1))

    # Visual 2: Correlation Heatmap
    num_df = df.select_dtypes(include=[np.number])
    plt.figure(figsize=(8, 6))
    sns.heatmap(num_df.corr(), annot=True, cmap="coolwarm", fmt=".2f", linewidths=0.5)
    plt.title("Academic Marks Correlation Heatmap", fontsize=13)
    plt.tight_layout()
    p2 = os.path.join(OUT_DIR, "feature_correlation_analysis.png")
    plt.savefig(p2, dpi=200)
    plt.close()
    print("Saved visualization:", os.path.basename(p2))


def main() -> int:
    print_banner("LAB 3: AI DATA PREPARATION PIPELINE & EDA")
    print("Author: Jayesh Solanki | Roll No: IC-2K23-45 | MCA AI Lab (IC-703 C)\n")

    raw_df = load_dataset()
    perform_eda(raw_df)
    clean_df = clean_and_impute(raw_df)
    X, y = encode_features(clean_df)
    feature_selection_and_scaling(X, y)
    generate_visualizations(raw_df)

    print_banner("PIPELINE COMPLETED SUCCESSFULLY!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
