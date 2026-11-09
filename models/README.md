# Serialized Models and Checkpoints Directory

This folder stores trained machine learning classifiers, neural network checkpoints, and serialized pipeline transformers produced during laboratory exercises.

### Expected Model Artifacts by Lab Session

| Lab Session | Model File | Framework / Format | Description |
|---|---|---|---|
| **Lab 5** | `decision_tree.pkl` | Scikit-learn / Joblib | Trained Decision Tree classifier for student placement or disease prediction. |
| **Lab 6** | `linear_regression.pt` | PyTorch (`.pt`) | PyTorch linear regression model checkpoint with learned weight and bias tensors. |
| **Lab 6** | `neural_network.pt` | PyTorch (`.pt`) | Multilayer perceptron weights for non-linear decision boundary classification. |
| **Lab 7** | `resnet_classifier.pt` | PyTorch / TorchVision | Pretrained ResNet model used for Grad-CAM visual interpretability and FGSM adversarial evaluation. |

*Note: Lab 1 focuses on discrete state-space formulation and symbolic rule engines; serialized statistical model weights are not generated in this laboratory session.*
