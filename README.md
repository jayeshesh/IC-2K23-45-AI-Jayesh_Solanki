# Artificial Intelligence Laboratory (IC-703 C / IC-709D)

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Code style: PEP 8](https://img.shields.io/badge/code%20style-PEP%208-brightgreen.svg)](https://www.python.org/dev/peps/pep-0008/)
[![Academic: IIPS DAVV](https://img.shields.io/badge/academic-IIPS%20DAVV-orange.svg)](https://www.iips.edu.in/)

This repository contains practical implementations, state-space formulations, search algorithms, empirical benchmarks, and academic documentation for the **Artificial Intelligence Laboratory** course (**IC-703 C / IC-709D**), Master of Computer Applications (MCA), at the **International Institute of Professional Studies (IIPS), Devi Ahilya Vishwavidyalaya (DAVV), Indore**.

The primary objective is to gain rigorous, foundational experience in representing real-world problems mathematically and symbolically, designing search and reasoning algorithms, implementing declarative production rule systems, and engineering intelligent decision-making agents.

---

## Laboratory Roadmap & Syllabus Mapping

Following the official **DAVV MCA AI Lab Syllabus (IC-703 C / IC-709D)**, the laboratory exercises are structured across the semester units:

| Lab Session | Unit & Course Outcome | Experiment Scope & Core Themes | Status |
|---|---|---|:---:|
| [**Lab 1**](Lab1/README.md) | **Unit 1: CO1** | **AI Environment Setup, Production Systems, Water Jug Problem** | Completed |
| [**Lab 2**](Lab2/README.md) | **Unit 2: CO2** | **Heuristic Search Algorithms (BFS, DFS, Hill Climbing, Best First, A*)** | Completed |
| [**Lab 3**](Lab3/README.md) | **Unit 3: CO2, CO5** | **AI Programming Frameworks & Data Preparation (NumPy, Pandas, EDA, Pipelines)** | Completed |
| [**Lab 4**](Lab4/README.md) | **Unit 4: CO1, CO3** | **Knowledge Representation & Logical Reasoning (Predicates, Rule-Based Systems, Semantic Networks)** | Completed |
| [**Lab 5**](Lab5/README.md) | **Unit 5: CO4, CO5** | **Decision Tree Classifier and Model Evaluation** | Completed |
| [**Lab 6**](Lab6/README.md) | **Unit 6: CO4, CO5** | **Deep Learning Fundamentals using PyTorch (Tensors, Autograd, Linear Regression)** | Completed |
| [**Lab 7**](Lab7/README.md) | **Unit 7: CO4, CO5** | **Explainable AI (Grad-CAM), Adversarial AI (FGSM), PCA/SVD Dimensionality Reduction** | Completed |

---

## Lab 1 — AI Environment Setup, Production Systems, Water Jug Problem

Lab 1 establishes the mathematical, architectural, and operational foundations of symbolic AI problem solving:

- **Experiment 1 (Environment Setup):** Configuration, verification, and automated diagnostic profiling of Python 3, pip, Jupyter Notebook, Colab detection, and core state-space primitives (`tuple`, `set`, `deque`).
- **Experiment 2 (Production System):** Generic, forward-chaining production rule engine executing the Recognize-Act cycle with a 4-tier conflict resolution strategy on the **Smart Irrigation Advisor** domain.
- **Experiment 3 (Water Jug Problem):** State-space formulation ⟨S, s₀, O, G⟩ of the classical water jug problem, analytical solvability proof via Bézout's identity ($T \equiv 0 \pmod{\gcd(A, B)}$), and optimal, minimum-step solution discovery using Breadth-First Search (BFS).
- **Unit 1 Analysis Part:** Comprehensive comparative analysis of Classical vs. AI Programming and state-space evaluation of standard AI problems (Water Jug, Vacuum Cleaner, Missionaries & Cannibals, 8-Puzzle).

For complete code, algorithms, flowcharts, benchmarks, and execution outputs:  
👉 **[View Detailed Lab 1 Documentation & Code](Lab1/README.md)**

---

## Lab 2 — Heuristic Search Algorithms

Lab 2 covers uninformed, informed and local search methods:
- Breadth-First Search (BFS) and Depth-First Search (DFS).
- Greedy Best-First Search and A*.
- Hill Climbing for function maximization.
- 8-puzzle solving, graph traversal, maze navigation and route planning.

See [Lab2/README.md](Lab2/README.md) for the theory, activities, performance comparison and execution commands.

---

## Lab 3 — AI Programming Frameworks & Data Preparation

Lab 3 uses the Campus Placement dataset to practise:
- NumPy and Pandas-based data loading and inspection.
- Exploratory Data Analysis (EDA) and summary statistics.
- Missing-value handling and categorical encoding.
- Leak-free train/test splitting, feature selection and scaling.
- Matplotlib and Seaborn visualizations.

The shared dataset is stored at [datasets/placement.csv](datasets/placement.csv). See [Lab3/README.md](Lab3/README.md) for the full pipeline, outputs and learning outcomes.


---

## Lab 4 — Knowledge Representation & Logical Reasoning

Lab 4 demonstrates symbolic ways to represent knowledge and derive new facts:
- Predicate facts and a university knowledge base.
- Forward-chaining production rules and a logical inference engine.
- Semantic network construction, frame representation and conceptual dependency.
- A small medical knowledge representation example using illustrative rules.

See [Lab4/README.md](Lab4/README.md) for the algorithm, comparison of representation methods, diagram and execution output.

---

## Lab 5 — Decision Tree Classifier and Model Evaluation

Lab 5 uses the shared Campus Placement dataset to train a Decision Tree Classifier. It covers feature-matrix creation, stratified train/test splitting, numeric and categorical preprocessing, prediction, accuracy, precision, recall, F1-score, a confusion matrix and decision-tree visualization. Salary and the student serial number are excluded from predictors to prevent leakage.

See [Lab5/README.md](Lab5/README.md) for the complete experiment. The checked-in sample output is a 40-row development smoke test; the script uses the full shared 215-row dataset when run from the repository root.

---

## Lab 6 — Deep Learning Fundamentals using PyTorch

Lab 6 implements foundational deep learning mechanics in PyTorch:
- Multi-dimensional Tensor manipulation and tensor arithmetic.
- Dynamic computational graph tracking and reverse-mode automatic differentiation (`autograd`).
- Custom `torch.nn.Module` linear regression model trained via MSE loss and Adam optimizer.
- Training loss convergence monitoring and parameter convergence inspection.
- Model persistence saving state dictionary to `models/linear_regression.pt`.

See [Lab6/README.md](Lab6/README.md) for mathematical derivations, loss curves, and execution commands.

---

## Lab 7 — Explainable AI, Adversarial AI & Advanced Dimensionality Reduction

Lab 7 explores modern neural interpretability, security, and representation learning:
- **Explainable AI (Grad-CAM):** Gradient-weighted Class Activation Mapping to extract saliency heatmaps highlighting discriminative spatial regions in convolutional feature maps.
- **Adversarial Machine Learning (FGSM):** Fast Gradient Sign Method crafting bounded adversarial perturbations ($\epsilon \in [0.0, 0.30]$) to evaluate neural robustness and decision boundary vulnerability.
- **Representation Learning (PCA & SVD):** High-dimensional projection via Singular Value Decomposition, evaluating eigenvalue scree plots and cumulative variance retention curves.

See [Lab7/README.md](Lab7/README.md) for theoretical background, mathematical equations, visualization figures, and experimental results.

---

## Lab 6 — Deep Learning Fundamentals using PyTorch

Lab 6 covers tensor operations, analytical gradient verification with autograd, PyTorch linear regression and a multi-layer feed-forward network for student score prediction. The neural-network experiment uses separate training, validation and test partitions, reports MAE/RMSE and saves its checkpoint in `models/`.

See [Lab6/README.md](Lab6/README.md) for the implementation, results and visualizations.

---

## Lab 7 — Explainable AI, Adversarial AI, PCA/SVD and Mini-Project

Lab 7 trains a compact residual CNN on the Scikit-learn handwritten Digits dataset, explains a prediction with Grad-CAM, evaluates FGSM robustness, and compares PCA with explicit SVD. The mini-project combines these outputs in an explainability and robustness dashboard.

See [Lab7/README.md](Lab7/README.md) and the [mini-project report](docs/mini-project-report.pdf).

---

## Repository Structure

Each lab has its own source code, notebook, README and output artifacts. Shared datasets and diagrams stay at the repository level.

```text
IC-2K23-45-AI-Jayesh_Solanki/
│
├── Lab1/
│   ├── Experiment1.py
│   ├── exp2_production_system.py
│   ├── Experiment2.py
│   ├── Experiment1.ipynb
│   ├── README.md
│   └── outputs/
│       ├── execution logs
│       └── screenshots/
│
├── Lab2/
│   ├── SearchAlgorithms.py
│   ├── SearchAlgorithms.ipynb
│   ├── README.md
│   └── outputs/
│       ├── execution logs
│       └── screenshots/
│
├── Lab3/
│   ├── DataPreprocessing.py
│   ├── DataPreprocessing.ipynb
│   ├── README.md
│   └── outputs/
│       ├── execution logs
│       └── screenshots and plots
│
├── Lab4/
│   ├── KnowledgeRepresentation.py
│   ├── KnowledgeRepresentation.ipynb
│   ├── README.md
│   └── outputs/
│       ├── knowledge_representation_output.txt
│       └── semantic_network.svg
│
├── Lab5/
│   ├── DecisionTree.py
│   ├── DecisionTree.ipynb
│   ├── README.md
│   └── outputs/
│       ├── decision_tree_output.txt
│       └── confusion matrix and tree diagrams
│
├── Lab6/
│   ├── PytorchBasics.py
│   ├── PytorchBasics.ipynb
│   ├── README.md
│   └── outputs/
│       ├── pytorch_basics_output.txt
│       └── SVG training visualizations
│
├── Lab7/
│   ├── ExplainableAI.py
│   ├── ExplainableAI.ipynb
│   ├── README.md
│   └── outputs/
│       ├── explainable_ai_output.txt
│       ├── mini_project_results.json
│       └── SVG dashboard and diagnostics
│
├── datasets/
│   ├── README.md
│   └── placement.csv
├── models/
│   ├── README.md
│   ├── linear_regression.pt
│   ├── student_score_network.pt
│   └── digit_resnet.pt
├── docs/
│   ├── README.md
│   ├── algorithm-flowcharts/
│   ├── architecture-diagrams/
│   ├── performance-analysis.pdf
│   ├── mini-project-report.md
│   └── mini-project-report.pdf
├── requirements.txt
├── .gitignore
└── README.md
```

---

## Setup and Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/jayeshesh/IC-2K23-45-AI-Jayesh_Solanki.git
cd IC-2K23-45-AI-Jayesh_Solanki
```

### 2. Create a Virtual Environment and Install Packages

```bash
python -m venv .venv

# Windows
.venv\\Scripts\\activate

# Linux / macOS
source .venv/bin/activate

pip install -r requirements.txt
```

### 3. Run Lab 1

```bash
python Lab1/Experiment1.py
python Lab1/exp2_production_system.py
python Lab1/Experiment2.py --trace
```

### 4. Run Lab 2

```bash
python Lab2/SearchAlgorithms.py
python Lab2/SearchAlgorithms.py --activity 8puzzle
python Lab2/SearchAlgorithms.py --activity graph
python Lab2/SearchAlgorithms.py --activity maze
python Lab2/SearchAlgorithms.py --activity route
python Lab2/SearchAlgorithms.py --activity hill
```

### 5. Run Lab 3

```bash
python Lab3/DataPreprocessing.py
```

The Lab 3 script reads `datasets/placement.csv` and saves its logs and visualizations in `Lab3/outputs/`.

### 6. Run Lab 4

```bash
python Lab4/KnowledgeRepresentation.py
```

Run a single knowledge-base example with `--example university` or `--example medical`.

### 7. Run Lab 5

```bash
python Lab5/DecisionTree.py
```

### 8. Run Lab 6

```bash
python Lab6/PytorchBasics.py
```

### 9. Run Lab 7 and the mini-project

```bash
python Lab7/ExplainableAI.py
```

---

## Software Quality and Academic Integrity Standards

- Each laboratory session keeps its source code, notebook, README and output artifacts together.
- Shared data files are stored in `datasets/` so they can be reused across labs.
- The Campus Placement dataset included for Lab 3 is stored once in the shared dataset folder.
- Screenshots and execution logs are kept with the corresponding laboratory outputs.
- Python package dependencies are listed in `requirements.txt`.

---

## Academic References

1. Russell, S., & Norvig, P. (2020). *Artificial Intelligence: A Modern Approach* (4th ed.). Pearson Education.
2. Rich, E., Knight, K., & Nair, S. B. (2017). *Artificial Intelligence* (3rd ed.). McGraw-Hill Education.
3. Nilsson, N. J. (2014). *Principles of Artificial Intelligence*. Morgan Kaufmann Publishers.
4. Forgy, C. L. (1982). *Rete: A Fast Algorithm for the Many Pattern/Many Object Pattern Match Problem*. Artificial Intelligence, 19(1), 17–37.
5. Devi Ahilya Vishwavidyalaya (DAVV). *Master of Computer Applications (MCA) Artificial Intelligence Lab Syllabus (IC-703 C / IC-709D)*.
