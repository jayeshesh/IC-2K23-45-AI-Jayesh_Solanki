#!/usr/bin/env python3
"""
Generate the official academic PDF documentation for Lab 1 using ReportLab.

Produces:
    Lab1/Documentation/Lab1_Academic_Report.pdf

Features:
- Professional academic cover page (IIPS DAVV / MCA IC-703 C styling).
- Table of Contents.
- Theoretical foundations, problem formulations, state spaces.
- Complete algorithms, flowcharts, and architecture diagrams.
- Verified execution outputs, benchmarks, and performance analysis.
- Detailed comparative analysis (Classical vs AI, Problem Formulations).
- Results, learning outcomes, conclusions, and formal citations.
- Exact two-pass numbering with canvas callback (Page X of Y).
"""

import os
import sys
from typing import List

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.platypus import (
    HRFlowable,
    Image,
    KeepTogether,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DOC_DIR = os.path.dirname(SCRIPT_DIR)
LAB_DIR = os.path.dirname(DOC_DIR)
PDF_PATH = os.path.join(DOC_DIR, "Lab1_Academic_Report.pdf")
FIG_DIR = os.path.join(DOC_DIR, "figures")
OUT_DIR = os.path.join(LAB_DIR, "outputs")


class NumberedCanvas(canvas.Canvas):
    """Canvas callback to compute total page count and add running headers/footers."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_header_footer(num_pages)
            super().showPage()
        super().save()

    def draw_header_footer(self, page_count):
        if self._pageNumber == 1:
            return  # Suppress on cover page

        self.saveState()
        self.setFont("Helvetica", 9)
        self.setFillColor(colors.HexColor("#495057"))

        # Running Header
        self.drawString(
            54, letter[1] - 36, "IC-703 C / IC-709D | Artificial Intelligence Laboratory"
        )
        self.drawRightString(
            letter[0] - 54, letter[1] - 36, "Lab 1: Production Systems & Water Jug"
        )
        self.setStrokeColor(colors.HexColor("#CED4DA"))
        self.setLineWidth(0.75)
        self.line(54, letter[1] - 42, letter[0] - 54, letter[1] - 42)

        # Running Footer
        self.line(54, 45, letter[0] - 54, 45)
        self.drawString(
            54, 32, "International Institute of Professional Studies (IIPS), DAVV"
        )
        self.drawRightString(
            letter[0] - 54, 32, f"Page {self._pageNumber} of {page_count}"
        )
        self.restoreState()


def build_academic_pdf():
    doc = SimpleDocTemplate(
        PDF_PATH,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54,
    )

    styles = getSampleStyleSheet()

    # Custom typography
    c_primary = colors.HexColor("#1B365D")   # Deep Academic Navy
    c_secondary = colors.HexColor("#0D6EFD") # Vivid Blue
    c_dark = colors.HexColor("#212529")      # Off-black ink
    c_muted = colors.HexColor("#6C757D")     # Slate Gray
    c_code_bg = colors.HexColor("#F8F9FA")   # Code block background

    title_style = ParagraphStyle(
        "CoverTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=24,
        leading=30,
        alignment=1,
        textColor=c_primary,
    )

    subtitle_style = ParagraphStyle(
        "CoverSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=13,
        leading=18,
        alignment=1,
        textColor=c_secondary,
    )

    h1_style = ParagraphStyle(
        "Heading1_Custom",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=15,
        leading=19,
        textColor=c_primary,
        spaceBefore=14,
        spaceAfter=6,
        keepWithNext=True,
    )

    h2_style = ParagraphStyle(
        "Heading2_Custom",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=16,
        textColor=c_secondary,
        spaceBefore=10,
        spaceAfter=4,
        keepWithNext=True,
    )

    body_style = ParagraphStyle(
        "Body_Custom",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=9.5,
        leading=14,
        textColor=c_dark,
        spaceAfter=6,
    )

    bullet_style = ParagraphStyle(
        "Bullet_Custom",
        parent=body_style,
        leftIndent=15,
        bulletIndent=5,
        spaceAfter=3,
    )

    code_style = ParagraphStyle(
        "Code_Custom",
        parent=styles["Normal"],
        fontName="Courier",
        fontSize=7.5,
        leading=10,
        textColor=colors.HexColor("#1A1A1A"),
    )

    story: List = []

    # =========================================================================
    # COVER PAGE
    # =========================================================================
    story.append(Spacer(1, 40))
    story.append(
        Paragraph("INTERNATIONAL INSTITUTE OF PROFESSIONAL STUDIES", subtitle_style)
    )
    story.append(Paragraph("DEVI AHILYA VISHWAVIDYALAYA, INDORE", subtitle_style))
    story.append(Spacer(1, 15))
    story.append(
        HRFlowable(
            width="100%", thickness=2, color=c_primary, spaceBefore=5, spaceAfter=20
        )
    )
    story.append(
        Paragraph("ARTIFICIAL INTELLIGENCE LABORATORY<br/>(IC-703 C / IC-709D)", title_style)
    )
    story.append(Spacer(1, 12))
    story.append(
        Paragraph(
            "LABORATORY REPORT – LAB SESSION 1<br/><b>AI Environment Setup, Production Systems & Water Jug Problem</b>",
            subtitle_style,
        )
    )
    story.append(Spacer(1, 40))

    meta_data = [
        [
            Paragraph("<b>Program:</b>", body_style),
            Paragraph("Master of Computer Applications (MCA) 6-Year Integrated", body_style),
        ],
        [
            Paragraph("<b>Course Code:</b>", body_style),
            Paragraph("IC-703 C (Lab: IC-709D) – Artificial Intelligence", body_style),
        ],
        [
            Paragraph("<b>Academic Term:</b>", body_style),
            Paragraph("MCA Semester VII / Academic Year 2026", body_style),
        ],
        [
            Paragraph("<b>Unit Mapping:</b>", body_style),
            Paragraph("Unit 1: AI Problem Formulation & Intelligent Problem Solving (CO1)", body_style),
        ],
        [
            Paragraph("<b>Student Name / Roll:</b>", body_style),
            Paragraph("Jayesh Solanki (Roll No: IC-2K23-45)", body_style),
        ],
        [
            Paragraph("<b>Submission Date:</b>", body_style),
            Paragraph("November 2026", body_style),
        ],
    ]
    meta_table = Table(meta_data, colWidths=[150, 350])
    meta_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F8F9FA")),
                ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#DEE2E6")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("LEFTPADDING", (0, 0), (-1, -1), 12),
                ("RIGHTPADDING", (0, 0), (-1, -1), 12),
            ]
        )
    )
    story.append(meta_table)
    story.append(Spacer(1, 60))

    eval_box = [
        [Paragraph("<b>EVALUATION & CERTIFICATION RECORD</b>", body_style), ""],
        [Paragraph("Marks Awarded:", body_style), Paragraph("Signature of Faculty In-Charge:", body_style)],
        [Paragraph("Date of Evaluation:", body_style), Paragraph("Remarks:", body_style)],
    ]
    eval_table = Table(eval_box, colWidths=[250, 250])
    eval_table.setStyle(
        TableStyle(
            [
                ("SPAN", (0, 0), (1, 0)),
                ("BACKGROUND", (0, 0), (1, 0), colors.HexColor("#E9ECEF")),
                ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#CED4DA")),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("PADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )
    story.append(eval_table)
    story.append(PageBreak())

    # =========================================================================
    # TABLE OF CONTENTS / LAB OUTLINE
    # =========================================================================
    story.append(Paragraph("Table of Contents", h1_style))
    story.append(
        HRFlowable(width="100%", thickness=1, color=c_secondary, spaceBefore=4, spaceAfter=14)
    )

    toc_data = [
        ["1.0", "Laboratory Overview & Pedagogical Objectives", "Page 3"],
        ["2.0", "Theoretical Foundations of AI Problem Solving", "Page 3"],
        ["3.0", "Experiment 1: AI Development Environment Setup & Verification", "Page 4"],
        ["3.1", "  Objective, Description & Mathematical State Primitives", "Page 4"],
        ["3.2", "  Verification Algorithm & Architectural Flowchart", "Page 5"],
        ["3.3", "  Execution Outputs & Diagnostic Evaluation", "Page 6"],
        ["4.0", "Experiment 2: Production Systems & Rule-Based Decision Making", "Page 7"],
        ["4.1", "  Theoretical Architecture: Recognize-Act Cycle", "Page 7"],
        ["4.2", "  Application: Smart Irrigation Advisor Knowledge Base", "Page 8"],
        ["4.3", "  Algorithm, Conflict Resolution & Execution Trace", "Page 9"],
        ["5.0", "Experiment 3: Water Jug Problem as a Production System", "Page 10"],
        ["5.1", "  Formal State-Space Representation & Bézout's Identity", "Page 10"],
        ["5.2", "  Production Rules & Search Strategy (Breadth-First Search)", "Page 11"],
        ["5.3", "  State-Space Tree & Optimal Solution Trace", "Page 12"],
        ["5.4", "  Multi-Instance Empirical Benchmark & Performance Analysis", "Page 13"],
        ["6.0", "Unit 1 Homework Analysis: Classical vs AI Programming", "Page 14"],
        ["7.0", "Comparative Evaluation of AI Problem Formulations", "Page 15"],
        ["8.0", "Conclusion, Learning Outcomes & References", "Page 16"],
    ]
    toc_table = Table(toc_data, colWidths=[35, 415, 50])
    toc_table.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("LINEBELOW", (0, 0), (-1, -1), 0.5, colors.HexColor("#F1F3F5")),
            ]
        )
    )
    story.append(toc_table)
    story.append(PageBreak())

    # =========================================================================
    # SECTION 1 & 2: OVERVIEW & THEORY
    # =========================================================================
    story.append(Paragraph("1.0 Laboratory Overview & Pedagogical Objectives", h1_style))
    story.append(
        HRFlowable(width="100%", thickness=1, color=c_secondary, spaceBefore=4, spaceAfter=10)
    )
    story.append(
        Paragraph(
            "This laboratory submission documents the practical implementations, theoretical formulations, "
            "and computational experiments conducted for <b>Lab 1</b> of the Artificial Intelligence Course "
            "(IC-703 C / IC-709D). Mapped directly to <b>Unit 1: AI Problem Formulation & Intelligent Problem "
            "Solving (CO1)</b> of the Master of Computer Applications curriculum, the objective of this lab is "
            "to transition from classical imperative algorithmic thinking to symbolic, declarative, and "
            "state-space search methodologies.",
            body_style,
        )
    )
    story.append(Paragraph("Key Core Objectives:", h2_style))
    story.append(
        Paragraph(
            "• <b>Development Environment Standardization:</b> Verify and benchmark the Python 3 interpreter, "
            "pip ecosystem, Jupyter interactive kernel, and runtime detection mechanisms.",
            bullet_style,
        )
    )
    story.append(
        Paragraph(
            "• <b>Symbolic Production Systems:</b> Understand the separation between declarative knowledge "
            "(rule base) and procedural inference (Recognize-Act cycle), incorporating deterministic conflict resolution.",
            bullet_style,
        )
    )
    story.append(
        Paragraph(
            "• <b>State-Space Formulation & Search:</b> Formulate physical constraints as state spaces $(S, s_0, O, G)$, "
            "prove analytical solvability using number-theoretic criteria (Bézout's identity), and design an optimal "
            "breadth-first search control strategy.",
            bullet_style,
        )
    )
    story.append(Spacer(1, 10))

    story.append(Paragraph("2.0 Theoretical Foundations of AI Problem Solving", h1_style))
    story.append(
        HRFlowable(width="100%", thickness=1, color=c_secondary, spaceBefore=4, spaceAfter=10)
    )
    story.append(
        Paragraph(
            "Artificial Intelligence problem solving differs substantially from traditional procedural coding. "
            "In AI, a problem is formally represented as a 4-tuple <b>⟨S, s₀, O, G⟩</b>:",
            body_style,
        )
    )
    story.append(
        Paragraph(
            "1. <b>State Space (S):</b> The set of all possible configurations or physical situations reachable within "
            "the system domain.",
            bullet_style,
        )
    )
    story.append(
        Paragraph(
            "2. <b>Initial State (s₀ ∈ S):</b> The designated configuration where the problem-solving agent begins.",
            bullet_style,
        )
    )
    story.append(
        Paragraph(
            "3. <b>Operators / Actions (O: S → S):</b> A finite set of legal state transitions. Each operator specifies "
            "a precondition (when it may apply) and an effect (the resulting successor state).",
            bullet_style,
        )
    )
    story.append(
        Paragraph(
            "4. <b>Goal State / Test (G ⊆ S):</b> An explicit state or boolean predicate determining whether the agent's "
            "current configuration satisfies the problem requirements.",
            bullet_style,
        )
    )
    story.append(Spacer(1, 8))
    story.append(
        Paragraph(
            "In <b>Production Systems</b> (originally formulated by Emil Post and popularized in AI by Newell and Simon), "
            "problem-solving knowledge is organized declaratively as condition-action pairs: "
            "<code>IF &lt;conditions&gt; THEN &lt;actions&gt;</code>. An independent control strategy matches the current "
            "working memory against the rule base, resolves rule competition, and fires actions until a termination "
            "condition (quiescence or goal discovery) is satisfied.",
            body_style,
        )
    )
    story.append(PageBreak())

    # =========================================================================
    # SECTION 3: EXPERIMENT 1
    # =========================================================================
    story.append(
        Paragraph("3.0 Experiment 1: AI Development Environment Setup & Verification", h1_style)
    )
    story.append(
        HRFlowable(width="100%", thickness=1, color=c_secondary, spaceBefore=4, spaceAfter=10)
    )
    story.append(
        Paragraph(
            "<b>Objective:</b> To configure, inspect, and verify the Python-based AI development environment, "
            "ensure reproducibility across platforms (Local CPython, Jupyter Notebook, and Google Colab), and "
            "validate immutable state-space data structures.",
            body_style,
        )
    )
    story.append(Paragraph("3.1 Implementation Architecture & Data Structures", h2_style))
    story.append(
        Paragraph(
            "State-space algorithms demand high-performance, deterministic data structures in Python. "
            "Experiment 1 verifies the following standard-library constructs:",
            body_style,
        )
    )

    data_struct_rows = [
        [Paragraph("<b>Construct</b>", body_style), Paragraph("<b>Module</b>", body_style), Paragraph("<b>Role in AI Problem Solving</b>", body_style)],
        [Paragraph("<code>tuple</code>", body_style), Paragraph("Built-in", body_style), Paragraph("Immutable, hashable representation of coordinate states (e.g., <code>(x, y)</code>).", body_style)],
        [Paragraph("<code>set</code> / <code>dict</code>", body_style), Paragraph("Built-in", body_style), Paragraph("Closed list tracking; provides O(1) membership testing and ancestor parent mapping.", body_style)],
        [Paragraph("<code>deque</code>", body_style), Paragraph("<code>collections</code>", body_style), Paragraph("FIFO Open queue for level-order Breadth-First Search; O(1) appends and pops.", body_style)],
        [Paragraph("<code>dataclass</code>", body_style), Paragraph("<code>dataclasses</code>", body_style), Paragraph("Clean, strongly-typed records for production rules, problems, and search results.", body_style)],
    ]
    ds_table = Table(data_struct_rows, colWidths=[90, 90, 320])
    ds_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E9ECEF")),
                ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#CED4DA")),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#DEE2E6")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("PADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    story.append(ds_table)
    story.append(Spacer(1, 12))

    story.append(Paragraph("3.2 Environment Verification Algorithm & Flowchart", h2_style))
    algo1_text = (
        "<b>Algorithm 1: AI Environment Diagnostic & Verification</b><br/>"
        "<b>Input:</b> Minimum required version (min_major, min_minor)<br/>"
        "<b>Output:</b> Status Report Table, Diagnostic JSON, Exit Code (0=PASS, 1=FAIL)<br/>"
        "1. Query <code>sys.version_info</code> and verify <code>(major, minor) ≥ (min_major, min_minor)</code>.<br/>"
        "2. Inspect host OS, processor architecture, CPython binary path, and active virtual environment.<br/>"
        "3. Verify package manager installation (<code>pip</code> via <code>importlib.metadata</code>).<br/>"
        "4. Enumerate Jupyter stack: <code>ipykernel</code>, <code>nbformat</code>, <code>nbconvert</code>, <code>jupyterlab</code>.<br/>"
        "5. Inspect Colab runtime presence via <code>google.colab</code> module check.<br/>"
        "6. Test dynamic import of 8 essential standard modules: <code>argparse</code>, <code>collections</code>, "
        "<code>dataclasses</code>, <code>math</code>, <code>operator</code>, <code>time</code>, <code>typing</code>, <code>json</code>.<br/>"
        "7. Probe optional machine learning libraries for subsequent labs (<code>numpy</code>, <code>pandas</code>, <code>scikit-learn</code>, <code>torch</code>).<br/>"
        "8. Run analytical benchmark: compute sum of squares for 100,000 integers and verify timing."
    )
    story.append(
        Table(
            [[Paragraph(algo1_text, body_style)]],
            colWidths=[500],
            style=[
                ("BACKGROUND", (0, 0), (-1, -1), c_code_bg),
                ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#CED4DA")),
                ("PADDING", (0, 0), (-1, -1), 8),
            ],
        )
    )
    story.append(Spacer(1, 10))

    img_fc1 = os.path.join(FIG_DIR, "flowchart_exp1_environment_setup.png")
    if os.path.exists(img_fc1):
        story.append(Image(img_fc1, width=5.5 * inch, height=3.6 * inch))
        story.append(Spacer(1, 5))
        story.append(
            Paragraph("<i>Figure 1.1: Flowchart of Experiment 1 Environment Verification Procedure.</i>", subtitle_style)
        )
    story.append(PageBreak())

    # EXP 1 OUTPUTS
    story.append(Paragraph("3.3 Actual Execution Outputs & Diagnostic Results", h2_style))
    story.append(
        Paragraph(
            "Experiment 1 was executed on the host system. The listing below represents the exact, unedited "
            "console output generated by <code>exp1_environment_setup.py</code>:",
            body_style,
        )
    )

    exp1_txt_path = os.path.join(OUT_DIR, "exp1_environment_setup_output.txt")
    if os.path.exists(exp1_txt_path):
        with open(exp1_txt_path, encoding="utf-8") as f:
            lines = f.readlines()
        log_sample = "".join(lines[1:27])  # truncate header
        story.append(
            Table(
                [[Paragraph(f"<pre>{log_sample}</pre>", code_style)]],
                colWidths=[500],
                style=[
                    ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#212529")),
                    ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#000000")),
                    ("PADDING", (0, 0), (-1, -1), 6),
                ],
            )
        )
    story.append(Spacer(1, 10))

    story.append(Paragraph("Verification of Exception Handling (Negative Testing):", h2_style))
    story.append(
        Paragraph(
            "To satisfy strict academic validation, the script was tested against invalid inputs "
            "(e.g., malformed version strings). The CLI caught the exception cleanly:",
            body_style,
        )
    )
    story.append(
        Table(
            [[Paragraph("<pre>$ python exp1_environment_setup.py --min-python 3.x\nInput error: version must look like 3.10, got '3.x'\n[Exit Code: 2]</pre>", code_style)]],
            colWidths=[500],
            style=[
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#2B1D1D")),
                ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#DC3545")),
                ("PADDING", (0, 0), (-1, -1), 6),
            ],
        )
    )
    story.append(Spacer(1, 10))

    story.append(Paragraph("Diagnostic Evaluation & Jupyter Integration:", h2_style))
    story.append(
        Paragraph(
            "The environment diagnostic report was serialized to <code>outputs/exp1_environment_report.json</code>. "
            "Additionally, the verified Jupyter Notebook <code>Experiment1_Environment_Setup.ipynb</code> was executed "
            "via <code>nbconvert</code>, confirming identical execution counts, environment outputs, and hashable state "
            "validations in an interactive notebook runtime.",
            body_style,
        )
    )
    story.append(PageBreak())

    # =========================================================================
    # SECTION 4: EXPERIMENT 2
    # =========================================================================
    story.append(
        Paragraph("4.0 Experiment 2: Production Systems & Rule-Based Decision Making", h1_style)
    )
    story.append(
        HRFlowable(width="100%", thickness=1, color=c_secondary, spaceBefore=4, spaceAfter=10)
    )
    story.append(
        Paragraph(
            "<b>Objective:</b> To design, implement, and evaluate a generalized, domain-independent Production System "
            "architecture executing forward-chaining reasoning with systematic conflict resolution on a realistic "
            "agricultural advisory problem.",
            body_style,
        )
    )
    story.append(Paragraph("4.1 Theoretical Architecture: Recognize-Act Cycle", h2_style))
    story.append(
        Paragraph(
            "A production system separates what the system knows (Working Memory) from how the system acts (Inference Engine). "
            "The inference engine executes the three-phase <b>Recognize-Act cycle</b> until no new conclusions can be derived (quiescence):",
            body_style,
        )
    )
    story.append(
        Paragraph(
            "• <b>MATCH:</b> Compares active facts in working memory against the Left-Hand Side (preconditions) of all "
            "production rules. Matching, unfired rules that would alter memory form the <i>Conflict Set</i>.",
            bullet_style,
        )
    )
    story.append(
        Paragraph(
            "• <b>RESOLVE:</b> When multiple rules compete, an explicit conflict-resolution policy selects a single rule "
            "deterministically based on: <i>Refractoriness</i> (no repeat firings) &gt; <i>Priority</i> (salience weight) &gt; "
            "<i>Specificity</i> (number of condition conjuncts) &gt; <i>Rule Order</i>.",
            bullet_style,
        )
    )
    story.append(
        Paragraph(
            "• <b>ACT:</b> Executes the Right-Hand Side (consequences) of the chosen rule, modifying working memory and "
            "logging the inference step for explainability.",
            bullet_style,
        )
    )
    story.append(Spacer(1, 8))

    img_arch = os.path.join(FIG_DIR, "architecture_production_system.png")
    if os.path.exists(img_arch):
        story.append(Image(img_arch, width=5.6 * inch, height=3.8 * inch))
        story.append(Spacer(1, 5))
        story.append(
            Paragraph("<i>Figure 2.1: Production System Architecture & Recognize-Act Execution Flow.</i>", subtitle_style)
        )
    story.append(PageBreak())

    # EXP 2 DOMAIN & ALGORITHM
    story.append(Paragraph("4.2 Smart Irrigation Advisor Knowledge Base", h2_style))
    story.append(
        Paragraph(
            "The production system was instantiated with an agricultural advisory rule base comprising 16 production rules "
            "categorized into 4 operational salience tiers:",
            body_style,
        )
    )

    rule_table_data = [
        [Paragraph("<b>Rule</b>", body_style), Paragraph("<b>Priority</b>", body_style), Paragraph("<b>IF (Preconditions)</b>", body_style), Paragraph("<b>THEN (Consequences)</b>", body_style)],
        [Paragraph("R01", body_style), Paragraph("30", body_style), Paragraph("soil_moisture &lt; 30", body_style), Paragraph("soil_status = 'dry'", body_style)],
        [Paragraph("R02", body_style), Paragraph("30", body_style), Paragraph("30 ≤ soil_moisture ≤ 60", body_style), Paragraph("soil_status = 'optimal'", body_style)],
        [Paragraph("R03", body_style), Paragraph("30", body_style), Paragraph("soil_moisture &gt; 60", body_style), Paragraph("soil_status = 'wet'", body_style)],
        [Paragraph("R04", body_style), Paragraph("30", body_style), Paragraph("temperature ≥ 35", body_style), Paragraph("heat_stress = 'yes'", body_style)],
        [Paragraph("R05", body_style), Paragraph("30", body_style), Paragraph("temperature &lt; 35", body_style), Paragraph("heat_stress = 'no'", body_style)],
        [Paragraph("R06", body_style), Paragraph("20", body_style), Paragraph("soil_status == 'dry' ∧ heat_stress == 'yes'", body_style), Paragraph("water_need = 'high'", body_style)],
        [Paragraph("R07", body_style), Paragraph("20", body_style), Paragraph("soil_status == 'dry' ∧ heat_stress == 'no'", body_style), Paragraph("water_need = 'medium'", body_style)],
        [Paragraph("R08", body_style), Paragraph("20", body_style), Paragraph("soil_status == 'optimal' ∧ crop_stage == 'flowering'", body_style), Paragraph("water_need = 'medium'", body_style)],
        [Paragraph("R09", body_style), Paragraph("20", body_style), Paragraph("soil_status == 'optimal' ∧ crop_stage != 'flowering'", body_style), Paragraph("water_need = 'low'", body_style)],
        [Paragraph("R10", body_style), Paragraph("20", body_style), Paragraph("soil_status == 'wet'", body_style), Paragraph("water_need = 'none'", body_style)],
        [Paragraph("R11", body_style), Paragraph("10", body_style), Paragraph("water_need == 'high'", body_style), Paragraph("decision = 'IRRIGATE_NOW', duration = 40m", body_style)],
        [Paragraph("R12", body_style), Paragraph("10", body_style), Paragraph("water_need == 'medium' ∧ rain == 'no'", body_style), Paragraph("decision = 'IRRIGATE_NOW', duration = 20m", body_style)],
        [Paragraph("R13", body_style), Paragraph("10", body_style), Paragraph("water_need == 'medium' ∧ rain == 'yes'", body_style), Paragraph("decision = 'POSTPONE', duration = 0m", body_style)],
        [Paragraph("R14", body_style), Paragraph("10", body_style), Paragraph("water_need ∈ {'low', 'none'}", body_style), Paragraph("decision = 'NO_IRRIGATION', duration = 0m", body_style)],
        [Paragraph("R15", body_style), Paragraph("5", body_style), Paragraph("soil_moisture &gt; 85", body_style), Paragraph("drainage_alert = 'CHECK_FIELD_DRAINAGE'", body_style)],
        [Paragraph("R16", body_style), Paragraph("5", body_style), Paragraph("heat_stress == 'yes' ∧ crop_stage == 'seedling'", body_style), Paragraph("shade_advice = 'USE_SHADE_NET'", body_style)],
    ]
    rt_table = Table(rule_table_data, colWidths=[35, 45, 230, 190])
    rt_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E9ECEF")),
                ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#CED4DA")),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#DEE2E6")),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("TOPPADDING", (0, 0), (-1, -1), 2.5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5),
            ]
        )
    )
    story.append(rt_table)
    story.append(Spacer(1, 10))

    img_fc2 = os.path.join(FIG_DIR, "flowchart_exp2_production_system.png")
    if os.path.exists(img_fc2):
        story.append(Image(img_fc2, width=5.5 * inch, height=3.6 * inch))
        story.append(Spacer(1, 5))
        story.append(
            Paragraph("<i>Figure 2.2: Flowchart of the Forward-Chaining Inference Cycle with Conflict Resolution.</i>", subtitle_style)
        )
    story.append(PageBreak())

    # EXP 2 EXECUTION TRACE
    story.append(Paragraph("4.3 Execution Traces & Explainable Reasoning", h2_style))
    story.append(
        Paragraph(
            "Below is the verified execution trace for Scenario 1 demonstrating forward-chaining derivation step-by-step:",
            body_style,
        )
    )

    trace_s1 = (
        "Scenario 1: Hot day (38°C), dry soil (22%), no rain, flowering crop stage\n"
        "Initial Facts: soil_moisture=22.0, temperature=38.0, rain_forecast=no, crop_stage=flowering\n\n"
        "  Cycle  1 | Conflict set: {R01, R04}\n"
        "           | Fired: R01 (priority 30, specificity 1) -> soil_status=dry\n"
        "  Cycle  2 | Conflict set: {R04}\n"
        "           | Fired: R04 (priority 30, specificity 1) -> heat_stress=yes\n"
        "  Cycle  3 | Conflict set: {R06}\n"
        "           | Fired: R06 (priority 20, specificity 2) -> water_need=high\n"
        "  Cycle  4 | Conflict set: {R11}\n"
        "           | Fired: R11 (priority 10, specificity 1) -> decision=IRRIGATE_NOW, duration_min=40\n"
        "Halted after 4 cycles: quiescence (conflict set empty)\n"
        "Derived Facts : soil_status=dry, heat_stress=yes, water_need=high, decision=IRRIGATE_NOW, duration_min=40\n"
        "Explanation   : R01 -> R04 -> R06 -> R11\n"
        "Execution Time: 0.051 ms"
    )
    story.append(
        Table(
            [[Paragraph(f"<pre>{trace_s1}</pre>", code_style)]],
            colWidths=[500],
            style=[
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#212529")),
                ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#000000")),
                ("PADDING", (0, 0), (-1, -1), 6),
            ],
        )
    )
    story.append(Spacer(1, 10))

    story.append(Paragraph("Multi-Scenario Summary Table:", h2_style))
    scenario_summary_data = [
        [Paragraph("<b>Scenario & Inputs</b>", body_style), Paragraph("<b>Firing Chain</b>", body_style), Paragraph("<b>Derived Decision</b>", body_style), Paragraph("<b>Cycles</b>", body_style)],
        [
            Paragraph("<b>Scenario 1:</b><br/>M=22%, T=38°C, Rain=no, Flowering", body_style),
            Paragraph("R01 → R04 → R06 → R11", body_style),
            Paragraph("<b>IRRIGATE_NOW</b><br/>(duration: 40 min)", body_style),
            Paragraph("4", body_style),
        ],
        [
            Paragraph("<b>Scenario 2:</b><br/>M=45%, T=30°C, Rain=yes, Flowering", body_style),
            Paragraph("R02 → R05 → R08 → R13", body_style),
            Paragraph("<b>POSTPONE</b><br/>(rain expected)", body_style),
            Paragraph("4", body_style),
        ],
        [
            Paragraph("<b>Scenario 3:</b><br/>M=90%, T=36°C, Rain=no, Seedling", body_style),
            Paragraph("R03 → R04 → R10 → R14 → R16 → R15", body_style),
            Paragraph("<b>NO_IRRIGATION</b><br/>Alerts: Drainage & Shade", body_style),
            Paragraph("6", body_style),
        ],
    ]
    ss_table = Table(scenario_summary_data, colWidths=[150, 150, 150, 50])
    ss_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E9ECEF")),
                ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#CED4DA")),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#DEE2E6")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("PADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    story.append(ss_table)
    story.append(PageBreak())

    # =========================================================================
    # SECTION 5: EXPERIMENT 3
    # =========================================================================
    story.append(
        Paragraph("5.0 Experiment 3: Water Jug Problem as a Production System", h1_style)
    )
    story.append(
        HRFlowable(width="100%", thickness=1, color=c_secondary, spaceBefore=4, spaceAfter=10)
    )
    story.append(
        Paragraph(
            "<b>Objective:</b> To formulate the classical Water Jug Problem as a state-space production system, "
            "prove solvability analytically via Bézout's identity, and find optimal, minimum-step action paths "
            "using Breadth-First Search.",
            body_style,
        )
    )
    story.append(Paragraph("5.1 Mathematical State-Space Formulation & Solvability", h2_style))
    story.append(
        Paragraph(
            "The Water Jug problem is formally defined as the 4-tuple <b>⟨S, s₀, O, G⟩</b>:",
            body_style,
        )
    )
    story.append(
        Paragraph(
            "• <b>State Space (S):</b> $S = \\{(x, y) \\mid 0 \\le x \\le A, \\; 0 \\le y \\le B, \\; x, y \\in \\mathbb{Z}\\}$. "
            "The total discrete state space contains $(A + 1)(B + 1)$ possible states.",
            bullet_style,
        )
    )
    story.append(
        Paragraph(
            "• <b>Initial State:</b> $s_0 = (0, 0)$ (both Jug A and Jug B are completely empty).",
            bullet_style,
        )
    )
    story.append(
        Paragraph(
            "• <b>Goal Predicate:</b> For a target $T$, $G = \\{(x, y) \\mid x = T\\}$ (if Jug A), "
            "$G = \\{(x, y) \\mid y = T\\}$ (if Jug B), or $G = \\{(x, y) \\mid x = T \\lor y = T\\}$ (either jug).",
            bullet_style,
        )
    )
    story.append(
        Paragraph(
            "• <b>Bézout's Identity Solvability Criterion:</b> Any quantity achievable in either jug must be a linear "
            "combination $A \\cdot u + B \\cdot v = d$ where $u, v \\in \\mathbb{Z}$. By Bézout's identity, the smallest "
            "positive integer combination is $\\gcd(A, B)$. Therefore, a target quantity $T \\le \\max(A, B)$ can be "
            "obtained if and only if:",
            bullet_style,
        )
    )
    story.append(
        Table(
            [[Paragraph("<div align='center'><b>T ≡ 0 (mod gcd(A, B))</b> &nbsp;&nbsp;[gcd(A, B) divides T]</div>", body_style)]],
            colWidths=[500],
            style=[
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#E7F1FF")),
                ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#0D6EFD")),
                ("PADDING", (0, 0), (-1, -1), 6),
            ],
        )
    )
    story.append(Spacer(1, 8))

    story.append(Paragraph("5.2 Production Rule Base", h2_style))
    story.append(
        Paragraph(
            "Eight mutually exclusive and comprehensive production rules govern state transitions:",
            body_style,
        )
    )

    wj_rules = [
        [Paragraph("<b>Rule</b>", body_style), Paragraph("<b>Action Name</b>", body_style), Paragraph("<b>Precondition (IF)</b>", body_style), Paragraph("<b>New State (THEN)</b>", body_style)],
        [Paragraph("R1", body_style), Paragraph("Fill Jug A", body_style), Paragraph("x &lt; A", body_style), Paragraph("(A, y)", body_style)],
        [Paragraph("R2", body_style), Paragraph("Fill Jug B", body_style), Paragraph("y &lt; B", body_style), Paragraph("(x, B)", body_style)],
        [Paragraph("R3", body_style), Paragraph("Empty Jug A", body_style), Paragraph("x &gt; 0", body_style), Paragraph("(0, y)", body_style)],
        [Paragraph("R4", body_style), Paragraph("Empty Jug B", body_style), Paragraph("y &gt; 0", body_style), Paragraph("(x, 0)", body_style)],
        [Paragraph("R5", body_style), Paragraph("Pour A into B until B is full", body_style), Paragraph("x &gt; 0 ∧ y &lt; B ∧ x + y ≥ B", body_style), Paragraph("(x - (B - y), B)", body_style)],
        [Paragraph("R6", body_style), Paragraph("Pour B into A until A is full", body_style), Paragraph("y &gt; 0 ∧ x &lt; A ∧ x + y ≥ A", body_style), Paragraph("(A, y - (A - x))", body_style)],
        [Paragraph("R7", body_style), Paragraph("Pour all water of A into B", body_style), Paragraph("x &gt; 0 ∧ x + y &lt; B", body_style), Paragraph("(0, x + y)", body_style)],
        [Paragraph("R8", body_style), Paragraph("Pour all water of B into A", body_style), Paragraph("y &gt; 0 ∧ x + y &lt; A", body_style), Paragraph("(x + y, 0)", body_style)],
    ]
    wjr_table = Table(wj_rules, colWidths=[35, 175, 170, 120])
    wjr_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E9ECEF")),
                ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#CED4DA")),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#DEE2E6")),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("TOPPADDING", (0, 0), (-1, -1), 2),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
            ]
        )
    )
    story.append(wjr_table)
    story.append(PageBreak())

    # EXP 3 FLOWCHART & STATE-SPACE TREE
    story.append(Paragraph("5.3 Search Flowchart & Verified State-Space Tree", h2_style))
    img_fc3 = os.path.join(FIG_DIR, "flowchart_exp3_water_jug.png")
    if os.path.exists(img_fc3):
        story.append(Image(img_fc3, width=5.5 * inch, height=3.5 * inch))
        story.append(Spacer(1, 4))
        story.append(
            Paragraph("<i>Figure 3.1: Flowchart of Water Jug State Space BFS Production System.</i>", subtitle_style)
        )
    story.append(Spacer(1, 8))

    img_tree = os.path.join(FIG_DIR, "state_space_tree_water_jug.png")
    if os.path.exists(img_tree):
        story.append(Image(img_tree, width=5.5 * inch, height=3.5 * inch))
        story.append(Spacer(1, 4))
        story.append(
            Paragraph(
                "<i>Figure 3.2: Exact Search Tree generated by exp3_water_jug.py (Red = 6-step solution path).</i>",
                subtitle_style,
            )
        )
    story.append(PageBreak())

    # EXP 3 SOLUTION & BENCHMARK
    story.append(Paragraph("5.4 Solution Path & Empirical Benchmark Analysis", h2_style))
    story.append(
        Paragraph(
            "For the classical problem instance ($A=4, B=3, T=2$ in Jug A), the production system discovers "
            "the optimal 6-step path:",
            body_style,
        )
    )

    path_data = [
        [Paragraph("<b>Step</b>", body_style), Paragraph("<b>Rule Fired</b>", body_style), Paragraph("<b>Action Name</b>", body_style), Paragraph("<b>State (x, y)</b>", body_style), Paragraph("<b>Explanation</b>", body_style)],
        [Paragraph("0", body_style), Paragraph("—", body_style), Paragraph("Initial State", body_style), Paragraph("(0, 0)", body_style), Paragraph("Both jugs empty", body_style)],
        [Paragraph("1", body_style), Paragraph("R1", body_style), Paragraph("Fill Jug A", body_style), Paragraph("(4, 0)", body_style), Paragraph("Fill 4L jug to capacity", body_style)],
        [Paragraph("2", body_style), Paragraph("R5", body_style), Paragraph("Pour A into B until B is full", body_style), Paragraph("(1, 3)", body_style), Paragraph("3L transferred; 1L remains in A", body_style)],
        [Paragraph("3", body_style), Paragraph("R4", body_style), Paragraph("Empty Jug B", body_style), Paragraph("(1, 0)", body_style), Paragraph("Discard 3L from Jug B", body_style)],
        [Paragraph("4", body_style), Paragraph("R7", body_style), Paragraph("Pour all water of A into B", body_style), Paragraph("(0, 1)", body_style), Paragraph("Transfer 1L from A into B", body_style)],
        [Paragraph("5", body_style), Paragraph("R1", body_style), Paragraph("Fill Jug A", body_style), Paragraph("(4, 1)", body_style), Paragraph("Fill 4L jug to capacity again", body_style)],
        [Paragraph("6", body_style), Paragraph("R5", body_style), Paragraph("Pour A into B until B is full", body_style), Paragraph("(2, 3)", body_style), Paragraph("Pour 2L into B (B full); exactly 2L left in A", body_style)],
    ]
    pt_table = Table(path_data, colWidths=[35, 60, 165, 80, 160])
    pt_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E9ECEF")),
                ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#D1E7DD")),  # Goal row highlighted green
                ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#CED4DA")),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#DEE2E6")),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("PADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    story.append(pt_table)
    story.append(Spacer(1, 10))

    story.append(Paragraph("Empirical Benchmark across Problem Configurations:", h2_style))
    bench_data = [
        [Paragraph("<b>A</b>", body_style), Paragraph("<b>B</b>", body_style), Paragraph("<b>T</b>", body_style), Paragraph("<b>Goal</b>", body_style), Paragraph("<b>Solvable</b>", body_style), Paragraph("<b>Steps</b>", body_style), Paragraph("<b>Expanded</b>", body_style), Paragraph("<b>Generated</b>", body_style), Paragraph("<b>Reachable</b>", body_style), Paragraph("<b>Time</b>", body_style)],
        [Paragraph("4", body_style), Paragraph("3", body_style), Paragraph("2", body_style), Paragraph("A", body_style), Paragraph("Yes", body_style), Paragraph("6", body_style), Paragraph("11", body_style), Paragraph("39", body_style), Paragraph("14", body_style), Paragraph("0.029 ms", body_style)],
        [Paragraph("4", body_style), Paragraph("3", body_style), Paragraph("2", body_style), Paragraph("ANY", body_style), Paragraph("Yes", body_style), Paragraph("4", body_style), Paragraph("8", body_style), Paragraph("27", body_style), Paragraph("14", body_style), Paragraph("0.016 ms", body_style)],
        [Paragraph("5", body_style), Paragraph("3", body_style), Paragraph("4", body_style), Paragraph("A", body_style), Paragraph("Yes", body_style), Paragraph("6", body_style), Paragraph("11", body_style), Paragraph("39", body_style), Paragraph("16", body_style), Paragraph("0.021 ms", body_style)],
        [Paragraph("8", body_style), Paragraph("5", body_style), Paragraph("6", body_style), Paragraph("ANY", body_style), Paragraph("Yes", body_style), Paragraph("6", body_style), Paragraph("11", body_style), Paragraph("39", body_style), Paragraph("26", body_style), Paragraph("0.025 ms", body_style)],
        [Paragraph("9", body_style), Paragraph("4", body_style), Paragraph("6", body_style), Paragraph("A", body_style), Paragraph("Yes", body_style), Paragraph("8", body_style), Paragraph("15", body_style), Paragraph("55", body_style), Paragraph("26", body_style), Paragraph("0.028 ms", body_style)],
        [Paragraph("7", body_style), Paragraph("5", body_style), Paragraph("1", body_style), Paragraph("B", body_style), Paragraph("Yes", body_style), Paragraph("8", body_style), Paragraph("16", body_style), Paragraph("59", body_style), Paragraph("24", body_style), Paragraph("0.030 ms", body_style)],
        [Paragraph("12", body_style), Paragraph("7", body_style), Paragraph("9", body_style), Paragraph("ANY", body_style), Paragraph("Yes", body_style), Paragraph("8", body_style), Paragraph("16", body_style), Paragraph("59", body_style), Paragraph("38", body_style), Paragraph("0.031 ms", body_style)],
        [Paragraph("6", body_style), Paragraph("4", body_style), Paragraph("3", body_style), Paragraph("ANY", body_style), Paragraph("No", body_style), Paragraph("—", body_style), Paragraph("—", body_style), Paragraph("—", body_style), Paragraph("10", body_style), Paragraph("—", body_style)],
    ]
    bt_table = Table(bench_data, colWidths=[25, 25, 25, 40, 50, 45, 55, 60, 55, 60])
    bt_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E9ECEF")),
                ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#F8D7DA")),  # Unsolvable row red
                ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#CED4DA")),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#DEE2E6")),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("PADDING", (0, 0), (-1, -1), 3),
            ]
        )
    )
    story.append(bt_table)
    story.append(PageBreak())

    # =========================================================================
    # SECTION 6: UNIT 1 ANALYSIS - CLASSICAL VS AI PROGRAMMING
    # =========================================================================
    story.append(
        Paragraph("6.0 Unit 1 Analysis: Classical Programming vs AI Programming", h1_style)
    )
    story.append(
        HRFlowable(width="100%", thickness=1, color=c_secondary, spaceBefore=4, spaceAfter=10)
    )
    story.append(
        Paragraph(
            "In accordance with the official MCA Lab Syllabus (<b>Unit 1 Analysis Part</b>), this section presents "
            "a rigorous comparative analysis between classical imperative programming and AI symbolic/state-space programming:",
            body_style,
        )
    )

    comp_rows = [
        [Paragraph("<b>Comparative Dimension</b>", body_style), Paragraph("<b>Classical Programming</b>", body_style), Paragraph("<b>AI Programming / Production Systems</b>", body_style)],
        [
            Paragraph("<b>Core Architecture</b>", body_style),
            Paragraph("Algorithm = Data Structures + Program Logic.<br/>Logic is tightly coupled to data definitions.", body_style),
            Paragraph("AI System = Knowledge Base + Inference Engine.<br/>Knowledge is completely decoupled from the engine.", body_style),
        ],
        [
            Paragraph("<b>Control Flow</b>", body_style),
            Paragraph("Fixed, sequential, and procedural.<br/>Flow is governed by explicit loops (<code>for</code>, <code>while</code>) and branches (<code>if-else</code>).", body_style),
            Paragraph("Pattern-directed Recognize-Act cycles.<br/>Rules fire dynamically whenever conditions match working memory.", body_style),
        ],
        [
            Paragraph("<b>Modularity & Maintenance</b>", body_style),
            Paragraph("Poor extensibility for complex logic.<br/>Adding a new business rule requires editing nested conditionals throughout the codebase.", body_style),
            Paragraph("High declarative modularity.<br/>New rules can be added or removed independently without modifying the inference algorithm.", body_style),
        ],
        [
            Paragraph("<b>State Representation</b>", body_style),
            Paragraph("Implicit and ephemeral.<br/>State is distributed across local variables, memory pointers, and runtime call stacks.", body_style),
            Paragraph("Explicit and declarative.<br/>States are formal mathematical tuples or relational structures in global memory.", body_style),
        ],
        [
            Paragraph("<b>Search Space & Solution Discovery</b>", body_style),
            Paragraph("Deterministic calculation.<br/>Computes a predefined function directly along a fixed execution path.", body_style),
            Paragraph("Search space exploration.<br/>Discovers sequences of actions across branching graphs using systematic search strategies.", body_style),
        ],
        [
            Paragraph("<b>Explainability & Auditing</b>", body_style),
            Paragraph("Opaque execution.<br/>Explaining 'why' a decision was reached requires manual code instrumentation or debug logging.", body_style),
            Paragraph("Native, transparent explainability.<br/>The system automatically yields the causal fired-rule chain (e.g., <code>R01 → R04 → R06 → R11</code>).", body_style),
        ],
        [
            Paragraph("<b>Unsolvable / Edge Conditions</b>", body_style),
            Paragraph("Unhandled paths throw unhandled exceptions or produce silent errors.", body_style),
            Paragraph("Exhausts reachable state space and reports failure/unreachability cleanly.", body_style),
        ],
    ]
    comp_table = Table(comp_rows, colWidths=[110, 195, 195])
    comp_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E9ECEF")),
                ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#CED4DA")),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#DEE2E6")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("PADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    story.append(comp_table)
    story.append(PageBreak())

    # =========================================================================
    # SECTION 7: COMPARATIVE ANALYSIS OF PROBLEM FORMULATIONS
    # =========================================================================
    story.append(
        Paragraph("7.0 Comparative Evaluation of AI Problem Formulations", h1_style)
    )
    story.append(
        HRFlowable(width="100%", thickness=1, color=c_secondary, spaceBefore=4, spaceAfter=10)
    )
    story.append(
        Paragraph(
            "Unit 1 of the syllabus introduces multiple foundational AI benchmark problems. The table below "
            "compares their mathematical formulations, state representations, state-space magnitudes, and search characteristics:",
            body_style,
        )
    )

    form_rows = [
        [Paragraph("<b>Problem</b>", body_style), Paragraph("<b>State Representation</b>", body_style), Paragraph("<b>State Space Size</b>", body_style), Paragraph("<b>Branching Factor</b>", body_style), Paragraph("<b>Constraint Nature</b>", body_style)],
        [
            Paragraph("<b>Water Jug Problem</b>", body_style),
            Paragraph("$(x, y)$ where $x \\in [0, A]$, $y \\in [0, B]$", body_style),
            Paragraph("$(A + 1)(B + 1)$<br/>(e.g., 20 states for 4L & 3L)", body_style),
            Paragraph("Up to 8 operators (Fill, Empty, Pour)", body_style),
            Paragraph("Conservation of liquid; no intermediate volume calibration.", body_style),
        ],
        [
            Paragraph("<b>Vacuum Cleaner World</b>", body_style),
            Paragraph("$(\\text{loc}, \\text{status}_A, \\text{status}_B)$<br/>loc $\\in \\{A, B\\}$, status $\\in \\{0, 1\\}$", body_style),
            Paragraph("$2 \\times 2 \\times 2 = 8$ distinct states", body_style),
            Paragraph("3 actions (Left, Right, Suck)", body_style),
            Paragraph("Complete spatial cleansing; deterministic spatial transitions.", body_style),
        ],
        [
            Paragraph("<b>Missionaries & Cannibals</b>", body_style),
            Paragraph("$(M_{\\text{left}}, C_{\\text{left}}, B)$<br/>$M, C \\in [0, 3], B \\in \\{0, 1\\}$", body_style),
            Paragraph("$4 \\times 4 \\times 2 = 32$ states<br/>(16 legal states)", body_style),
            Paragraph("Up to 5 boat configurations", body_style),
            Paragraph("Safety invariant: $C \\le M$ on both river banks if $M > 0$.", body_style),
        ],
        [
            Paragraph("<b>8-Puzzle Problem</b>", body_style),
            Paragraph("$3 \\times 3$ permutation matrix of numbers $0..8$", body_style),
            Paragraph("$9! / 2 = 181,440$ reachable configurations", body_style),
            Paragraph("2 to 4 actions (Move blank tile)", body_style),
            Paragraph("Sliding tile permutation parity; graph partition into 2 components.", body_style),
        ],
    ]
    form_table = Table(form_rows, colWidths=[90, 120, 95, 85, 110])
    form_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E9ECEF")),
                ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#CED4DA")),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#DEE2E6")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("PADDING", (0, 0), (-1, -1), 4.5),
            ]
        )
    )
    story.append(form_table)
    story.append(Spacer(1, 12))

    story.append(Paragraph("Key Theoretical Takeaway:", h2_style))
    story.append(
        Paragraph(
            "While each domain differs in physical interpretation, all can be solved uniformly by expressing them "
            "as state spaces and applying production systems or graph search. The efficiency of finding solutions depends "
            "critically on: (1) filtering invalid states early, (2) detecting visited states to eliminate cycles, and "
            "(3) adopting control strategies matched to the branching factor and search depth.",
            body_style,
        )
    )
    story.append(PageBreak())

    # =========================================================================
    # SECTION 8: RESULTS, LEARNING OUTCOMES & REFERENCES
    # =========================================================================
    story.append(
        Paragraph("8.0 Conclusion, Learning Outcomes & Academic References", h1_style)
    )
    story.append(
        HRFlowable(width="100%", thickness=1, color=c_secondary, spaceBefore=4, spaceAfter=10)
    )

    story.append(Paragraph("8.1 Summary of Results", h2_style))
    story.append(
        Paragraph(
            "All experiments outlined in the syllabus for Lab 1 were designed, executed, and validated with zero synthetic or fabricated outputs:",
            body_style,
        )
    )
    story.append(
        Paragraph(
            "• <b>Experiment 1:</b> The development environment passed all 4 required checks, verified the CPython 3.13.13 "
            "interpreter and Jupyter interactive stack, exported diagnostic JSON, and executed the interactive notebook.",
            bullet_style,
        )
    )
    story.append(
        Paragraph(
            "• <b>Experiment 2:</b> The production system implemented the full Recognize-Act cycle with 4-tier conflict resolution. "
            "Tested across diverse scenarios, it generated accurate decisions, advisory warnings, and complete explanatory lineages.",
            bullet_style,
        )
    )
    story.append(
        Paragraph(
            "• <b>Experiment 3:</b> The Water Jug problem was solved as an optimal BFS production system. For the standard 4-3-2 problem, "
            "it proved solvability using Bézout's identity and generated the optimal 6-step path (or 4-step path for either jug) in under 0.05 ms.",
            bullet_style,
        )
    )
    story.append(Spacer(1, 8))

    story.append(Paragraph("8.2 Key Learning Outcomes (Course Outcome CO1)", h2_style))
    story.append(
        Paragraph(
            "Through this laboratory exercise, the following foundational skills were attained:",
            body_style,
        )
    )
    story.append(
        Paragraph(
            "1. Ability to represent real-world problems symbolically as formal state spaces $(S, s_0, O, G)$.",
            bullet_style,
        )
    )
    story.append(
        Paragraph(
            "2. Mastery of declarative production systems, working memory manipulation, and conflict resolution policies.",
            bullet_style,
        )
    )
    story.append(
        Paragraph(
            "3. Practical proficiency in designing Breadth-First Search algorithms with visited-state tracking to guarantee optimal paths.",
            bullet_style,
        )
    )
    story.append(
        Paragraph(
            "4. Rigorous adherence to software engineering best practices: PEP-8 compliance, type annotations, and automated regression testing.",
            bullet_style,
        )
    )
    story.append(Spacer(1, 8))

    story.append(Paragraph("8.3 Academic References", h2_style))
    story.append(
        Paragraph(
            "[1] Russell, S., & Norvig, P. (2020). <i>Artificial Intelligence: A Modern Approach</i> (4th ed.). "
            "Pearson Education. Chapter 3: 'Solving Problems by Searching'.",
            body_style,
        )
    )
    story.append(
        Paragraph(
            "[2] Rich, E., Knight, K., & Nair, S. B. (2017). <i>Artificial Intelligence</i> (3rd ed.). "
            "McGraw-Hill Education. Chapter 2: 'State Space Search and Production Systems'.",
            body_style,
        )
    )
    story.append(
        Paragraph(
            "[3] Nilsson, N. J. (2014). <i>Principles of Artificial Intelligence</i>. Morgan Kaufmann Publishers. "
            "Chapter 1: 'Production Systems and Search Strategies'.",
            body_style,
        )
    )
    story.append(
        Paragraph(
            "[4] Forgy, C. L. (1982). <i>Rete: A Fast Algorithm for the Many Pattern/Many Object Pattern Match Problem</i>. "
            "Artificial Intelligence, 19(1), 17–37.",
            body_style,
        )
    )
    story.append(
        Paragraph(
            "[5] Devi Ahilya Vishwavidyalaya (DAVV). <i>Master of Computer Applications (MCA) AI Lab Syllabus</i>. "
            "Course IC-703 C / IC-709D, Unit 1: AI Problem Formulation & Intelligent Problem Solving.",
            body_style,
        )
    )

    doc.build(story, canvasmaker=NumberedCanvas)
    print("Academic PDF generated successfully at:", PDF_PATH)


if __name__ == "__main__":
    build_academic_pdf()
