# Mini-Project Report: Explainable and Robust Handwritten Digit Recognition

**Course:** MCA Artificial Intelligence Laboratory (IC-703 C / IC-709D)  
**Unit:** Unit 7 – Explainable AI, Adversarial AI and Advanced Applications  
**Student:** Jayesh Solanki (IC-2K23-45)

## 1. Problem

Train a compact image classifier for handwritten digits, explain a held-out prediction with Grad-CAM, evaluate its sensitivity to FGSM perturbations and compare PCA with an explicit SVD decomposition.

## 2. Dataset and model

The Scikit-learn Digits dataset contains 1,797 labelled 8 × 8 grayscale images in ten classes. A stratified split creates 1,437 training and 360 test samples. A two-convolution CNN is trained for 45 epochs with mini-batches, Adam and cross-entropy loss.

## 3. Results

| Measure | Result |
|---|---:|
| Clean test accuracy | 98.06% |
| FGSM accuracy, ε = 0.05 | 90.28% |
| FGSM accuracy, ε = 0.10 | 56.11% |
| FGSM accuracy, ε = 0.15 | 19.44% |
| FGSM accuracy, ε = 0.20 | 8.89% |
| FGSM accuracy, ε = 0.25 | 3.06% |
| First four SVD components variance | 48.94% |
| PCA/SVD variance-ratio difference, first 10 | approximately 0 |
| Ten-component relative reconstruction error | 0.5111 |

## 4. Explainability and robustness

Grad-CAM is calculated from the gradients and activations of the final convolutional feature map for a correctly classified held-out image. The heatmap highlights spatial regions contributing to that prediction. It explains one model decision and should not be interpreted as causal proof.

FGSM is evaluated on the same 360 test images at six epsilon values. Accuracy falls as perturbation strength increases, demonstrating sensitivity to this specific white-box attack. It does not characterize all adversarial threats.

## 5. PCA and SVD

The centered training-image matrix is decomposed using NumPy SVD. Squared singular values provide variance ratios, which are compared with Scikit-learn PCA. The two implementations agree to floating-point precision for the first ten components. The first four components retain 48.94% of the variance.

## 6. Limitations

The dataset contains small grayscale images, so results may not transfer to larger real-world image tasks. Only a compact model, one test split and the FGSM attack family are considered.

## 7. Conclusion

This mini-project integrates supervised CNN training, a gradient-based explanation, adversarial robustness evaluation and dimensionality reduction. The scripts, notebook, metrics and generated figures are included in Lab 7.
