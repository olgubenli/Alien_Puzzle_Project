# Alien Puzzle Project - Notebooks Section

**Project Abstract**

The Alien Puzzle Project represents a comprehensive computational study aimed at determining optimal interplanetary trajectories within the Solar System, focusing on a specific set of target asteroids (e.g., (55701) Ukalegon, (84011) Jean-Claude). This research employs advanced graph theory algorithms (Dijkstra), physical orbital parameter analysis (Tisserand's Parameter, Inclination, Eccentricity), and large-scale data visualization to validate the feasibility of "multi-hop" asteroid transfers.

The core objective is to minimize the total delta-v cost and transfer time by utilizing "transit hubs"—intermediary asteroids that facilitate lower-energy transfers between the Earth and the outer solar system main belt targets. The codebases provided herein document the entire lifecycle of this project: from initial data acquisition and cleaning, through the core optimization engine, to the final statistical validation and 3D visualization of the proposed routes.

---

## Detailed Notebook Guide

These notebooks serve as a documented archive of the project's source code, organized by scientific workflow stage.

### [01_Data_Acquisition.ipynb](./01_Data_Acquisition.ipynb)
**Purpose:** Establishes the foundational data layer. This notebook documents how raw orbital data is retrieved, filtered, and structured into the project's primary database.
*   **vericekme.py**: The primary interface script for querying external orbital databases (JPL/MPC) and fetching state vectors.
*   **fullasteroiddb20590.py**: Aggregates the fetched data into a unified, high-performance in-memory dictionary structure.
*   **harddbtestdata.py / harddbtestdata2.py**: Generates synthetic and subset datasets for unit testing the database integrity under different load conditions.
*   **ikieksikcisimveriler.py**: A supplemental script handling the injection of specific "missing" celestial bodies that were not captured in the initial bulk scan.
*   **20590eslesme.py**: Defines the preliminary logic for identifying potential asteroid pairs based on orbital resonance criteria.

### [02_Route_Analysis_and_Optimization.ipynb](./02_Route_Analysis_and_Optimization.ipynb)
**Purpose:** The algorithmic heart of the project. It details the graph construction, cost function definitions, and the execution of the pathfinding algorithms.
*   **yenimatrisgunceldb.py**: Defines the weighted graph structure where nodes are asteroids and edges represent transfer costs. Implements the core Dijkstra algorithm.
*   **anayolyanyoltop10.py**: A comparative analysis script that evaluates "Main Line" (direct) vs. "Side Line" (multi-hop) trajectories to identify top-tier transit hubs.
*   **icbaglantilarladuraklar.py**: Specifically analyzes the internal connectivity between secondary ("Hub") and tertiary ("Spoke") nodes, calculating "free-flight" costs.
*   **equjmesafeler.py**: A specialized calculator for computing Euclidean distances between bodies with specific string patterns (E-Q / U-J) in their designations.
*   **k7top5icin.py**: Implements an iterative pruning mechanism to discover the Top 5 distinct routes by finding and effectively removing the "best" path to reveal alternatives.
*   **kontrol56top20icin.py**: An extended "Deep Search" variation of the pruning algorithm, hunting for the Top 20 viable routes for robust stress testing.

### [03_Global_Statistical_Visualization.ipynb](./03_Global_Statistical_Visualization.ipynb)
**Purpose:** Provides the "Proof of Work" through statistical rigor. This notebook contains the plotting libraries used to verify that the selected routes are statistically significant anomalies and not random variance.
*   **yenigrafik49.py**: The master plotting suite, generating presence matrices and multi-variable scatter plots for the entire dataset.
*   **yenigrafik50.py**: The updated plotting engine (v50) featuring refined color palettes and publication-ready formatting logic.
*   **piegrafik18.py**: Visualize the temporal distribution of repeat counts/matches across 1-day, 10-day, and 100-day windows.
*   **bigpie20590grafik6.py**: A specialized "Anomaly vs. Noise" pie chart, contrasting the "Top 8 Pearls" (high-value targets) against the background "Ocean" data.
*   **violingrafik.py**: Generates Violin plots to statistically compare physical parameters (a, e, i) between the "Target Group" and the "Control Group".
*   **historgram1bucuk.py**: A log-scale histogram displaying the deviation metrics, highlighting the outlier status of the optimal routes.

### [04_Route_Visualization_and_Validation.ipynb](./04_Route_Visualization_and_Validation.ipynb)
**Purpose:** Validates the results in a simulated physical space. It includes scripts for 3D reconstruction and network topology stress testing.
*   **3dgrafik31.py**: Generates 3D plots of the solar system, rendering the calculated transfer orbits and asteroid positions at specific epochs.
*   **networkgrafikhat5.py**: visualizes the abstract network topology using NetworkX, emphasizing the centrality of key bridge nodes.
*   **dunyadanmesafe.py**: A validation script that cross-checks the calculated distances against Earth-relative observational data for the target date (1977-08-15).
*   **sonuckontrol.py**: An independent "double-check" script that re-calculates optimal paths using a separate logic flow to ensure determinism.
*   **strestestison6.py**: Simulates network failures (node removal, edge cost increases) to test the robustness and resiliency of the proposed transport web.

---

## Usage Warning

> **IMPORTANT: Source Code Reference Only**
>
> These notebooks are designed as **static reference documents**. They contain the raw Python source code for the Alien Puzzle Project's various modules embedded within Markdown cells.
>
> *   **Do NOT attempt to "Run All"**: The cells contain raw Python scripts that may depend on local file paths, specific database connections, or external environment variables not present in this notebook environment.
> *   **Intended Use**: Use these notebooks to read, review, and understand the logic and structure of the underlying codebase in a literate programming format.

## Requirements

To run the source scripts contained within these references in a proper Python environment, the following dependencies are required:

*   Python 3.8+
*   `numpy`
*   `pandas`
*   `matplotlib`
*   `seaborn`
*   `networkx`
*   `scipy`
*   `sqlite3` (Standard library)
