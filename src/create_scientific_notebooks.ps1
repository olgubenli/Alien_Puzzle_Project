$notebooks = @{
    "01_Data_Acquisition.ipynb"                   = @{
        "Abstract" = "# 01. Data Acquisition and Database Construction`n`n**Abstract**`nThis notebook serves as the foundational layer of the Alien Puzzle Project. It documents the methodologies used for retrieving orbital elements, physical parameters, and potential route connections from the JPL Small-Body Database and other sources. The scripts herein establish the 'Source of Truth' database (`solar_system_analysis_with_distances.db`) used by subsequent optimization engines."
        "Files"    = @(
            @{"Name" = "vericekme.py"; "Desc" = "## Data Retrieval Script`nCore module for interfacing with external APIs to fetch orbital vectors and physical properties for the defined asteroid sets." },
            @{"Name" = "fullasteroiddb20590.py"; "Desc" = "## Full Database Compiler`nAggregates individual data points into a unified dictionary structure, forming the primary in-memory database." },
            @{"Name" = "harddbtestdata.py"; "Desc" = "## Test Dataset Generator (A)`nProvides a robust set of test cases to validate the database integrity under various 'k' parameter configurations." },
            @{"Name" = "harddbtestdata2.py"; "Desc" = "## Test Dataset Generator (B)`nSecondary test set reflecting edge cases and expanded asteroid clusters." },
            @{"Name" = "ikieksikcisimveriler.py"; "Desc" = "## Missing Body Supplement`nHandles the injection of specific celestial bodies that were absent or malformed in the initial bulk retrieval." },
            @{"Name" = "20590eslesme.py"; "Desc" = "## Match Logic Pre-processor`nDefines the initial matching logic to pair asteroids based on orbital resonances and physical characteristic similarity." }
        )
    }

    "02_Route_Analysis_and_Optimization.ipynb"    = @{
        "Abstract" = "# 02. Route Analysis and Optimization`n`n**Abstract**`nThis module implements the algorithmic core of the project. Using the data prepared in Notebook 01, we apply Dijkstra's algorithm and custom cost functions to determine the optimal interplanetary trajectories. The code covers 'k=7' pruning strategies, 'hub-and-spoke' transit analysis, and the 'Final Physical Model' cost verification."
        "Files"    = @(
            @{"Name" = "yenimatrisgunceldb.py"; "Desc" = "## Core Matrix Engine`nThe central processing unit for the route optimization graph. Defines the weighted graph structure and Dijkstra implementation." },
            @{"Name" = "anayolyanyoltop10.py"; "Desc" = "## Primary vs. Secondary Route Analysis`nAnalyzes the trade-offs between 'Main Line' (direct) and 'Side Line' (multi-hop) trajectories, highlighting the Top 10 most efficient paths." },
            @{"Name" = "icbaglantilarladuraklar.py"; "Desc" = "## Hub Connection Analysis`nInvestigates the internal connectivity between '2nd Stop' (Hub) and '3rd Stop' (Spoke) nodes, calculating free-flight transfer costs." },
            @{"Name" = "equjmesafeler.py"; "Desc" = "## E-Q / U-J Distance Calculator`nSpecialized utility for computing the Euclidean distances between specific 'Key' asteroid pairs (E-Q and U-J strings)." },
            @{"Name" = "k7top5icin.py"; "Desc" = "## Top 5 Route Pruning (k=7)`nImplements an iterative pruning algorithm to discover the 2nd, 3rd, 4th, and 5th best routes by removing optimal nodes sequentially." },
            @{"Name" = "kontrol56top20icin.py"; "Desc" = "## Top 20 Deep Search (k=7)`nAn extended variation of the Top 5 analysis, performing a deep-dive search for the Top 20 viable routes for stress testing." }
        )
    }

    "03_Global_Statistical_Visualization.ipynb"   = @{
        "Abstract" = "# 03. Global Statistical Visualization`n`n**Abstract**`nStatistical rigor is essential for validating the significance of the discovered routes. This notebook presents a comprehensive suite of visualization tools, ranging from Violin plots comparing orbital parameters to Pie charts illustrating class distributions. These visualizations provide the 'Proof of Work' for the anomaly detection algorithms."
        "Files"    = @(
            @{"Name" = "yenigrafik49.py"; "Desc" = "## Master Plotting Suite`nThe primary visualization library, capable of generating presence matrices and multi-variable scatter plots." },
            @{"Name" = "yenigrafik50.py"; "Desc" = "## Updated Plotting Logic (v50)`nRefined plotting routines with enhanced color palettes and label placement algorithms for publication-ready figures." },
            @{"Name" = "piegrafik18.py"; "Desc" = "## Distribution Pie Charts`nVisualizes the distribution of repeat counts across varying time windows (1-day, 10-day, 100-day)." },
            @{"Name" = "bigpie20590grafik6.py"; "Desc" = "## Anomaly Comparison Chart`nA specialized visualization contrasting the 'Top 8 Pearls' (Anomalies) against the background 'Ocean' (Noise) data." },
            @{"Name" = "violingrafik.py"; "Desc" = "## Orbital Parameter Violin Plots`nStatistical comparison of Semi-major Axis, Eccentricity, and Inclination between Subject and Control groups." },
            @{"Name" = "historgram1bucuk.py"; "Desc" = "## Deviation Histogram`nLog-scale histogram displaying the deviation metrics, highlighting the statistical outlier status of the selected routes." }
        )
    }

    "04_Route_Visualization_and_Validation.ipynb" = @{
        "Abstract" = "# 04. Route Visualization and Validation`n`n**Abstract**`nThe final validation step involves 3D spatial reconstruction and network resiliency testing. This notebook contains the scripts used to generate 3D orbital diagrams, network graph topologies, and stress-test reports, confirming the physical viability of the optimized paths in a simulated 3D space."
        "Files"    = @(
            @{"Name" = "3dgrafik31.py"; "Desc" = "## 3D Orbital Visualization`nGenerates interactable (or static projection) 3D plots of the solar system, drawing the calculated transfer orbits." },
            @{"Name" = "networkgrafikhat5.py"; "Desc" = "## Network Topology Graph`nUses NetworkX to visualize the abstract connectivity graph, emphasizing 'Bridge' nodes and 'Hub' centrality." },
            @{"Name" = "dunyadanmesafe.py"; "Desc" = "## Earth-Relative Distance Check`nValidates the calculated distances against Earth-relative observational data for the target epoch (1977)." },
            @{"Name" = "sonuckontrol.py"; "Desc" = "## Final Result Validator`nA standalone script that re-runs the optimal paths through an independent verification logic to ensure result determinism." },
            @{"Name" = "strestestison6.py"; "Desc" = "## Network Stress Test`nSimulates node failures and varying 'k' parameters to test the resiliency and robustness of the proposed transport network." },
            @{"Name" = "anasonkontrol.py"; "Desc" = "## Anason Control Script`n(If present) Auxiliary validation checks for specific signal patterns." }
        )
    }
}

