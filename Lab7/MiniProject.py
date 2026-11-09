#!/usr/bin/env python3
"""Trained handwritten-digit mini-project with Grad-CAM, FGSM, PCA and SVD."""
import json
import os
import random
import time

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import torch
from sklearn.datasets import load_digits
from sklearn.decomposition import PCA
from sklearn.model_selection import train_test_split
from torch import nn
from torch.nn import functional as F
from torch.optim import Adam

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(HERE, "outputs")
MODELS = os.path.join(ROOT, "models")
os.makedirs(OUT, exist_ok=True)
os.makedirs(MODELS, exist_ok=True)


class DigitCNN(nn.Module):
    """Compact convolutional classifier with a Grad-CAM target layer."""
    def __init__(self):
        super().__init__()
        self.conv1 = nn.Conv2d(1, 16, 3, padding=1)
        self.conv2 = nn.Conv2d(16, 32, 3, padding=1)
        self.pool = nn.MaxPool2d(2)
        self.fc1 = nn.Linear(32 * 2 * 2, 64)
        self.fc2 = nn.Linear(64, 10)
        self.activations = None
        self.gradients = None

    def save_gradient(self, gradient):
        self.gradients = gradient

    def forward(self, x):
        x = self.pool(F.relu(self.conv1(x)))
        x = F.relu(self.conv2(x))
        self.activations = x
        if x.requires_grad:
            x.register_hook(self.save_gradient)
        x = self.pool(x).flatten(1)
        return self.fc2(F.relu(self.fc1(x)))


