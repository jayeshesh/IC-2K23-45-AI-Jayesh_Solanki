#!/usr/bin/env python3
"""
Lab 2: Search Algorithms & Navigation in AI.

Course : Artificial Intelligence Laboratory (IC-703 C / IC-709D)
Unit   : Unit 2 - Heuristic Search Algorithms (CO2)
Author : Jayesh Solanki (Roll No: IC-2K23-45)

Algorithms Implemented:
  1. Breadth-First Search (BFS) - Uninformed, complete, optimal.
  2. Depth-First Search (DFS) - Uninformed, memory-efficient.
  3. Greedy Best-First Search (GBFS) - Informed, heuristic f(n) = h(n).
  4. A* Search - Informed, optimal f(n) = g(n) + h(n).
  5. Hill Climbing - Local heuristic search with local-optima detection.

Laboratory Activities:
  Activity 1: 8-Puzzle Solver (Solvability parity, Manhattan vs Misplaced).
  Activity 2: Graph Traversal (Adjacency list BFS vs DFS comparison).
  Activity 3: Maze Solver & Robot Navigation (2D grid obstacle navigation).
  Activity 4: Route Planning & GPS Route Planner (City roadmap with SLD).

Strictly PEP-8 compliant and uses only the Python standard library.
"""

import argparse
import heapq
import sys
import time
from collections import deque
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Set, Tuple

LINE_WIDTH = 74


# ============================================================================
# Core Data Structures & Search Result
# ============================================================================
@dataclass
class SearchResult:
    """Standardized result object returned by all search algorithms."""

    algorithm: str
    problem: str
    found: bool
    path: List[Any]
    cost: float
    nodes_expanded: int
    nodes_generated: int
    elapsed_ms: float
    extra_metrics: Dict[str, Any] = field(default_factory=dict)


@dataclass(order=True)
class PriorityNode:
    """Node wrapper for heapq priority queue in informed search algorithms."""

    priority: float
    count: int
    state: Any = field(compare=False)
    cost: float = field(compare=False)
    parent: Optional[Any] = field(default=None, compare=False)


# ============================================================================
# Activity 1: 8-Puzzle Problem
# ============================================================================
EightPuzzleState = Tuple[int, ...]  # 9-element tuple representing 3x3 board
GOAL_8PUZZLE: EightPuzzleState = (1, 2, 3, 4, 5, 6, 7, 8, 0)

