# 🚗 Rush Hour Puzzle Solver (Python + BFS / A\*)

This project implements a complete solver for the classic **Rush Hour**
puzzle using two search algorithms: - **Breadth-First Search (BFS)** -
**A\* Search with a custom heuristic**

It also includes a **Pygame animation** that visualizes each movement of
the solution.

------------------------------------------------------------------------

## 📌 Features

-   Load Rush Hour puzzles from CSV files\
-   Validate board dimensions and vehicle positions\
-   Solve puzzles using BFS or A\*\
-   Heuristic for A\*:
    -   Distance of the target car to the exit\
    -   Number of blocking vehicles\
-   Pygame animation showing each move\
-   Fully object-oriented Python implementation

------------------------------------------------------------------------

## 📁 Project Structure

    rush-hour-solver/
    │
    ├── src/
    │   └── rush_hour.py
    │
    ├── examples/
    │   ├── easy1.csv
    │   ├── ...
    │
    ├── requirements.txt
    ├── README.md
    └── .gitignore

------------------------------------------------------------------------

## ▶️ Installation

Install the dependencies:

``` bash
pip install -r requirements.txt
```

**requirements.txt**

    pygame

**.gitignore** (recommended)

    __pycache__/
    *.pyc
    .vscode/
    .idea/

------------------------------------------------------------------------

## ▶️ Usage

Run the solver:

``` bash
python src/rush_hour.py
```

You will be asked to:

1.  Select a CSV puzzle from the `examples/` folder\
2.  Choose an algorithm: `bfs` or `a*`

A solution summary is printed in the terminal, followed by a Pygame
animation.

------------------------------------------------------------------------

## 📄 CSV Puzzle Format

Each puzzle CSV file must follow this structure:

    height,width
    id,x,y,orientation,length

Example:

    6,6
    X,1,2,H,2
    A,0,0,V,3
    B,3,1,H,2

Where:

-   **id**: vehicle label\
-   **x,y**: top-left coordinates (0-indexed)\
-   **orientation**: `H` (horizontal) or `V` (vertical)\
-   **length**: number of grid cells

------------------------------------------------------------------------

## 🎮 Pygame Animation

-   The red car (`X`) is the target car.\
-   Blue cars represent the blocking vehicles.\
-   Smooth transition between moves.\
-   The total number of moves is displayed at the end.

------------------------------------------------------------------------

## 🧠 Algorithms

### **BFS**

-   Explores all states level-by-level\
-   Always finds the shortest path\
-   Slower for large puzzles

### **A\***

-   Uses a heuristic (distance + blockers)\
-   Much faster and more efficient\
-   Ideal for medium and large board configurations

------------------------------------------------------------------------

------------------------------------------------------------------------

## 👤 Author

**Mohamed Amine Sellami**\
Full-Stack Developer & Visual Computing Master's student.

------------------------------------------------------------------------

## 🔗 Local uploaded script (for reference)

    /mnt/data/7b53910b-78ce-496e-a6c1-53e6cf17876a.py
