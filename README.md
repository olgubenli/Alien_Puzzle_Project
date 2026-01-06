# Alien Puzzle Project: Orbital Resonance & Trajectory Analysis


## Publication

This repository contains the official implementation and supplementary data for the paper:
**"The 'Hidden Highway' Hypothesis: Statistical Anomalies within the 6EQ=5UJ Formula as Navigational Markers"**

You can access the full paper and technical report here: 
👉 [https://doi.org/10.5281/zenodo.18160688](https://doi.org/10.5281/zenodo.18160688)

### Citation
If you use this code or hypothesis in your research, please cite it as:
> Benli, T. O. (2026). The "Hidden Highway" Hypothesis: Statistical Anomalies within the 6EQ=5UJ Formula as Navigational Markers (Version 1.0.0). Zenodo. https://doi.org/10.5281/zenodo.18160688


## Overview
This project presents a comprehensive computational study on Solar System dynamics, focusing on the statistical analysis of orbital mechanics and trajectory optimization for interplanetary travel. By leveraging high-precision data from NASA/JPL Horizons and other astronomical databases, we analyze the distribution and resonance patterns of asteroids and major bodies. The project further implements advanced algorithms to calculate optimal transfer routes, minimizing energy consumption (delta-v) and travel time, effectively solving complex "puzzles" of celestial navigation.

## Repository Structure

- **`src/`**: Contains the core Python scripts and analysis modules for data processing, resonance calculations, and trajectory optimization algorithms.
- **`notebooks/`**: Interactive Jupyter Notebooks providing a step-by-step reproduction of the study, from raw data acquisition to final visualizations.
- **`data/`**: Stores database files (`.db`, `.json`, `.txt`) and raw datasets used in the analysis. 
  > **Note**: Large database files (e.g., `solar_system_analysis_with_distances.db`) are excluded from this repository via `.gitignore` due to size constraints.
- **`docs/`**: Supplementary documentation, theoretical background references, and project reports.

## Data Sources
We gratefully acknowledge the following data providers for enabling this research:
- **NASA/JPL Horizons System**: For high-precision ephemerides and orbital elements.
- **SBDB (Small-Body Database) API**: For physical parameters of asteroids and comets.
- **Minor Planet Center (MPC)**: For observational data of minor bodies.
- **Le Système Solaire**: For planetary system data APIs.

## Installation
To reproduce the analysis environment, install the required Python dependencies:

```bash
pip install -r requirements.txt
```

## License
This project is licensed under the [MIT License](LICENSE).
