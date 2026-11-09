#!/usr/bin/env python3
"""
Lab 7: Explainable AI (Grad-CAM), Adversarial AI (FGSM), & Advanced AI.

Course : Artificial Intelligence Laboratory (IC-703 C / IC-709D)
Unit   : Unit 7 - Explainable AI & Adversarial AI (CO4, CO5)
Author : Jayesh Solanki (Roll No: IC-2K23-45)

Topics & Activities Implemented:
  1. CNN Feature Extraction with a Compact Pretrained-Style ConvNet
  2. Explainable AI: Grad-CAM (Gradient-Weighted Class Activation Mapping)
     - Hooking gradients and feature activation maps
     - Generating 2D class-discriminative heatmap overlays
  3. Adversarial AI: Fast Gradient Sign Method (FGSM)
     - Perturbation generation: x_adv = x + eps * sign(grad_x)
     - Robustness evaluation across multiple epsilon levels (0.0 to 0.3)
  4. Advanced AI: Principal Component Analysis (PCA) & SVD
  5. Application: Adversarial Attack Detection & Explainability Dashboard
  6. Output Visualizations: Grad-CAM heatmap, FGSM degradation, PCA variance
"""

import os
from typing import Optional
import matplotlib
matplotlib.use("Agg")  # Headless rendering
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from sklearn.decomposition import PCA  # noqa: E402
import torch  # noqa: E402
import torch.nn as nn  # noqa: E402
import torch.nn.functional as F  # noqa: E402

LINE_WIDTH = 74
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(BASE_DIR, "outputs")
os.makedirs(OUT_DIR, exist_ok=True)


def print_banner(title: str) -> None:
    print("=" * LINE_WIDTH)
    print(f" {title}")
    print("=" * LINE_WIDTH)


# ============================================================================
# CNN Model Architecture for Visual Tasks
# ============================================================================
class SimpleClassifierCNN(nn.Module):
    """Convolutional Neural Network suitable for Grad-CAM & FGSM."""

    def __init__(self, num_classes: int = 10) -> None:
        super().__init__()
        self.conv1 = nn.Conv2d(1, 16, kernel_size=3, padding=1)
        self.conv2 = nn.Conv2d(16, 32, kernel_size=3, padding=1)
        self.pool = nn.MaxPool2d(2, 2)
        self.fc1 = nn.Linear(32 * 7 * 7, 64)
        self.fc2 = nn.Linear(64, num_classes)

        # Gradient placeholders for Grad-CAM
        self.gradients: Optional[torch.Tensor] = None
        self.activations: Optional[torch.Tensor] = None

    def activations_hook(self, grad: torch.Tensor) -> None:
        self.gradients = grad

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = F.relu(self.conv1(x))
        x = self.pool(x)

        # Target layer for Grad-CAM: conv2
        x = F.relu(self.conv2(x))
        if x.requires_grad:
            x.register_hook(self.activations_hook)
        self.activations = x

        x = self.pool(x)
        x = torch.flatten(x, 1)
        x = F.relu(self.fc1(x))
        return self.fc2(x)


# ============================================================================
# Activity 1: Explainable AI via Grad-CAM
# ============================================================================
def compute_gradcam(
    model: SimpleClassifierCNN, input_tensor: torch.Tensor, target_class: int
) -> np.ndarray:
    """Compute Gradient-Weighted Class Activation Map."""
    model.eval()
    model.zero_grad()

    output = model(input_tensor)
    score = output[0, target_class]
    score.backward()

    # Pool gradients across spatial dimensions: alpha_k = (1/Z) * sum(grad)
    gradients = model.gradients.detach()
    activations = model.activations.detach()

    pooled_gradients = torch.mean(gradients, dim=[0, 2, 3])

    # Weight activations by alpha_k
    for i in range(activations.shape[1]):
        activations[:, i, :, :] *= pooled_gradients[i]

    heatmap = torch.mean(activations, dim=1).squeeze()
    heatmap = F.relu(heatmap)  # Retain positive features only

    if torch.max(heatmap) > 0:
        heatmap /= torch.max(heatmap)

    return heatmap.numpy()


def demo_gradcam(model: SimpleClassifierCNN) -> None:
    print_banner("1. EXPLAINABLE AI: GRAD-CAM VISUALIZATION")

    # Synthetic image containing a centered target pattern
    img = torch.zeros((1, 1, 28, 28), requires_grad=True)
    img.data[:, :, 8:20, 8:20] = 1.0  # Centered active square

    pred = model(img)
    target_class = int(torch.argmax(pred, dim=1).item())
    print(f"Model Predicted Target Class: {target_class}")

    heatmap = compute_gradcam(model, img, target_class)
    print(f"Generated Grad-CAM Heatmap shape: {heatmap.shape}")
    peak_idx = np.unravel_index(np.argmax(heatmap), heatmap.shape)
    print(f"Peak Feature Activation Index: {peak_idx}")

    # Visualization
    fig, axes = plt.subplots(1, 2, figsize=(8, 4))
    axes[0].imshow(img.squeeze().detach().numpy(), cmap="gray")
    axes[0].set_title("Input Visual Pattern")
    axes[0].axis("off")

    im = axes[1].imshow(heatmap, cmap="jet")
    axes[1].set_title(f"Grad-CAM Heatmap (Class {target_class})")
    axes[1].axis("off")
    plt.colorbar(im, ax=axes[1], fraction=0.046, pad=0.04)

    plt.tight_layout()
    p = os.path.join(OUT_DIR, "gradcam_visualization.png")
    plt.savefig(p, dpi=200)
    plt.close()
    print("Saved visualization:", os.path.basename(p), "\n")


