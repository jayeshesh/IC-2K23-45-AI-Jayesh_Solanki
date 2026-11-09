#!/usr/bin/env python3
"""Train and evaluate a feed-forward PyTorch network for student scores."""
import os
import random
import time

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import torch
from torch import nn
from torch.optim import Adam

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(HERE, "outputs")
MODELS = os.path.join(ROOT, "models")
os.makedirs(OUT, exist_ok=True)
os.makedirs(MODELS, exist_ok=True)


class ScoreNetwork(nn.Module):
    def __init__(self):
        super().__init__()
        self.layers = nn.Sequential(
            nn.Linear(3, 32), nn.ReLU(), nn.Linear(32, 16),
            nn.ReLU(), nn.Linear(16, 1)
        )

    def forward(self, x):
        return self.layers(x)


def main():
    random.seed(42)
    np.random.seed(42)
    torch.manual_seed(42)
    rng = np.random.default_rng(2026)
    n = 300
    hours = rng.uniform(0.5, 8.0, n)
    attendance = rng.uniform(55, 100, n)
    assignment = rng.uniform(40, 100, n)
    noise = rng.normal(0, 3, n)
    score = 24 + 3.5 * hours + 0.20 * attendance + 0.16 * assignment + 0.42 * hours ** 2 + noise
    X = torch.tensor(np.column_stack([hours, attendance, assignment]), dtype=torch.float32)
    y = torch.tensor(score.reshape(-1, 1), dtype=torch.float32)

    order = torch.randperm(n)
    train_ids, valid_ids, test_ids = order[:210], order[210:255], order[255:]
    x_train, y_train = X[train_ids], y[train_ids]
    x_valid, y_valid = X[valid_ids], y[valid_ids]
    x_test, y_test = X[test_ids], y[test_ids]
    x_mean, x_std = x_train.mean(0), x_train.std(0).clamp_min(1e-6)
    y_mean, y_std = y_train.mean(0), y_train.std(0).clamp_min(1e-6)
    norm_x = lambda v: (v - x_mean) / x_std
    norm_y = lambda v: (v - y_mean) / y_std

    model = ScoreNetwork()
    loss_fn = nn.MSELoss()
    optimizer = Adam(model.parameters(), lr=0.01, weight_decay=1e-4)
    train_hist, valid_hist = [], []
    best, best_state, patience = float("inf"), None, 0
    started = time.perf_counter()
    for epoch in range(1, 301):
        model.train()
        pred = model(norm_x(x_train))
        loss = loss_fn(pred, norm_y(y_train))
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        model.eval()
        with torch.no_grad():
            vloss = float(loss_fn(model(norm_x(x_valid)), norm_y(y_valid)).item())
        train_hist.append(float(loss.item()))
        valid_hist.append(vloss)
        if vloss < best - 1e-5:
            best, patience = vloss, 0
            best_state = {k: v.detach().clone() for k, v in model.state_dict().items()}
        else:
            patience += 1
        if patience >= 35:
            break
    model.load_state_dict(best_state)
    model.eval()
    with torch.no_grad():
        prediction = model(norm_x(x_test)) * y_std + y_mean
    error = prediction - y_test
    mae = float(error.abs().mean().item())
    rmse = float(error.square().mean().sqrt().item())
    print(f"Dataset: {n} synthetic samples | Split: 210/45/45")
    print(f"Early stopping epoch: {len(train_hist)}")
    print(f"Test MAE: {mae:.3f} score points")
    print(f"Test RMSE: {rmse:.3f} score points")
    print(f"Training time: {time.perf_counter() - started:.3f} seconds")

    plt.figure(figsize=(7, 4))
    plt.plot(train_hist, label="Training")
    plt.plot(valid_hist, label="Validation")
    plt.xlabel("Epoch")
    plt.ylabel("Normalized MSE")
    plt.title("Student Score Network Loss")
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(OUT, "student_network_loss.svg"))
    plt.close()

    checkpoint = {
        "state_dict": model.state_dict(), "input_mean": x_mean,
        "input_std": x_std, "target_mean": y_mean, "target_std": y_std,
        "features": ["study_hours", "attendance_percent", "assignment_average"],
        "test_mae": mae, "test_rmse": rmse,
    }
    torch.save(checkpoint, os.path.join(MODELS, "student_score_network.pt"))
    print("Saved models/student_score_network.pt and student_network_loss.svg")


if __name__ == "__main__":
    main()
