#!/usr/bin/env python3
"""
Generate all Lab 1 figures (requires Pillow).

Produces
    Documentation/figures/flowchart_exp1_environment_setup.png
    Documentation/figures/flowchart_exp2_production_system.png
    Documentation/figures/flowchart_exp3_water_jug.png
    Documentation/figures/architecture_production_system.png
    Documentation/figures/state_space_tree_water_jug.png
    outputs/screenshots/*.png  (terminal captures rendered from the real
                                 output logs in Lab1/outputs/*.txt)
and copies the flowcharts / diagrams to the repository-level docs/ folder.

The state-space tree is drawn from the actual search performed by
Code/exp3_water_jug.py, so the figure always matches the program.

Usage (from the Lab1 folder or anywhere):
    python Documentation/scripts/generate_figures.py
"""

import os
import shutil
import sys
from typing import Dict, List, Optional, Sequence, Tuple

from PIL import Image, ImageDraw, ImageFont

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
LAB_DIR = os.path.dirname(os.path.dirname(SCRIPT_DIR))
REPO_DIR = os.path.dirname(LAB_DIR)
FIG_DIR = os.path.join(LAB_DIR, "Documentation", "figures")
SHOT_DIR = os.path.join(LAB_DIR, "outputs", "screenshots")
OUT_DIR = os.path.join(LAB_DIR, "outputs")
DOCS_FLOW = os.path.join(REPO_DIR, "docs", "algorithm-flowcharts")
DOCS_ARCH = os.path.join(REPO_DIR, "docs", "architecture-diagrams")

sys.path.insert(0, os.path.join(LAB_DIR, "Code"))
import exp3_water_jug as wj  # noqa: E402  (path set above)

FONT_DIRS = [r"C:\Windows\Fonts", "/usr/share/fonts/truetype/dejavu",
             "/Library/Fonts", "/System/Library/Fonts/Supplemental"]


def load_font(names: Sequence[str], size: int) -> ImageFont.FreeTypeFont:
    """Load the first available TrueType font from a list of names."""
    for folder in FONT_DIRS:
        for name in names:
            path = os.path.join(folder, name)
            if os.path.exists(path):
                return ImageFont.truetype(path, size)
    return ImageFont.load_default(size)


SANS = ["arial.ttf", "DejaVuSans.ttf", "Arial.ttf"]
SANS_BOLD = ["arialbd.ttf", "DejaVuSans-Bold.ttf", "Arial Bold.ttf"]
MONO = ["consola.ttf", "DejaVuSansMono.ttf", "Courier New.ttf"]

# Colour palette
INK = (33, 37, 41)
COLORS = {
    "terminal": ((222, 247, 236), (25, 135, 84)),
    "process": ((231, 241, 255), (13, 110, 253)),
    "decision": ((255, 243, 205), (204, 145, 0)),
    "io": ((243, 232, 255), (111, 66, 193)),
    "error": ((253, 226, 228), (200, 35, 51)),
}