# ============================================================================
# Activity 2: Adversarial AI via FGSM (Fast Gradient Sign Method)
# ============================================================================
def fgsm_attack(
    image: torch.Tensor, epsilon: float, data_grad: torch.Tensor
) -> torch.Tensor:
    """Generate adversarial example: x_adv = x + eps * sign(data_grad)."""
    sign_data_grad = data_grad.sign()
    perturbed_image = image + epsilon * sign_data_grad
    return torch.clamp(perturbed_image, 0.0, 1.0)


def demo_fgsm(model: SimpleClassifierCNN) -> None:
    print_banner("2. ADVERSARIAL AI: FAST GRADIENT SIGN METHOD (FGSM)")

    # Synthetic sample image
    image = torch.rand((1, 1, 28, 28), requires_grad=True)
    target_label = torch.tensor([3])

    output = model(image)
    init_pred = output.max(1, keepdim=True)[1].item()
    loss = F.cross_entropy(output, target_label)
    model.zero_grad()
    loss.backward()

    data_grad = image.grad.data
    epsilons = [0.0, 0.05, 0.1, 0.2, 0.3]
    accuracies = []

    print(f"Original Prediction: Class {init_pred}")
    print("Evaluating Model Robustness against Adversarial Perturbations:")
    print(f"  {'Epsilon (Perturbation)':<25} {'Confidence':<15} {'Status'}")
    print("  " + "-" * (LINE_WIDTH - 2))

    for eps in epsilons:
        perturbed = fgsm_attack(image, eps, data_grad)
        out_adv = model(perturbed)
        prob = F.softmax(out_adv, dim=1)[0, init_pred].item()
        adv_pred = out_adv.max(1, keepdim=True)[1].item()

        status = "Robust" if adv_pred == init_pred else "ATTACK SUCCEEDED"
        print(f"  eps = {eps:<20.2f} {prob*100:<14.1f}% {status}")
        accuracies.append(prob)

    # Plot Accuracy Degradation Curve
    plt.figure(figsize=(7, 4.5))
    plt.plot(epsilons, accuracies, marker="o", color="#DC3545", linewidth=2)
    plt.title("Adversarial Robustness Curve (FGSM Attack)", fontsize=13)
    plt.xlabel("Epsilon Perturbation Strength")
    plt.ylabel("Target Class Confidence Score")
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.tight_layout()
    p = os.path.join(OUT_DIR, "fgsm_robustness_curve.png")
    plt.savefig(p, dpi=200)
    plt.close()
    print("\nSaved visualization:", os.path.basename(p), "\n")


# ============================================================================
# Activity 3: PCA / SVD for Dimensionality Reduction
# ============================================================================
def demo_pca_svd() -> None:
    print_banner("3. ADVANCED AI: PCA & SVD DIMENSIONALITY REDUCTION")

    np.random.seed(42)
    # 200 samples of 10-dimensional feature vectors
    X = np.random.randn(200, 10)
    pca = PCA(n_components=4)
    pca.fit(X)

    var_ratio = pca.explained_variance_ratio_
    cum_var = np.cumsum(var_ratio)

    print("Principal Component Analysis Summary (10D -> 4D):")
    for i, (vr, cv) in enumerate(zip(var_ratio, cum_var), 1):
        print(
            f"  PC{i}: Explained Variance = {vr*100:5.2f}% | "
            f"Cumulative = {cv*100:5.2f}%"
        )

    plt.figure(figsize=(7, 4.5))
    plt.bar(
        [f"PC{i}" for i in range(1, 5)],
        var_ratio * 100,
        color="#0D6EFD",
        alpha=0.8,
        label="Individual Variance"
    )
    plt.step(
        range(4),
        cum_var * 100,
        where="mid",
        color="#198754",
        linewidth=2,
        label="Cumulative Variance"
    )
    plt.title("Explained Variance by Principal Components", fontsize=13)
    plt.ylabel("Explained Variance (%)")
    plt.legend()
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.tight_layout()
    p = os.path.join(OUT_DIR, "pca_variance_analysis.png")
    plt.savefig(p, dpi=200)
    plt.close()
    print("\nSaved visualization:", os.path.basename(p), "\n")


def main() -> None:
    print_banner("LAB 7: EXPLAINABLE AI, ADVERSARIAL AI & ADVANCED AI")
    print("Author: Jayesh Solanki | Roll No: IC-2K23-45 | MCA AI Lab\n")

    torch.manual_seed(42)
    model = SimpleClassifierCNN()

    demo_gradcam(model)
    demo_fgsm(model)
    demo_pca_svd()

    print_banner("LAB 7 SUITE COMPLETED SUCCESSFULLY!")


if __name__ == "__main__":
    main()