def main():
    random.seed(42)
    np.random.seed(42)
    torch.manual_seed(42)
    torch.set_num_threads(1)
    started = time.perf_counter()

    digits = load_digits()
    images = digits.images.astype(np.float32) / 16.0
    x_train_np, x_test_np, y_train_np, y_test_np = train_test_split(
        images, digits.target, test_size=0.20, random_state=42,
        stratify=digits.target
    )
    x_train = torch.tensor(x_train_np[:, None], dtype=torch.float32)
    y_train = torch.tensor(y_train_np, dtype=torch.long)
    x_test = torch.tensor(x_test_np[:, None], dtype=torch.float32)
    y_test = torch.tensor(y_test_np, dtype=torch.long)

    model = DigitCNN()
    optimizer = Adam(model.parameters(), lr=0.003)
    epochs = 45
    losses = []
    for epoch in range(epochs):
        model.train()
        batch_losses = []
        order = torch.randperm(len(x_train))
        for start in range(0, len(order), 64):
            ids = order[start:start + 64]
            logits = model(x_train[ids])
            loss = F.cross_entropy(logits, y_train[ids])
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            batch_losses.append(float(loss.item()))
        losses.append(float(np.mean(batch_losses)))

    model.eval()
    with torch.no_grad():
        clean_predictions = model(x_test).argmax(1)
    clean_accuracy = float((clean_predictions == y_test).float().mean().item())

    # Grad-CAM for one correctly classified held-out digit.
    correct = torch.where(clean_predictions == y_test)[0]
    sample_index = int(correct[0].item())
    sample = x_test[sample_index:sample_index + 1].clone().requires_grad_(True)
    model.zero_grad()
    target = int(y_test[sample_index].item())
    model(sample)[0, target].backward()
    channel_weights = model.gradients.mean(dim=(2, 3), keepdim=True)
    heat = F.relu((channel_weights * model.activations).sum(dim=1, keepdim=True))
    heat = F.interpolate(heat, size=(8, 8), mode="bilinear", align_corners=False)
    heat = (heat / heat.max().clamp_min(1e-8)).detach().squeeze().numpy()
    image = sample.detach().squeeze().numpy()

    fig, axes = plt.subplots(1, 3, figsize=(8, 3))
    axes[0].imshow(image, cmap="gray_r")
    axes[0].set_title(f"Input: {target}")
    axes[1].imshow(heat, cmap="inferno")
    axes[1].set_title("Grad-CAM")
    axes[2].imshow(image, cmap="gray_r")
    axes[2].imshow(heat, cmap="inferno", alpha=0.5)
    axes[2].set_title("Overlay")
    for axis in axes:
        axis.axis("off")
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "gradcam_visualization.svg"))
    plt.close(fig)

    # FGSM on the same held-out test partition.
    epsilons = [0.0, 0.05, 0.10, 0.15, 0.20, 0.25]
    robust_accuracy = []
    attack_inputs = x_test.clone().requires_grad_(True)
    model.zero_grad()
    F.cross_entropy(model(attack_inputs), y_test).backward()
    input_gradient = attack_inputs.grad.detach()
    for epsilon in epsilons:
        adversarial = torch.clamp(
            x_test + epsilon * input_gradient.sign(), min=0.0, max=1.0
        )
        with torch.no_grad():
            predicted = model(adversarial).argmax(1)
        robust_accuracy.append(float((predicted == y_test).float().mean().item()))

    fig, axis = plt.subplots(figsize=(6, 4))
    axis.plot(epsilons, np.array(robust_accuracy) * 100, marker="o")
    axis.set_xlabel("FGSM epsilon")
    axis.set_ylabel("Test accuracy (%)")
    axis.set_title("FGSM Robustness Evaluation")
    axis.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "fgsm_robustness_curve.svg"))
    plt.close(fig)

    # Compare PCA with an explicit SVD of the centered training feature matrix.
    matrix = x_train_np.reshape(len(x_train_np), -1).astype(np.float64)
    centered = matrix - matrix.mean(axis=0, keepdims=True)
    _, singular_values, right_vectors = np.linalg.svd(centered, full_matrices=False)
    svd_variance = singular_values ** 2 / np.sum(singular_values ** 2)
    pca = PCA(n_components=10, svd_solver="full").fit(matrix)
    pca_variance = pca.explained_variance_ratio_
    variance_difference = float(
        np.max(np.abs(svd_variance[:10] - pca_variance))
    )
    reconstruction = (centered @ right_vectors[:10].T) @ right_vectors[:10]
    reconstruction_error = float(
        np.linalg.norm(centered - reconstruction) / np.linalg.norm(centered)
    )

    fig, axis = plt.subplots(figsize=(6, 4))
    components = np.arange(1, 11)
    axis.bar(components - 0.18, pca_variance * 100, width=0.36, label="PCA")
    axis.bar(components + 0.18, svd_variance[:10] * 100, width=0.36, label="SVD")
    axis.set_xlabel("Component")
    axis.set_ylabel("Explained variance (%)")
    axis.set_title("PCA and SVD: Explained Variance")
    axis.legend()
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "pca_svd_comparison.svg"))
    plt.close(fig)

    fig, axis = plt.subplots(figsize=(6, 3.5))
    axis.plot(range(1, epochs + 1), losses)
    axis.set_xlabel("Epoch")
    axis.set_ylabel("Training cross-entropy")
    axis.set_title("Digit CNN Training Loss")
    axis.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "training_loss.svg"))
    plt.close(fig)

    results = {
        "dataset": "scikit-learn Digits",
        "samples": int(len(images)),
        "train_samples": int(len(x_train_np)),
        "test_samples": int(len(x_test_np)),
        "epochs": epochs,
        "clean_test_accuracy": clean_accuracy,
        "fgsm_epsilons": epsilons,
        "fgsm_test_accuracy": robust_accuracy,
        "pca_svd_max_variance_difference": variance_difference,
        "first_four_components_variance": float(np.sum(svd_variance[:4])),
        "ten_component_relative_reconstruction_error": reconstruction_error,
        "training_seconds": time.perf_counter() - started,
    }
    with open(os.path.join(OUT, "mini_project_results.json"), "w", encoding="utf-8") as file:
        json.dump(results, file, indent=2)
    torch.save(
        {"model_state_dict": model.state_dict(), "classes": list(range(10))},
        os.path.join(MODELS, "digit_resnet.pt")
    )

    lines = [
        "LAB 7: TRAINED DIGIT RECOGNITION MINI-PROJECT",
        f"Dataset: Scikit-learn Digits ({len(images)} labelled 8x8 images)",
        f"Split: {len(x_train_np)} train / {len(x_test_np)} test",
        f"Training epochs: {epochs}",
        f"Clean test accuracy: {clean_accuracy * 100:.2f}%",
        "FGSM test accuracy:",
    ]
    lines.extend(
        f"  epsilon={eps:.2f}: {acc * 100:.2f}%"
        for eps, acc in zip(epsilons, robust_accuracy)
    )
    lines.extend([
        f"PCA/SVD max variance-ratio difference: {variance_difference:.8f}",
        f"First four components retain: {np.sum(svd_variance[:4]) * 100:.2f}%",
        f"10-component reconstruction error: {reconstruction_error:.4f}",
        "Saved Grad-CAM, FGSM, PCA/SVD plots, JSON results and digit_resnet.pt",
    ])
    with open(os.path.join(OUT, "explainable_ai_output.txt"), "w", encoding="utf-8") as file:
        file.write("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