# ---------------------------------------------------------------------------
# Flowchart engine
# ---------------------------------------------------------------------------
class Flowchart:
    """Very small grid-based flowchart renderer."""

    COL_W, ROW_H, MARGIN_X, MARGIN_Y = 470, 128, 120, 110
    SIZES = {"terminal": (300, 66), "process": (390, 84),
             "decision": (400, 108), "io": (390, 84), "error": (330, 84)}

    def __init__(self, title: str, cols: int, rows: int) -> None:
        self.title = title
        self.width = self.MARGIN_X * 2 + cols * self.COL_W
        self.height = self.MARGIN_Y + rows * self.ROW_H + 50
        self.image = Image.new("RGB", (self.width, self.height), "white")
        self.draw = ImageDraw.Draw(self.image)
        self.font = load_font(SANS, 21)
        self.bold = load_font(SANS_BOLD, 21)
        self.small = load_font(SANS_BOLD, 19)
        self.nodes: Dict[str, Tuple[str, float, float]] = {}
        title_font = load_font(SANS_BOLD, 30)
        tw = self.draw.textlength(title, font=title_font)
        self.draw.text(((self.width - tw) / 2, 30), title, fill=INK,
                       font=title_font)

    def centre(self, col: float, row: float) -> Tuple[float, float]:
        """Pixel centre of a grid cell."""
        return (self.MARGIN_X + col * self.COL_W + self.COL_W / 2,
                self.MARGIN_Y + row * self.ROW_H + self.ROW_H / 2)

    def _wrap(self, text: str, max_width: float,
              font: ImageFont.FreeTypeFont) -> List[str]:
        lines: List[str] = []
        for paragraph in text.split("\n"):
            current = ""
            for word in paragraph.split():
                trial = f"{current} {word}".strip()
                if self.draw.textlength(trial, font=font) <= max_width:
                    current = trial
                else:
                    if current:
                        lines.append(current)
                    current = word
            lines.append(current)
        return lines

    def node(self, node_id: str, kind: str, text: str, col: float,
             row: float) -> None:
        """Draw a node of the given kind at a grid position."""
        cx, cy = self.centre(col, row)
        w, h = self.SIZES[kind]
        fill, line = COLORS[kind]
        box = (cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2)
        if kind in ("terminal",):
            self.draw.rounded_rectangle(box, radius=h / 2, fill=fill,
                                        outline=line, width=3)
            text_w = w - 40
        elif kind == "decision":
            pts = [(cx, cy - h / 2), (cx + w / 2, cy), (cx, cy + h / 2),
                   (cx - w / 2, cy)]
            self.draw.polygon(pts, fill=fill, outline=line, width=3)
            text_w = w * 0.62
        elif kind == "io":
            skew = 22
            pts = [(box[0] + skew, box[1]), (box[2], box[1]),
                   (box[2] - skew, box[3]), (box[0], box[3])]
            self.draw.polygon(pts, fill=fill, outline=line, width=3)
            text_w = w - 2 * skew - 24
        else:
            self.draw.rounded_rectangle(box, radius=10, fill=fill,
                                        outline=line, width=3)
            text_w = w - 28
        font = self.bold if kind == "terminal" else self.font
        lines = self._wrap(text, text_w, font)
        line_h = 25
        y = cy - line_h * len(lines) / 2
        for line_text in lines:
            lw = self.draw.textlength(line_text, font=font)
            self.draw.text((cx - lw / 2, y), line_text, fill=INK, font=font)
            y += line_h
        self.nodes[node_id] = (kind, cx, cy)

    def anchor(self, node_id: str, side: str) -> Tuple[float, float]:
        """Connection point on a node side: t, b, l or r."""
        kind, cx, cy = self.nodes[node_id]
        w, h = self.SIZES[kind]
        return {"t": (cx, cy - h / 2), "b": (cx, cy + h / 2),
                "l": (cx - w / 2, cy), "r": (cx + w / 2, cy)}[side]

    def edge(self, src: str, dst: str, label: str = "",
             src_side: str = "b", dst_side: str = "t",
             via: Optional[List[Tuple[float, float]]] = None) -> None:
        """Draw an orthogonal arrow; `via` holds grid-coordinate bends."""
        sx, sy = self.anchor(src, src_side)
        dx, dy = self.anchor(dst, dst_side)
        points = [(sx, sy)]
        if via:
            points += [self.centre(c, r) for c, r in via]
            # make the first bend orthogonal to the source side
            bx, by = points[1]
            points[1] = (bx, sy) if src_side in "lr" else (sx, by)
            last_x, last_y = points[-1]
            points[-1] = (last_x, dy) if dst_side in "lr" else (dx, last_y)
        elif src_side in "lr" and dst_side in "tb":
            points.append((dx, sy))
        elif src_side in "tb" and dst_side in "lr":
            points.append((sx, dy))
        elif src_side in "tb" and dst_side in "tb" and sx != dx:
            my = (sy + dy) / 2
            points += [(sx, my), (dx, my)]
        elif src_side in "lr" and dst_side in "lr" and sy != dy:
            mx = (sx + dx) / 2
            points += [(mx, sy), (mx, dy)]
        points.append((dx, dy))
        self.draw.line(points, fill=INK, width=3, joint="curve")
        self._arrow_head(points[-2], points[-1])
        if label:
            lx, ly = points[0]
            offset = {"b": (10, 6), "r": (12, -28), "l": (-48, -28),
                      "t": (10, -30)}[src_side]
            self.draw.text((lx + offset[0], ly + offset[1]), label,
                           fill=(200, 35, 51) if label == "No"
                           else (25, 135, 84), font=self.small)

    def _arrow_head(self, start: Tuple[float, float],
                    end: Tuple[float, float]) -> None:
        (x1, y1), (x2, y2) = start, end
        size = 14
        if abs(x2 - x1) >= abs(y2 - y1):
            d = 1 if x2 > x1 else -1
            pts = [(x2, y2), (x2 - d * size, y2 - size / 2),
                   (x2 - d * size, y2 + size / 2)]
        else:
            d = 1 if y2 > y1 else -1
            pts = [(x2, y2), (x2 - size / 2, y2 - d * size),
                   (x2 + size / 2, y2 - d * size)]
        self.draw.polygon(pts, fill=INK)

    def save(self, path: str) -> None:
        """Save the image as PNG."""
        self.image.save(path, dpi=(200, 200))
        print("saved", os.path.relpath(path, REPO_DIR))