$srcDir = Get-Location
$outDir = Join-Path (Get-Item $srcDir).Parent.FullName "notebooks"

# Ensure output directory exists
if (-not (Test-Path $outDir)) {
    New-Item -ItemType Directory -Path $outDir | Out-Null
}

foreach ($nbName in $notebooks.Keys) {
    Write-Host "Processing $nbName..."
    $nbData = $notebooks[$nbName]
    $cells = @()
    
    # 1. Abstract / Introduction Cell
    $cells += @{
        "cell_type" = "markdown"
        "metadata"  = @{}
        "source"    = @($nbData["Abstract"])
    }

    # 2. Process Files
    foreach ($fileData in $nbData["Files"]) {
        $fileName = $fileData["Name"]
        $fileDesc = $fileData["Desc"]
        
        $path = Join-Path $srcDir $fileName
        
        if (Test-Path $path) {
            # Read raw content
            try {
                $content = Get-Content $path -Encoding UTF8 -Raw -ErrorAction Stop
                
                # Create Description Cell
                $cells += @{
                    "cell_type" = "markdown"
                    "metadata"  = @{}
                    "source"    = @($fileDesc)
                }

                # Create Code Cell
                $lines = $content -split "`r`n|`r|`n"
                $cells += @{
                    "cell_type"       = "code"
                    "execution_count" = $null
                    "metadata"        = @{ "collapsed" = $true }
                    "outputs"         = @()
                    "source"          = $lines
                }
                
            }
            catch {
                Write-Host "Error reading $fileName : $_"
            }
        }
        else {
            Write-Host "Warning: File not found: $fileName"
            # Optional: Add a placeholder saying file is missing?
            # For now, we skip or add a note.
            if ($fileName -ne "anasonkontrol.py") {
                # anasonkontrol might be missing, optional
                $cells += @{
                    "cell_type" = "markdown"
                    "metadata"  = @{}
                    "source"    = @("## $fileName (MISSING)`nFile was expected but not found in the source directory.")
                }
            }
        }
    }
    
    # Construct Notebook JSON
    $nbContent = @{
        "cells"          = $cells
        "metadata"       = @{
            "kernelspec"    = @{
                "display_name" = "Python 3"
                "language"     = "python"
                "name"         = "python3"
            }
            "language_info" = @{
                "codemirror_mode"    = @{
                    "name"    = "ipython"
                    "version" = 3
                }
                "file_extension"     = ".py"
                "mimetype"           = "text/x-python"
                "name"               = "python"
                "nbconvert_exporter" = "python"
                "pygments_lexer"     = "ipython3"
                "version"            = "3.8.5"
            }
        }
        "nbformat"       = 4
        "nbformat_minor" = 4
    }
    
    # Convert and Save
    $json = $nbContent | ConvertTo-Json -Depth 100
    $outPath = Join-Path $outDir $nbName
    $json | Set-Content $outPath -Encoding UTF8
    Write-Host "Created $outPath"
}
