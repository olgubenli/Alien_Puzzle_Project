# Revision analyses (November 2026)

This folder contains the scripts, tables and figures added during the revision of the manuscript
"The 'Hidden Highway' Hypothesis" (JBIS). The Supplementary Material is in
`docs/Hidden_Highway_Supplementary_2026-11.pdf`.

## Contents

| Path | Content |
|---|---|
| `analysis/01_h1_dogrulama.py` – `03_tarayici_saglama.py` | Re-computation of the Hypothesis 1 result and checks of the matching code |
| `analysis/04_111gun/` | 111-epoch analysis (Hypothesis 1): matches, KDE, DBSCAN, rolling mean, regression; figures for every reading |
| `analysis/05_h2/` | Hypothesis 2: deviation distribution, elbow analysis, Top 8, Methods A and B; figures for every reading |
| `analysis/06_h3/` | Hypothesis 3: gateway selection, cost matrix, Dijkstra routes, stress test, routes to 32532 Thereus |
| `analysis/07_profil/` | Joint test of the three criteria (A–C); `kapi_tj.py` evaluates the gateway criterion |
| `analysis/08_thereus_tarihleri/` | Recurrence of the Thereus solution, 1950–2100 (Fig. S30) |
| `analysis/09_S2/`, `analysis/10_dogrulama/` | Section 7 document builder and final consistency checks |
| `analysis/*/cikti/formuller/` | Per-reading figures (PNG) and tables (XLSX) for the adopted reading ("Ref") and the 20 alternative parsings (F1–F10 and their absolute-value forms) |
| `analysis/*/cikti/karsilastirma_EN/` | Comparison panels of all readings for each figure type |
| `random_readings/faz3_formuller.py` | Generator of the 1,000 random readings (fixed seed 2026) |
| `random_readings/faz3_calistir.py`, `faz3_analiz.py` | Evaluation of the random readings |
| `random_readings/faz3_sonuclar/formuller.json` | The list of 1,000 random readings |
| `random_readings/faz3_sonuclar/faz3_ham.csv`, `faz3_ozet.json` | Raw and summary results for the random readings |
| `Supplementary_Material_Section7_tables.xlsx` | All tables of Section 7 of the Supplementary Material |

## Notes

- File and folder names are partly in Turkish (`analiz` = analysis, `cikti` = output, `formuller` = formulas/readings,
  `karsilastirma` = comparison, `kapi` = gateway, `dogrulama` = verification).
- The ephemeris and orbital data (NASA/JPL Horizons, SBDB, MPC) are not included because of their size; the
  scripts read them from the local data folders defined in `analysis/ortak.py`, which must be adapted before running.
- All values refer to the epoch 1977-08-15 00:00 UT unless stated otherwise.