def flowchart_exp1(path: str) -> None:
    """Flowchart of Code/exp1_environment_setup.py."""
    fc = Flowchart("Experiment 1: AI Environment Setup and Verification",
                   2, 14)
    fc.node("start", "terminal", "Start", 0, 0)
    fc.node("in", "io", "Read arguments: --min-python, --json", 0, 1)
    fc.node("valid", "decision", "Version argument valid?", 0, 2)
    fc.node("err", "error", "Print input error; Stop (exit code 2)", 1, 2)
    fc.node("py", "process",
            "Check Python version >= minimum (required)", 0, 3)
    fc.node("plat", "process",
            "Collect OS, interpreter path and virtual-env status (info)",
            0, 4)
    fc.node("pip", "process",
            "Check pip (required) and Jupyter packages (optional)", 0, 5)
    fc.node("colab", "process", "Detect Google Colab runtime (info)", 0, 6)
    fc.node("std", "process",
            "Import Lab 1 standard-library modules (required)", 0, 7)
    fc.node("future", "process",
            "Report AI libraries of later labs (info only)", 0, 8)
    fc.node("sanity", "process",
            "Run sanity computation and measure time (required)", 0, 9)
    fc.node("ready", "process",
            "ready <- all required checks are PASS", 0, 10)
    fc.node("report", "io",
            "Print report table and verdict READY / NOT READY", 0, 11)
    fc.node("json", "decision", "--json path given?", 0, 12)
    fc.node("save", "io", "Save JSON report", 1, 12)
    fc.node("stop", "terminal", "Stop (exit 0 if ready, else 1)", 0, 13)
    for a, b in (("start", "in"), ("in", "valid"), ("py", "plat"),
                 ("plat", "pip"), ("pip", "colab"), ("colab", "std"),
                 ("std", "future"), ("future", "sanity"),
                 ("sanity", "ready"), ("ready", "report"),
                 ("report", "json")):
        fc.edge(a, b)
    fc.edge("valid", "py", "Yes")
    fc.edge("valid", "err", "No", "r", "l")
    fc.edge("json", "save", "Yes", "r", "l")
    fc.edge("json", "stop", "No")
    fc.edge("save", "stop", "", "b", "r", via=[(1, 13)])
    fc.save(path)


