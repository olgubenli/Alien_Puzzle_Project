# Source Code Directory (`src`)

This directory contains the flat-file collection of all Python scripts driving the Alien Puzzle Project. While the structure is flat for simplicity, the files are logically organized into the following categories:

## 1. Data Acquisition Scripts
*Tools for fetching, cleaning, and structuring the raw astronomical data.*

*   **`vericekme.py`**: The primary data retrieval script interfacing with external APIs (JPL/MPC) to fetch asteroid state vectors.
*   **`fullasteroiddb20590.py`**: Compiles the raw fetched data into the project's main in-memory dictionary database structure.
*   **`harddbtestdata.py`** & **`harddbtestdata2.py`**: Generators for synthetic and subset test datasets used to validate database integrity.
*   **`ikieksikcisimveriler.py`**: A patch script that injects specific celestial bodies missing from the initial bulk data scans.
*   **`20590eslesme.py`**: Pre-processing logic that defines the initial "match candidates" based on orbital resonance criteria.
*   **`bigpie20590veri.py`**: Contains the raw data structures used specifically for the "Big Pie" anomaly visualization.

## 2. Core Analysis Engines
*The heavy-lifting algorithms for graph construction, route optimization, and cost analysis.*

*   **`yenimatrisgunceldb.py`**: The central engine establishing the weighted graph and running the primary Dijkstra pathfinding algorithm.
*   **`anayolyanyoltop10.py`**: A comparative analysis script distinguishing between direct "Main Line" routes and multi-hop "Side Lines".
*   **`icbaglantilarladuraklar.py`**: Analyzes the "free-flight" transfer costs between secondary (Hub) and tertiary (Spoke) nodes.
*   **`k7top5icin.py`**: Implements an iterative pruning algorithm to discover the 2nd through 5th best alternative routes.
*   **`kontrol56top20icin.py`**: An extended deep-search variant hunting for the Top 20 viable routes for stress-testing purposes.
*   **`strestestison6.py`**: Simulation script that tests network resiliency by removing nodes or increasing costs.

## 3. Visualization Tools
*Modules for generating 2D and 3D plotting artifacts.*

*   **`yenigrafik49.py`**: The master plotting suite for generating presence matrices and general scatter plots.
*   **`yenigrafik50.py`**: The updated (v50) plotting engine with refined publication-quality aesthetics.
*   **`3dgrafik31.py`**: Generates interactive 3D visualizations of the solar system and calculated transfer orbits.
*   **`violingrafik.py`**: Creates Violin plots to compare the statistical distribution of orbital parameters.
*   **`piegrafik18.py`**: Generates pie charts showing the temporal distribution of asteroid repeat matches.
*   **`bigpie20590grafik6.py`**: Specialized visualization contrasting "Anomaly" vs. "Ocean" (noise) datasets.
*   **`historgram1bucuk.py`**: Log-scale histogram plotting the deviation metrics of the optimal routes.
*   **`networkgrafikhat5.py`**: Uses NetworkX to render the abstract topology of the transport graph.
*   **`dunyadanmesafe.py`**: Visualizes Earth-relative distances for the target epoch using bar charts.

## 4. Utilities & Helpers
*Verification scripts, math helpers, and build tools.*

*   **`equjmesafeler.py`**: Helper for computing Euclidean distances between bodies with specific string patterns (E-Q / U-J).
*   **`sonuckontrol.py`**: An independent "double-check" script ensuring the determinism of the calculated optimal paths.
*   **`anasonkontrol.py`**: Auxiliary validation script for checking specific signal integrity or formatting.
*   **`thereushedef6maliyet.py`**: A specialized utility for calculating costs to a specific target subset (Target #6).
*   **`auatlama.py`**: A utility script potentially used for specific AU (Astronomical Unit) distance checks or jumps.
*   **`3dgrafikveriler.py`**: Contains static data definitions used by the 3D visualization tools.
*   **`create_notebooks.py`**: The Python automation script for generating the project notebooks.
*   **`create_notebooks.ps1`**: The PowerShell fallback script for notebook generation.
*   **`create_scientific_notebooks.ps1`**: The advanced PowerShell script that generates the scientifically styled notebooks.