# Precomputed 2D coordinates for 3x3 grid positions (0..8)
GRID_COORDS = [(i // 3, i % 3) for i in range(9)]
GOAL_POSITIONS = {
    tile: GRID_COORDS[idx] for idx, tile in enumerate(GOAL_8PUZZLE)
}


def is_solvable_8puzzle(state: EightPuzzleState) -> bool:
    """Return True if the 8-puzzle configuration is mathematically solvable.

    For a 3x3 puzzle, solvability invariant depends on inversion count:
    A state is solvable if and only if the number of inversions is EVEN.
    """
    tiles = [t for t in state if t != 0]
    inversions = 0
    for i in range(len(tiles)):
        for j in range(i + 1, len(tiles)):
            if tiles[i] > tiles[j]:
                inversions += 1
    return inversions % 2 == 0


def get_8puzzle_neighbors(
    state: EightPuzzleState,
) -> List[Tuple[str, EightPuzzleState]]:
    """Generate valid successor states by sliding tiles into blank (0)."""
    blank_idx = state.index(0)
    row, col = GRID_COORDS[blank_idx]
    moves = [
        ("UP", row - 1, col),
        ("DOWN", row + 1, col),
        ("LEFT", row, col - 1),
        ("RIGHT", row, col + 1),
    ]
    neighbors = []
    board = list(state)
    for action, nr, nc in moves:
        if 0 <= nr < 3 and 0 <= nc < 3:
            new_idx = nr * 3 + nc
            board[blank_idx], board[new_idx] = board[new_idx], board[blank_idx]
            neighbors.append((action, tuple(board)))
            board[blank_idx], board[new_idx] = board[new_idx], board[blank_idx]
    return neighbors


def heuristic_misplaced(state: EightPuzzleState) -> int:
    """Heuristic h1: Number of misplaced tiles (excluding blank)."""
    return sum(1 for i in range(9) if state[i] != 0 and state[i] != i + 1)


def heuristic_manhattan(state: EightPuzzleState) -> int:
    """Heuristic h2: Sum of Manhattan distances of tiles to goal positions."""
    dist = 0
    for idx, tile in enumerate(state):
        if tile != 0:
            cr, cc = GRID_COORDS[idx]
            gr, gc = GOAL_POSITIONS[tile]
            dist += abs(cr - gr) + abs(cc - gc)
    return dist


def solve_8puzzle_astar(
    start: EightPuzzleState,
    heuristic_func: Callable[[EightPuzzleState], int],
    heuristic_name: str = "Manhattan",
) -> SearchResult:
    """Solve the 8-puzzle using the A* Search algorithm."""
    start_time = time.perf_counter()
    if not is_solvable_8puzzle(start):
        elapsed = (time.perf_counter() - start_time) * 1000.0
        return SearchResult(
            f"A* ({heuristic_name})",
            "8-Puzzle",
            False,
            [],
            0,
            0,
            0,
            elapsed,
            {"solvable": False},
        )

    counter = 0
    frontier: List[PriorityNode] = []
    h_start = heuristic_func(start)
    heapq.heappush(frontier, PriorityNode(h_start, counter, start, 0, None))

    came_from: Dict[EightPuzzleState, Optional[EightPuzzleState]] = {
        start: None
    }
    cost_so_far: Dict[EightPuzzleState, float] = {start: 0}
    expanded = 0
    generated = 1

    goal_node = None
    while frontier:
        node = heapq.heappop(frontier)
        current = node.state

        if current == GOAL_8PUZZLE:
            goal_node = current
            break

        expanded += 1
        current_cost = cost_so_far[current]

        for _, next_state in get_8puzzle_neighbors(current):
            new_cost = current_cost + 1
            if (
                next_state not in cost_so_far
                or new_cost < cost_so_far[next_state]
            ):
                cost_so_far[next_state] = new_cost
                priority = new_cost + heuristic_func(next_state)
                counter += 1
                generated += 1
                heapq.heappush(
                    frontier,
                    PriorityNode(
                        priority, counter, next_state, new_cost, current
                    ),
                )
                came_from[next_state] = current

    elapsed = (time.perf_counter() - start_time) * 1000.0

    path = []
    if goal_node:
        curr = goal_node
        while curr is not None:
            path.append(curr)
            curr = came_from.get(curr)
        path.reverse()

    return SearchResult(
        f"A* ({heuristic_name})",
        "8-Puzzle",
        goal_node is not None,
        path,
        len(path) - 1 if path else 0,
        expanded,
        generated,
        elapsed,
        {"solvable": True},
    )


# ============================================================================
# Activity 2: Graph Traversal (BFS & DFS)
# ============================================================================
AdjacencyList = Dict[str, List[str]]

SAMPLE_GRAPH: AdjacencyList = {
    "A": ["B", "C"],
    "B": ["A", "D", "E"],
    "C": ["A", "F", "G"],
    "D": ["B"],
    "E": ["B", "H"],
    "F": ["C"],
    "G": ["C", "H"],
    "H": ["E", "G"],
}


def bfs_graph(graph: AdjacencyList, start: str, goal: str) -> SearchResult:
    """Breadth-First Search on an adjacency list graph."""
    t0 = time.perf_counter()
    queue = deque([start])
    parent: Dict[str, Optional[str]] = {start: None}
    visited: Set[str] = {start}
    traversal_order = []
    expanded = 0
    generated = 1

    found = False
    while queue:
        curr = queue.popleft()
        traversal_order.append(curr)
        expanded += 1

        if curr == goal:
            found = True
            break

        for neighbor in sorted(graph.get(curr, [])):
            if neighbor not in visited:
                visited.add(neighbor)
                parent[neighbor] = curr
                queue.append(neighbor)
                generated += 1

    elapsed = (time.perf_counter() - t0) * 1000.0
    path = []
    if found:
        curr = goal
        while curr is not None:
            path.append(curr)
            curr = parent[curr]
        path.reverse()

    return SearchResult(
        "BFS",
        "Graph Traversal",
        found,
        path,
        len(path) - 1 if path else 0,
        expanded,
        generated,
        elapsed,
        {"traversal_order": traversal_order},
    )


def dfs_graph(graph: AdjacencyList, start: str, goal: str) -> SearchResult:
    """Depth-First Search on an adjacency list graph."""
    t0 = time.perf_counter()
    stack = [start]
    parent: Dict[str, Optional[str]] = {start: None}
    visited: Set[str] = set()
    traversal_order = []
    expanded = 0
    generated = 1

    found = False
    while stack:
        curr = stack.pop()
        if curr in visited:
            continue
        visited.add(curr)
        traversal_order.append(curr)
        expanded += 1

        if curr == goal:
            found = True
            break

        # Reverse sorted order so alphabetical order is popped first
        for neighbor in sorted(graph.get(curr, []), reverse=True):
            if neighbor not in visited:
                if neighbor not in parent:
                    parent[neighbor] = curr
                stack.append(neighbor)
                generated += 1

    elapsed = (time.perf_counter() - t0) * 1000.0
    path = []
    if found:
        curr = goal
        while curr is not None:
            path.append(curr)
            curr = parent[curr]
        path.reverse()

    return SearchResult(
        "DFS",
        "Graph Traversal",
        found,
        path,
        len(path) - 1 if path else 0,
        expanded,
        generated,
        elapsed,
        {"traversal_order": traversal_order},
    )


# ============================================================================
# Activity 3: 2D Grid Maze Solver & Robot Navigation
# ============================================================================
GridCoord = Tuple[int, int]
# 0 = open path, 1 = wall/obstacle
SAMPLE_MAZE = [
    [0, 0, 0, 0, 0, 0, 1, 0],
    [1, 1, 0, 1, 1, 0, 1, 0],
    [0, 0, 0, 0, 1, 0, 0, 0],
    [0, 1, 1, 0, 0, 0, 1, 0],
    [0, 1, 0, 0, 1, 1, 1, 0],
    [0, 0, 0, 1, 0, 0, 0, 0],
    [0, 1, 0, 0, 0, 1, 1, 0],
    [0, 0, 0, 1, 0, 0, 0, 0],
]


def maze_manhattan_heuristic(a: GridCoord, b: GridCoord) -> float:
    """Manhattan distance between two 2D grid coordinates."""
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def get_grid_neighbors(
    grid: List[List[int]], coord: GridCoord
) -> List[GridCoord]:
    """Return adjacent, obstacle-free orthogonal coordinates."""
    r, c = coord
    rows, cols = len(grid), len(grid[0])
    valid = []
    for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        nr, nc = r + dr, c + dc
        if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] == 0:
            valid.append((nr, nc))
    return valid


def solve_maze_astar(
    grid: List[List[int]], start: GridCoord, goal: GridCoord
) -> SearchResult:
    """Find obstacle-free path for robot navigation using A*."""
    t0 = time.perf_counter()
    frontier: List[PriorityNode] = []
    counter = 0
    h_start = maze_manhattan_heuristic(start, goal)
    heapq.heappush(frontier, PriorityNode(h_start, counter, start, 0))

    came_from: Dict[GridCoord, Optional[GridCoord]] = {start: None}
    cost_so_far: Dict[GridCoord, float] = {start: 0}
    expanded = 0
    generated = 1

    found = False
    while frontier:
        node = heapq.heappop(frontier)
        curr = node.state

        if curr == goal:
            found = True
            break

        expanded += 1
        for nxt in get_grid_neighbors(grid, curr):
            new_cost = cost_so_far[curr] + 1
            if nxt not in cost_so_far or new_cost < cost_so_far[nxt]:
                cost_so_far[nxt] = new_cost
                priority = new_cost + maze_manhattan_heuristic(nxt, goal)
                counter += 1
                generated += 1
                heapq.heappush(
                    frontier, PriorityNode(priority, counter, nxt, new_cost)
                )
                came_from[nxt] = curr

    elapsed = (time.perf_counter() - t0) * 1000.0
    path = []
    if found:
        curr = goal
        while curr is not None:
            path.append(curr)
            curr = came_from[curr]
        path.reverse()

    return SearchResult(
        "A*",
        "Robot Navigation / Maze",
        found,
        path,
        len(path) - 1 if path else 0,
        expanded,
        generated,
        elapsed,
    )


# ============================================================================
# Activity 4: Route Planning & GPS Route Planner (Road Network)
# ============================================================================
RoadNetwork = Dict[str, Dict[str, float]]

# Romania-style roadmap network with real connection distances (km)
ROADMAP: RoadNetwork = {
    "Arad": {"Zerind": 75, "Sibiu": 140, "Timisoara": 118},
    "Zerind": {"Arad": 75, "Oradea": 71},
    "Oradea": {"Zerind": 71, "Sibiu": 151},
    "Sibiu": {"Arad": 140, "Oradea": 151, "Fagaras": 99, "Rimnicu": 80},
    "Fagaras": {"Sibiu": 99, "Bucharest": 211},
    "Rimnicu": {"Sibiu": 80, "Pitesti": 97, "Craiova": 146},
    "Pitesti": {"Rimnicu": 97, "Bucharest": 101, "Craiova": 138},
    "Timisoara": {"Arad": 118, "Lugoj": 111},
    "Lugoj": {"Timisoara": 111, "Mehadia": 70},
    "Mehadia": {"Lugoj": 70, "Drobeta": 75},
    "Drobeta": {"Mehadia": 75, "Craiova": 120},
    "Craiova": {"Drobeta": 120, "Rimnicu": 146, "Pitesti": 138},
    "Bucharest": {
        "Fagaras": 211,
        "Pitesti": 101,
        "Giurgiu": 90,
        "Urziceni": 85,
    },
    "Giurgiu": {"Bucharest": 90},
    "Urziceni": {"Bucharest": 85, "Hirsova": 98, "Vaslui": 142},
    "Hirsova": {"Urziceni": 98, "Eforie": 86},
    "Eforie": {"Hirsova": 86},
    "Vaslui": {"Urziceni": 142, "Iasi": 92},
    "Iasi": {"Vaslui": 92, "Neamt": 87},
    "Neamt": {"Iasi": 87},
}

# Straight-line distance (SLD) heuristic to Bucharest
SLD_TO_BUCHAREST: Dict[str, float] = {
    "Arad": 366,
    "Bucharest": 0,
    "Craiova": 160,
    "Drobeta": 242,
    "Eforie": 161,
    "Fagaras": 176,
    "Giurgiu": 77,
    "Hirsova": 151,
    "Iasi": 226,
    "Lugoj": 244,
    "Mehadia": 241,
    "Neamt": 234,
    "Oradea": 380,
    "Pitesti": 100,
    "Rimnicu": 193,
    "Sibiu": 253,
    "Timisoara": 329,
    "Urziceni": 80,
    "Vaslui": 199,
    "Zerind": 374,
}


def solve_route_planner(
    roadmap: RoadNetwork,
    heuristics: Dict[str, float],
    start: str,
    goal: str,
    algorithm: str = "A*",
) -> SearchResult:
    """Solve route planning using Greedy Best-First Search or A*."""
    t0 = time.perf_counter()
    frontier: List[PriorityNode] = []
    counter = 0

    h_val = heuristics.get(start, 0)
    p_val = h_val
    heapq.heappush(frontier, PriorityNode(p_val, counter, start, 0))

    came_from: Dict[str, Optional[str]] = {start: None}
    cost_so_far: Dict[str, float] = {start: 0}
    expanded = 0
    generated = 1

    found = False
    while frontier:
        node = heapq.heappop(frontier)
        curr = node.state

        if curr == goal:
            found = True
            break

        expanded += 1
        for neighbor, edge_weight in roadmap.get(curr, {}).items():
            new_cost = cost_so_far[curr] + edge_weight
            if neighbor not in cost_so_far or new_cost < cost_so_far[neighbor]:
                cost_so_far[neighbor] = new_cost
                h_n = heuristics.get(neighbor, 0)
                if algorithm == "A*":
                    priority = new_cost + h_n
                else:  # Greedy Best-First Search
                    priority = h_n
                counter += 1
                generated += 1
                heapq.heappush(
                    frontier,
                    PriorityNode(priority, counter, neighbor, new_cost),
                )
                came_from[neighbor] = curr

    elapsed = (time.perf_counter() - t0) * 1000.0
    path = []
    if found:
        curr = goal
        while curr is not None:
            path.append(curr)
            curr = came_from[curr]
        path.reverse()

    return SearchResult(
        algorithm,
        f"Route Planning ({start} -> {goal})",
        found,
        path,
        cost_so_far.get(goal, 0),
        expanded,
        generated,
        elapsed,
    )


# Activity 5: Hill Climbing (Function Maximization)
# ============================================================================
def hill_climbing_maximize(
    start: int = 0, step: int = 1, max_iterations: int = 20
) -> SearchResult:
    """Move to a better neighbour until a local maximum is reached.

    The sample objective has its maximum at x = 4:
        f(x) = -((x - 4) ** 2) + 16
    """
    if step <= 0:
        raise ValueError("step must be a positive integer")
    if max_iterations <= 0:
        raise ValueError("max_iterations must be positive")

    def objective(x: int) -> int:
        return -((x - 4) ** 2) + 16

    start_time = time.perf_counter()
    current = start
    path = [current]
    expanded = 0
    generated = 1

    for _ in range(max_iterations):
        neighbours = [current - step, current + step]
        expanded += 1
        generated += len(neighbours)
        best_neighbour = max(neighbours, key=objective)

        if objective(best_neighbour) <= objective(current):
            break

        current = best_neighbour
        path.append(current)

    elapsed = (time.perf_counter() - start_time) * 1000.0
    return SearchResult(
        "Hill Climbing",
        "Function Maximization",
        True,
        path,
        objective(current),
        expanded,
        generated,
        elapsed,
        {"maximum_x": current, "maximum_value": objective(current)},
    )


# ============================================================================
# Formatting & Presentation Helpers
# ============================================================================
def print_banner(title: str) -> None:
    print("=" * LINE_WIDTH)
    print(f" {title}")
    print("=" * LINE_WIDTH)


def print_result(res: SearchResult) -> None:
    status = "FOUND" if res.found else "NOT FOUND"
    print(f"  Algorithm           : {res.algorithm}")
    print(f"  Problem Domain      : {res.problem}")
    print(f"  Status              : {status}")
    print(f"  Solution Path       : {' -> '.join(str(p) for p in res.path)}")
    print(f"  Path Length / Cost  : {res.cost}")
    print(f"  Nodes Expanded      : {res.nodes_expanded}")
    print(f"  Nodes Generated     : {res.nodes_generated}")
    print(f"  Execution Time      : {res.elapsed_ms:.3f} ms")
    print()


# ============================================================================
# Execution Modes
# ============================================================================
def run_all_activities() -> None:
    """Execute all laboratory activities and print academic outputs."""
    print_banner("LAB 2: HEURISTIC SEARCH ALGORITHMS & NAVIGATION (CO2)")
    print("Author: Jayesh Solanki | Roll No: IC-2K23-45 | MCA AI Lab\n")

    # 1. 8-Puzzle Solver
    print("-" * LINE_WIDTH)
    print(" ACTIVITY 1: 8-PUZZLE SOLVER (A* COMPARISON)")
    print("-" * LINE_WIDTH)
    initial_8puzzle = (1, 2, 3, 0, 4, 6, 7, 5, 8)
    print("Initial State:\n  1 2 3\n  0 4 6\n  7 5 8")
    is_solv = is_solvable_8puzzle(initial_8puzzle)
    print(f"Solvability Check (Inversions): {is_solv}")

    res_h1 = solve_8puzzle_astar(
        initial_8puzzle, heuristic_misplaced, "Misplaced"
    )
    res_h2 = solve_8puzzle_astar(
        initial_8puzzle, heuristic_manhattan, "Manhattan"
    )
    print("\nHeuristic 1 (Misplaced Tiles):")
    print_result(res_h1)
    print("Heuristic 2 (Manhattan Distance):")
    print_result(res_h2)

    # 2. Graph Traversal
    print("-" * LINE_WIDTH)
    print(" ACTIVITY 2: GRAPH TRAVERSAL (BFS VS DFS)")
    print("-" * LINE_WIDTH)
    res_bfs = bfs_graph(SAMPLE_GRAPH, "A", "H")
    res_dfs = dfs_graph(SAMPLE_GRAPH, "A", "H")
    print_result(res_bfs)
    print_result(res_dfs)

    # 3. Maze Solver & Robot Navigation
    print("-" * LINE_WIDTH)
    print(" ACTIVITY 3: MAZE SOLVER & ROBOT NAVIGATION (A*)")
    print("-" * LINE_WIDTH)
    start_maze, goal_maze = (0, 0), (7, 7)
    res_maze = solve_maze_astar(SAMPLE_MAZE, start_maze, goal_maze)
    print_result(res_maze)

    # 4. Route Planning (GPS Route Planner)
    print("-" * LINE_WIDTH)
    print(" ACTIVITY 4: GPS ROUTE PLANNER (ARAD -> BUCHAREST)")
    print("-" * LINE_WIDTH)
    res_route_gbfs = solve_route_planner(
        ROADMAP, SLD_TO_BUCHAREST, "Arad", "Bucharest", "Greedy"
    )
    res_route_astar = solve_route_planner(
        ROADMAP, SLD_TO_BUCHAREST, "Arad", "Bucharest", "A*"
    )
    print_result(res_route_gbfs)
    print_result(res_route_astar)

    # Homework Analysis Table
    print_banner("HOMEWORK ANALYSIS: COMPARISON OF SEARCH ALGORITHMS")
    print(
        f"  {'Algorithm':<14} {'Domain':<20} {'Cost/Len':<10} "
        f"{'Expanded':<10} {'Generated':<11} {'Time (ms)':<10}"
    )
    print("  " + "-" * (LINE_WIDTH - 2))
    all_res = [
        res_h1,
        res_h2,
        res_bfs,
        res_dfs,
        res_maze,
        res_route_gbfs,
        res_route_astar,
    ]
    for r in all_res:
        print(
            f"  {r.algorithm:<14} {r.problem[:18]:<20} {r.cost:<10.1f} "
            f"{r.nodes_expanded:<10} {r.nodes_generated:<11} "
            f"{r.elapsed_ms:<10.3f}"
        )
    print()


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Lab 2 Search Algorithms Suite."
    )
    parser.add_argument(
        "--activity",
        choices=["all", "8puzzle", "graph", "maze", "route", "hill"],
        default="all",
        help="Select specific activity to run (default: all)",
    )
    args = parser.parse_args()

    if args.activity == "all":
        run_all_activities()
    elif args.activity == "8puzzle":
        state = (1, 2, 3, 0, 4, 6, 7, 5, 8)
        print_result(
            solve_8puzzle_astar(state, heuristic_manhattan, "Manhattan")
        )
    elif args.activity == "graph":
        print_result(bfs_graph(SAMPLE_GRAPH, "A", "H"))
        print_result(dfs_graph(SAMPLE_GRAPH, "A", "H"))
    elif args.activity == "maze":
        print_result(solve_maze_astar(SAMPLE_MAZE, (0, 0), (7, 7)))
    elif args.activity == "route":
        print_result(
            solve_route_planner(
                ROADMAP, SLD_TO_BUCHAREST, "Arad", "Bucharest", "A*"
            )
        )
    elif args.activity == "hill":
        print_banner("ACTIVITY 5: HILL CLIMBING")
        print_result(hill_climbing_maximize())

    return 0


if __name__ == "__main__":
    sys.exit(main())