def flowchart_exp2(path: str) -> None:
    """Flowchart of the recognise-act cycle in exp2_production_system.py."""
    fc = Flowchart("Experiment 2: Production System (Recognise-Act Cycle)",
                   2, 11)
    fc.node("start", "terminal", "Start", 0, 0)
    fc.node("in", "io", "Read observations: soil moisture, temperature, "
            "rain forecast, crop stage", 0, 1)
    fc.node("valid", "decision", "Observations valid?", 0, 2)
    fc.node("err", "error", "Print input error; Stop (exit code 2)", 1, 2)
    fc.node("init", "process", "Load rule base R01-R16; working memory "
            "<- observations; fired <- { }", 0, 3)
    fc.node("limit", "decision", "cycles < max cycles?", 0, 4)
    fc.node("match", "process", "MATCH: conflict set <- rules that match "
            "WM, have not fired and would change WM", 0, 5)
    fc.node("empty", "decision", "Conflict set empty?", 0, 6)
    fc.node("halt", "process", "HALT (quiescence or cycle limit)", 1, 6)
    fc.node("resolve", "process", "RESOLVE: pick rule with highest "
            "priority, then specificity, then rule order", 0, 7)
    fc.node("act", "process", "ACT: assert the rule's actions into WM, "
            "mark rule as fired, print trace", 0, 8)
    fc.node("out", "io", "Display decision, derived facts, advisories "
            "and explanation chain", 0, 9)
    fc.node("stop", "terminal", "Stop", 0, 10)
    fc.edge("start", "in")
    fc.edge("in", "valid")
    fc.edge("valid", "init", "Yes")
    fc.edge("valid", "err", "No", "r", "l")
    fc.edge("init", "limit")
    fc.edge("limit", "match", "Yes")
    fc.edge("limit", "halt", "No", "r", "t")
    fc.edge("match", "empty")
    fc.edge("empty", "halt", "Yes", "r", "l")
    fc.edge("empty", "resolve", "No")
    fc.edge("resolve", "act")
    fc.edge("act", "limit", "", "l", "l", via=[(-0.62, 8), (-0.62, 4)])
    fc.edge("halt", "out", "", "b", "r", via=[(1, 9)])
    fc.edge("out", "stop")
    fc.save(path)


def flowchart_exp3(path: str) -> None:
    """Flowchart of Code/exp3_water_jug.py."""
    fc = Flowchart("Experiment 3: Water Jug Problem as a Production System",
                   2, 13)
    fc.node("start", "terminal", "Start", 0, 0)
    fc.node("in", "io", "Input capacities A, B, target T and goal jug",
            0, 1)
    fc.node("valid", "decision", "Inputs valid? (positive, T fits jug)",
            0, 2)
    fc.node("err", "error", "Print input error; Stop (exit code 2)", 1, 2)
    fc.node("gcd", "decision", "gcd(A, B) divides T?", 0, 3)
    fc.node("nosol", "error", "Report 'not solvable'; Stop (exit code 1)",
            1, 3)
    fc.node("show", "process",
            "Display formulation and production rules R1-R8", 0, 4)
    fc.node("init", "process",
            "OPEN <- [(0, 0)];  parent <- {(0, 0): none}", 0, 5)
    fc.node("empty", "decision", "OPEN empty?", 0, 6)
    fc.node("fail", "error",
            "Report 'goal not reachable'; Stop (exit code 1)", 1, 6)
    fc.node("pop", "process", "state <- remove first state of OPEN", 0, 7)
    fc.node("apply", "process", "For each rule Ri whose condition matches "
            "state: new <- Ri(state); if new is unseen, record parent and "
            "append to OPEN", 0, 8)
    fc.node("goal", "decision", "Goal state generated?", 0, 9)
    fc.node("path", "process", "Follow parent links back to (0, 0) to "
            "build the solution path", 0, 10)
    fc.node("out", "io",
            "Display solution path and performance statistics", 0, 11)
    fc.node("stop", "terminal", "Stop (exit code 0)", 0, 12)
    fc.edge("start", "in")
    fc.edge("in", "valid")
    fc.edge("valid", "gcd", "Yes")
    fc.edge("valid", "err", "No", "r", "l")
    fc.edge("gcd", "show", "Yes")
    fc.edge("gcd", "nosol", "No", "r", "l")
    fc.edge("show", "init")
    fc.edge("init", "empty")
    fc.edge("empty", "pop", "No")
    fc.edge("empty", "fail", "Yes", "r", "l")
    fc.edge("pop", "apply")
    fc.edge("apply", "goal")
    fc.edge("goal", "path", "Yes")
    fc.edge("goal", "empty", "No", "l", "l", via=[(-0.62, 9), (-0.62, 6)])
    fc.edge("path", "out")
    fc.edge("out", "stop")
    fc.save(path)


