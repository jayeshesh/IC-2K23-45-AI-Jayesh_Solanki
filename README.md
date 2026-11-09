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
| **Lab 3** | Unit 3: CO2, CO5 | AI Programming Frameworks & Data Preparation (NumPy, Pandas, EDA, Pipelines) | Scheduled |
| **Lab 4** | Unit 4: CO1, CO3 | Knowledge Representation & Logical Reasoning (Predicates, Frames, Semantics) | Scheduled |
| **Lab 5** | Unit 5: CO4, CO5 | Machine Learning for Intelligent Decision Making (Decision Trees, Model Eval) | Scheduled |
| **Lab 6** | Unit 6: CO4, CO5 | Deep Learning Fundamentals using PyTorch (Tensors, Autograd, Regressors, NNs) | Scheduled |
| **Lab 7** | Unit 7: CO4, CO5 | Explainable AI (Grad-CAM), Adversarial AI (FGSM), PCA/SVD & Mini-Project | Scheduled |

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

## Repository Structure

The repository strictly follows the official folder hierarchy mandated by the course guidelines:

```text
IC-2K23-45-AI-Jayesh_Solanki/
│
├── Lab1/                                    # Lab 1 Session
│   ├── Code/                                # Executable source code
│   │   ├── Experiment1.py       # Diagnostic environment verification script
│   │   ├── exp2_production_system.py       # Production system engine (Smart Irrigation)
│   │   ├── Experiment2.py               # Water Jug state space & BFS production system
│   │   ├── Experiment1.ipynb # Executed interactive Jupyter notebook
│   │   └── run_all.py                      # Automated execution & log capture script
│   ├── Documentation/                       # Academic documentation package
│   │   ├── Lab1_Academic_Report.pdf        # Complete 16-page official academic PDF report
│   │   ├── figures/                        # Flowcharts, state-space tree & architecture diagrams
│   │   │   ├── architecture_production_system.png
│   │   │   ├── flowchart_exp1_environment_setup.png
│   │   │   ├── flowchart_exp2_production_system.png
│   │   │   ├── flowchart_exp3_water_jug.png
│   │   │   └── state_space_tree_water_jug.png
│   │   └── scripts/                        # Diagram & PDF build automation scripts
│   │       ├── generate_figures.py
│   │       └── build_lab1_report.py
│   ├── outputs/                             # Verified execution outputs & logs
│   │   ├── exp1_environment_setup_output.txt
│   │   ├── exp1_invalid_input_output.txt
│   │   ├── exp2_production_system_output.txt
│   │   ├── exp2_custom_input_output.txt
│   │   ├── exp2_invalid_input_output.txt
│   │   ├── exp3_water_jug_output.txt
│   │   ├── exp3_water_jug_any_jug_output.txt
│   │   ├── exp3_water_jug_unsolvable_and_invalid_output.txt
│   │   ├── exp3_water_jug_benchmark_output.txt
│   │   └── screenshots/                    # Real terminal capture images
│   └── README.md                            # Comprehensive Lab 1 overview & analysis
│
├── datasets/                                # Shared datasets across experiments (Placement, Iris, etc.)
│   └── README.md
│
├── models/                                  # Serialized models, weights, and checkpoints
│   └── README.md
│
├── docs/                                    # Global repository documentation & artifacts
│   ├── algorithm-flowcharts/                # Central repository for algorithm flowcharts
│   │   ├── lab1_flowchart_exp1_environment_setup.png
│   │   ├── lab1_flowchart_exp2_production_system.png
│   │   └── lab1_flowchart_exp3_water_jug.png
│   ├── architecture-diagrams/               # Central repository for architecture diagrams
│   │   ├── lab1_architecture_production_system.png
│   │   └── lab1_state_space_tree_water_jug.png
│   ├── performance-analysis.pdf             # (Maintained across lab milestones)
│   └── mini-project-report.pdf              # (Scheduled for Lab 7)
│
├── requirements.txt                         # Python dependencies
├── .gitignore                               # Standard Python gitignore rules
└── README.md                                # Root repository overview
```

---

## Setup and Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/JayeshSolanki/IC-2K23-45-AI-Jayesh_Solanki.git
cd IC-2K23-45-AI-Jayesh_Solanki
```

### 2. Environment Configuration
The core Lab 1 experiments rely **exclusively on the Python 3 standard library**. To run notebooks, generate diagrams, or compile PDFs, install the supporting packages:
```bash
# Create and activate a virtual environment
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

# Install optional dependencies
pip install -r requirements.txt
```

### 3. Running Lab 1 Experiments
```bash
# Execute all Lab 1 experiments and capture console logs
cd Lab1/Code
python run_all.py

# Run individual experiments directly:
python Experiment1.py
python exp2_production_system.py
python Experiment2.py --trace
```

---

## Software Quality and Academic Integrity Standards

- **PEP-8 Compliance:** All Python source files strictly comply with PEP-8 formatting (`pycodestyle --max-line-length=79` returns 0 warnings).
- **Static Analysis:** Verified using `pyflakes` with zero unused imports or variable leaks.
- **Empirical Authenticity:** Zero synthetic or fabricated outputs. All logs, benchmark tables, and screenshots are captured directly from actual execution runs on Python 3.13.13.
- **Mathematical Rigor:** Formal state-space formulations include explicit initial states, goal predicates, complete operator tables, and analytical solvability proofs.

---

## Academic References

1. Russell, S., & Norvig, P. (2020). *Artificial Intelligence: A Modern Approach* (4th ed.). Pearson Education.
2. Rich, E., Knight, K., & Nair, S. B. (2017). *Artificial Intelligence* (3rd ed.). McGraw-Hill Education.
3. Nilsson, N. J. (2014). *Principles of Artificial Intelligence*. Morgan Kaufmann Publishers.
4. Forgy, C. L. (1982). *Rete: A Fast Algorithm for the Many Pattern/Many Object Pattern Match Problem*. Artificial Intelligence, 19(1), 17–37.
5. Devi Ahilya Vishwavidyalaya (DAVV). *Master of Computer Applications (MCA) Artificial Intelligence Lab Syllabus (IC-703 C / IC-709D)*.
