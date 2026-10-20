# Geospatial Disease Burden Dashboard

An interactive geospatial dashboard mapping disease burden across all 47 Kenya counties using real administrative shapefiles, spatial autocorrelation statistics, and LISA cluster detection.

---

## Live Demo
https://geospatial-disease-burden-38x4qkos76gggyzhwza4zc.streamlit.app

## Problem Statement

Disease burden in Kenya is not randomly distributed. Malaria clusters around Lake Victoria and the coast; cholera follows arid-region water insecurity; dengue is coastal. Public health planners need tools that reveal these spatial patterns, identify hotspot counties, and quantify the strength of geographic clustering so resources can be allocated where they matter most.

This project builds that tool: a fully interactive county-level dashboard combining choropleth mapping, Global Moran's I autocorrelation analysis, and Local Indicators of Spatial Association (LISA) cluster detection.

---

## Features

### County Shapefile Integration
Downloads Kenya's official 47-county administrative boundaries from the geoBoundaries open dataset. Boundaries are cached locally as a GeoPackage for offline use.

### Synthetic Disease Burden Data
Generates realistic county-level disease rates (per 100,000 population) for malaria, cholera, dengue, and measles with geographic patterns matching known epidemiological distributions in Kenya. An overall burden score aggregates all four diseases.

### Global Moran's I
Quantifies the degree of spatial clustering for each disease indicator across all 47 counties. Values above 0 indicate that high-burden counties tend to neighbor other high-burden counties. All five indicators in this dataset are statistically significant (p less than 0.05).

### LISA Cluster Detection
Classifies every county into one of four spatial cluster types using Local Moran's I:
- HH (Hotspot): high burden surrounded by high burden neighbors
- LL (Cold spot): low burden surrounded by low burden neighbors
- HL (High outlier): high burden surrounded by low burden neighbors
- LH (Low outlier): low burden surrounded by high burden neighbors

### Interactive Maps
Two side-by-side Folium maps: a choropleth coloured by the selected disease indicator and a LISA cluster map showing spatial cluster classification for each county. Both support zoom, pan, and hover tooltips.

### Ranked Bar Chart
Top N counties by any selected indicator, with a slider to adjust N from 5 to 47.

---

## Tech Stack

| Layer | Tool |
|---|---|
| Geospatial data | GeoPandas, Shapely |
| Spatial statistics | libpysal, esda (PySAL ecosystem) |
| Interactive maps | Folium, streamlit-folium |
| Dashboard | Streamlit |
| Charts | Plotly Express |
| Shapefile source | geoBoundaries |

---

## Project Structure

```
geospatial-disease-burden/
├── app.py
├── requirements.txt
├── data/
└── src/
    ├── data_prep.py
    ├── spatial_analysis.py
    └── visualisation.py
```


---

## Key Results

- Dengue shows the strongest spatial clustering (Moran's I = 0.633, p = 0.001)
- Siaya, Homa Bay, and Mombasa are the top three burden counties
- 3 hotspot counties and 12 cold spot counties identified by LISA
- All five disease indicators show statistically significant spatial autocorrelation

---

## Author

**Amos Mwaura**
ZENIK.AI | Healthcare AI Engineering
mwauramos.n@gmail.com
