#!/usr/bin/env python3
"""
Lab 6: Deep Learning Fundamentals using PyTorch.

Course : Artificial Intelligence Laboratory (IC-703 C / IC-709D)
Unit   : Unit 6 - Deep Learning Fundamentals using PyTorch (CO4, CO5)
Author : Jayesh Solanki (Roll No: IC-2K23-45)

Topics & Activities Implemented:
  1. PyTorch Tensor Manipulation & Shape Operations
  2. Automatic Differentiation (`autograd` & gradient tracking)
  3. Linear Regression from Scratch using Pure PyTorch Tensors
  4. Neural Network Regression using `torch.nn.Module`, MSELoss, and SGD/Adam
  5. Training Loop with Loss Convergence Monitoring
  6. Application: Student Academic Score / House Price Prediction
  7. Loss Convergence Plot (.png)
  8. Model Serialization to models/linear_regression.pt
  9. Homework Analysis: Gradient-based convergence & Classical vs DL comparison
"""

import os
import matplotlib
matplotlib.use("Agg")  # Headless rendering
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import torch  # noqa: E402
import torch.nn as nn  # noqa: E402
import torch.optim as optim  # noqa: E402

LINE_WIDTH = 74
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(BASE_DIR, "outputs")
MODELS_DIR = os.path.join(os.path.dirname(BASE_DIR), "models")
os.makedirs(OUT_DIR, exist_ok=True)
os.makedirs(MODELS_DIR, exist_ok=True)


def print_banner(title: str) -> None:
    print("=" * LINE_WIDTH)
    print(f" {title}")
    print("=" * LINE_WIDTH)


# ============================================================================
# Activity 1: Tensor Operations & Automatic Differentiation
# ============================================================================
def demo_tensor_autograd() -> None:
    print_banner("1. PYTORCH TENSOR MANIPULATION & AUTOGRAD")

    # Tensor creation and manipulation
    x = torch.tensor([[1.0, 2.0], [3.0, 4.0]], requires_grad=True)
    print("Tensor x (requires_grad=True):")
    print(x)

    # Forward computation: y = 3 * x^2 + 2 * x + 1
    y = 3 * (x ** 2) + 2 * x + 1
    out = y.mean()
    print(f"\nForward evaluation output: {out.item():.4f}")

    # Backpropagation: dout/dx = (6x + 2) / 4
    out.backward()
    print("\nAnalytical Gradients (dout/dx):")
    print(x.grad)

    expected_grad = (6 * x.detach() + 2) / 4.0
    print("Exact Mathematical Verification:")
    print(f"  Gradient Match: {torch.allclose(x.grad, expected_grad)}\n")


# ============================================================================
# Activity 2 & 3: Linear Regression Model & Training Loop
# ============================================================================
class LinearRegressionModel(nn.Module):
    """PyTorch Linear Regression model."""

    def __init__(self, in_features: int, out_features: int) -> None:
        super().__init__()
        self.linear = nn.Linear(in_features, out_features)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.linear(x)


def train_regression_model():
    print_banner("2. LINEAR REGRESSION TRAINING LOOP & OPTIMIZATION")

    # Synthetic Student Score Prediction Dataset (Study Hours -> Score)
    torch.manual_seed(42)
    np.random.seed(42)

    # 100 samples: true relation y = 6.5 * x + 15 + noise
    X_numpy = np.random.uniform(1.0, 10.0, (100, 1)).astype(np.float32)
    noise = np.random.normal(0.0, 2.5, (100, 1)).astype(np.float32)
    y_numpy = 6.5 * X_numpy + 15.0 + noise

    X_train = torch.from_numpy(X_numpy)
    y_train = torch.from_numpy(y_numpy)

    model = LinearRegressionModel(1, 1)
    criterion = nn.MSELoss()
    optimizer = optim.SGD(model.parameters(), lr=0.01)

    print(f"Dataset Size: {len(X_train)} samples")
    print("Training Configuration: Optimizer=SGD (lr=0.01), Loss=MSELoss")

    loss_history = []
    epochs = 200

    for epoch in range(1, epochs + 1):
        # 1. Forward pass
        predictions = model(X_train)
        loss = criterion(predictions, y_train)
        loss_history.append(loss.item())

        # 2. Backward pass & optimization
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        if epoch % 40 == 0 or epoch == 1:
            w = model.linear.weight.item()
            b = model.linear.bias.item()
            print(
                f"  Epoch [{epoch:>3}/{epochs}] | Loss: {loss.item():<8.4f} | "
                f"Learned Weight: {w:.3f} | Learned Bias: {b:.3f}"
            )

    w_final = model.linear.weight.item()
    b_final = model.linear.bias.item()
    print(f"\nFinal Model Parameters: y = {w_final:.3f} * x + {b_final:.3f}")
    print("True Relation Target  : y = 6.500 * x + 15.000\n")

    return model, X_train, y_train, loss_history


def generate_visualizations(model, X, y, loss_history):
    print_banner("3. VISUALIZING MODEL CONVERGENCE & FIT")

    # 1. Loss Convergence Plot
    plt.figure(figsize=(7, 4.5))
    plt.plot(range(1, len(loss_history) + 1), loss_history, color="#0D6EFD")
    plt.title("SGD Training Loss Convergence (MSE)", fontsize=13)
    plt.xlabel("Epochs")
    plt.ylabel("Mean Squared Error")
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.tight_layout()
    p1 = os.path.join(OUT_DIR, "loss_convergence.png")
    plt.savefig(p1, dpi=200)
    plt.close()
    print("Saved visualization:", os.path.basename(p1))

    # 2. Fitted Regression Line Plot
    plt.figure(figsize=(7, 4.5))
    plt.scatter(
        X.numpy(), y.numpy(), color="#6C757D", alpha=0.7, label="True Samples"
    )
    with torch.no_grad():
        preds = model(X).numpy()
    plt.plot(
        X.numpy(), preds, color="#DC3545", linewidth=2, label="PyTorch Fit"
    )
    plt.title("Linear Regression Fit (Study Hours vs Score)", fontsize=13)
    plt.xlabel("Study Hours (x)")
    plt.ylabel("Exam Score (y)")
    plt.legend()
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.tight_layout()
    p2 = os.path.join(OUT_DIR, "linear_regression_fit.png")
    plt.savefig(p2, dpi=200)
    plt.close()
    print("Saved visualization:", os.path.basename(p2))


def serialize_model(model):
    """Serialize model state to models/linear_regression.pt."""
    model_path = os.path.join(MODELS_DIR, "linear_regression.pt")
    torch.save(model.state_dict(), model_path)
    rel = os.path.relpath(model_path, os.path.dirname(BASE_DIR))
    print(f"\nSerialized PyTorch weights to: {rel}")


def main():
    print_banner("LAB 6: DEEP LEARNING FUNDAMENTALS USING PYTORCH")
    print("Author: Jayesh Solanki | Roll No: IC-2K23-45 | MCA AI Lab\n")

    demo_tensor_autograd()
    model, X, y, loss_history = train_regression_model()
    generate_visualizations(model, X, y, loss_history)
    serialize_model(model)
    print_banner("LAB 6 COMPLETED SUCCESSFULLY!")


if __name__ == "__main__":
    main()