# ---------------------------------------------------------------------------
# Architecture diagram
# ---------------------------------------------------------------------------
def architecture_diagram(path: str) -> None:
    """Components of a production system and their mapping in Lab 1."""
    width, height = 1700, 1250
    img = Image.new("RGB", (width, height), "white")
    d = ImageDraw.Draw(img)
    title = load_font(SANS_BOLD, 32)
    head = load_font(SANS_BOLD, 24)
    body = load_font(SANS, 20)
    small = load_font(SANS, 18)

    def box(xy, fill, line, heading, lines):
        d.rounded_rectangle(xy, radius=14, fill=fill, outline=line, width=3)
        x0, y0, x1, _ = xy
        hw = d.textlength(heading, font=head)
        d.text(((x0 + x1 - hw) / 2, y0 + 14), heading, fill=INK, font=head)
        y = y0 + 52
        for text in lines:
            tw = d.textlength(text, font=body)
            d.text(((x0 + x1 - tw) / 2, y), text, fill=INK, font=body)
            y += 27

    def arrow(p1, p2, label="", two_way=False):
        d.line([p1, p2], fill=INK, width=3)
        for (ax, ay), (bx, by) in ([(p1, p2), (p2, p1)] if two_way
                                   else [(p1, p2)]):
            vx, vy = bx - ax, by - ay
            length = max((vx ** 2 + vy ** 2) ** 0.5, 1)
            ux, uy = vx / length, vy / length
            size = 16
            left = (bx - ux * size - uy * size / 2,
                    by - uy * size + ux * size / 2)
            right = (bx - ux * size + uy * size / 2,
                     by - uy * size - ux * size / 2)
            d.polygon([(bx, by), left, right], fill=INK)
        if label:
            mx, my = (p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2
            d.text((mx + 10, my - 26), label, fill=(90, 90, 90), font=small)

    heading = "Architecture of a Production System (Lab 1, Experiments 2-3)"
    tw = d.textlength(heading, font=title)
    d.text(((width - tw) / 2, 28), heading, fill=INK, font=title)

    blue, purple = COLORS["process"], COLORS["io"]
    green, amber = COLORS["terminal"], COLORS["decision"]
    box((60, 120, 470, 290), *purple, "INPUT",
        ["Observations (Exp 2)", "Jug capacities, target (Exp 3)",
         "validated before use"])
    box((640, 120, 1060, 290), *blue, "WORKING MEMORY",
        ["Global database of facts", "Exp 2: attribute = value",
         "Exp 3: current state (x, y)"])
    box((1230, 120, 1640, 290), *amber, "RULE BASE",
        ["Productions IF ... THEN ...", "Exp 2: R01 - R16",
         "Exp 3: R1 - R8"])
    # Inference engine container
    d.rounded_rectangle((300, 380, 1400, 700), radius=18,
                        fill=(248, 249, 250), outline=(73, 80, 87), width=3)
    label = "INFERENCE ENGINE / CONTROL STRATEGY"
    lw = d.textlength(label, font=head)
    d.text(((300 + 1400 - lw) / 2, 396), label, fill=INK, font=head)
    box((340, 460, 640, 640), *blue, "1. MATCH",
        ["Find rules whose", "conditions hold", "(conflict set)"])
    box((700, 460, 1000, 640), *amber, "2. RESOLVE",
        ["Select one rule", "(conflict-resolution", "strategy)"])
    box((1060, 460, 1360, 640), *green, "3. ACT",
        ["Fire the rule:", "update working", "memory"])
    arrow((640, 550), (700, 550))
    arrow((1000, 550), (1060, 550))
    d.line([(1210, 640), (1210, 675), (490, 675), (490, 640)],
           fill=INK, width=3)
    d.polygon([(490, 640), (482, 656), (498, 656)], fill=INK)
    d.text((700, 645), "repeat until halt condition", fill=(90, 90, 90),
           font=small)
    box((560, 780, 1140, 950), *green, "OUTPUT",
        ["Exp 2: decision + explanation chain",
         "Exp 3: solution path + statistics",
         "Execution trace of every cycle"])
    arrow((470, 205), (640, 205), "facts")
    arrow((850, 290), (850, 380), "read / update facts", two_way=True)
    arrow((1435, 290), (1300, 380), "rules")
    arrow((850, 700), (850, 780), "result")

    # Mapping table
    rows = [("Component", "Exp 2: Smart Irrigation Advisor",
             "Exp 3: Water Jug Problem"),
            ("Control strategy", "Forward chaining, one rule per cycle",
             "Breadth-wise systematic, no repeats"),
            ("Conflict resolution", "Refractoriness > priority > "
             "specificity > order", "All applicable rules applied in "
             "R1..R8 order"),
            ("Halt condition", "Conflict set empty / cycle limit",
             "Goal state generated / OPEN empty")]
    x_cols = [60, 420, 1040, 1640]
    y = 1000
    for index, row in enumerate(rows):
        fill = (233, 236, 239) if index == 0 else "white"
        d.rectangle((x_cols[0], y, x_cols[-1], y + 52), fill=fill,
                    outline=(173, 181, 189), width=2)
        for c, text in enumerate(row):
            font = head if index == 0 else body
            d.text((x_cols[c] + 14, y + 13), text, fill=INK,
                   font=load_font(SANS_BOLD, 20) if index == 0 or c == 0
                   else font)
            if c:
                d.line([(x_cols[c], y), (x_cols[c], y + 52)],
                       fill=(173, 181, 189), width=2)
        y += 52
    img.save(path, dpi=(200, 200))
    print("saved", os.path.relpath(path, REPO_DIR))


# ---------------------------------------------------------------------------
# State-space (search) tree drawn from the real solver
# ---------------------------------------------------------------------------
def state_space_tree(path: str) -> None:
    """Draw the search tree generated by exp3 for the 4-3-2 problem."""
    problem = wj.validate_parameters(4, 3, 2, "A")
    result = wj.solve(problem, wj.build_rule_base())
    tree = result.tree
    on_path = {state for _, state in result.path}

    depth: Dict[wj.State, int] = {}
    for state in tree:                      # insertion order = generation
        parent = tree[state][0]
        depth[state] = 0 if parent is None else depth[parent] + 1
    levels: Dict[int, List[wj.State]] = {}
    for state in tree:
        levels.setdefault(depth[state], []).append(state)

    width = 1700
    level_h = 150
    height = 190 + level_h * (max(levels) + 1) + 120
    img = Image.new("RGB", (width, height), "white")
    d = ImageDraw.Draw(img)
    title = load_font(SANS_BOLD, 30)
    node_font = load_font(SANS_BOLD, 24)
    label_font = load_font(SANS_BOLD, 19)
    note_font = load_font(SANS, 20)
    heading = ("Search tree generated by exp3_water_jug.py  "
               "(A = 4, B = 3, goal: 2 L in Jug A)")
    tw = d.textlength(heading, font=title)
    d.text(((width - tw) / 2, 28), heading, fill=INK, font=title)

    pos: Dict[wj.State, Tuple[float, float]] = {}
    for level, states in levels.items():
        gap = (width - 360) / len(states)
        for i, state in enumerate(states):
            pos[state] = (180 + gap * (i + 0.5), 150 + level * level_h)
        d.text((40, 150 + level * level_h - 12), f"Depth {level}",
               fill=(108, 117, 125), font=note_font)

    radius_w, radius_h = 74, 36
    for state, (parent, rule_id) in tree.items():
        if parent is None:
            continue
        (x1, y1), (x2, y2) = pos[parent], pos[state]
        highlight = state in on_path and parent in on_path
        colour = (200, 35, 51) if highlight else (134, 142, 150)
        d.line([(x1, y1 + radius_h), (x2, y2 - radius_h)], fill=colour,
               width=5 if highlight else 2)
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        d.rectangle((mx - 22, my - 14, mx + 22, my + 12), fill="white")
        d.text((mx - 16, my - 13), rule_id, fill=colour, font=label_font)

    for state, (x, y) in pos.items():
        if problem.is_goal(state):
            fill, line = COLORS["terminal"]
        elif state in on_path:
            fill, line = (253, 226, 228), (200, 35, 51)
        else:
            fill, line = (241, 243, 245), (134, 142, 150)
        d.ellipse((x - radius_w, y - radius_h, x + radius_w, y + radius_h),
                  fill=fill, outline=line, width=3)
        text = f"({state[0]}, {state[1]})"
        tw = d.textlength(text, font=node_font)
        d.text((x - tw / 2, y - 14), text, fill=INK, font=node_font)

    note = (f"Red = solution path ({len(result.path) - 1} rule "
            f"applications); green = goal state; edge labels = rule fired. "
            f"{len(tree)} distinct states generated.")
    nw = d.textlength(note, font=note_font)
    d.text(((width - nw) / 2, height - 80), note, fill=INK, font=note_font)
    img.save(path, dpi=(200, 200))
    print("saved", os.path.relpath(path, REPO_DIR))


# ---------------------------------------------------------------------------
# Terminal captures rendered from the real output logs
# ---------------------------------------------------------------------------
def terminal_capture(log_name: str, png_name: str) -> None:
    """Render an output log as a terminal-style PNG (text unchanged)."""
    log_path = os.path.join(OUT_DIR, log_name)
    with open(log_path, encoding="utf-8") as handle:
        lines = handle.read().rstrip("\n").split("\n")
    font = load_font(MONO, 20)
    bar_font = load_font(SANS, 18)
    line_h = 25
    max_w = max(font.getlength(line) for line in lines)
    width = int(max(max_w + 60, 900))
    height = 60 + line_h * len(lines) + 60
    img = Image.new("RGB", (width, height), (30, 30, 30))
    d = ImageDraw.Draw(img)
    d.rectangle((0, 0, width, 40), fill=(60, 60, 60))
    for i, colour in enumerate(((255, 95, 86), (255, 189, 46),
                                (39, 201, 63))):
        d.ellipse((16 + i * 26, 12, 32 + i * 26, 28), fill=colour)
    caption = f"Terminal capture rendered from Lab1/outputs/{log_name}"
    d.text((110, 10), caption, fill=(220, 220, 220), font=bar_font)
    y = 55
    for line in lines:
        if line.startswith("$ "):
            colour = (106, 214, 255)
        elif line.startswith("# Captured"):
            colour = (140, 140, 140)
        elif ("error" in line.lower() or "FAIL" in line
              or "NOT READY" in line):
            colour = (255, 123, 114)
        elif line.startswith(("Result:", "DECISION", "  Environment status")):
            colour = (126, 231, 135)
        else:
            colour = (230, 230, 230)
        d.text((30, y), line, fill=colour, font=font)
        y += line_h
    path = os.path.join(SHOT_DIR, png_name)
    img.save(path)
    print("saved", os.path.relpath(path, REPO_DIR))


CAPTURES = [
    ("exp1_environment_setup_output.txt", "exp1_environment_setup.png"),
    ("exp1_invalid_input_output.txt", "exp1_invalid_input.png"),
    ("exp2_production_system_output.txt", "exp2_production_system.png"),
    ("exp2_custom_input_output.txt", "exp2_custom_input.png"),
    ("exp2_invalid_input_output.txt", "exp2_invalid_input.png"),
    ("exp3_water_jug_output.txt", "exp3_water_jug.png"),
    ("exp3_water_jug_any_jug_output.txt", "exp3_water_jug_any_jug.png"),
    ("exp3_water_jug_unsolvable_and_invalid_output.txt",
     "exp3_unsolvable_and_invalid.png"),
    ("exp3_water_jug_benchmark_output.txt", "exp3_benchmark.png"),
]


def main() -> int:
    """Generate every figure and copy diagrams to docs/."""
    for folder in (FIG_DIR, SHOT_DIR, DOCS_FLOW, DOCS_ARCH):
        os.makedirs(folder, exist_ok=True)
    flows = {"flowchart_exp1_environment_setup.png": flowchart_exp1,
             "flowchart_exp2_production_system.png": flowchart_exp2,
             "flowchart_exp3_water_jug.png": flowchart_exp3}
    for name, builder in flows.items():
        builder(os.path.join(FIG_DIR, name))
        shutil.copy(os.path.join(FIG_DIR, name),
                    os.path.join(DOCS_FLOW, "lab1_" + name))
    for name, builder in (
            ("architecture_production_system.png", architecture_diagram),
            ("state_space_tree_water_jug.png", state_space_tree)):
        builder(os.path.join(FIG_DIR, name))
        shutil.copy(os.path.join(FIG_DIR, name),
                    os.path.join(DOCS_ARCH, "lab1_" + name))
    for log_name, png_name in CAPTURES:
        try:
            terminal_capture(log_name, png_name)
        except FileNotFoundError:
            print(f"skipped {log_name}: run Code/run_all.py first")
    return 0


if __name__ == "__main__":
    sys.exit(main())
