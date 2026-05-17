# Kolkata Land Cover Classification & Analysis Pipeline

An automated geospatial data science workflow designed to process, analyze, and visualize multi-temporal land cover dynamics across the Kolkata metropolitan region between **2016 and 2022**. This project combines programmatic raster processing using Python with desktop GIS mapping environments to evaluate urban sprawl and environmental transitions.

---

## Tech Stack & Core Libraries
* **GIS Environment:** QGIS 3.x (Workspace layout and vector management)
* **Data Engineering:** `rasterio` (Geospatial raster I/O), `numpy` (Array-based grid manipulation)
* **Analysis & Pipeline:** Jupyter Notebook (`finalproject.ipynb`)
* **Interactive Visualization:** Leaflet-based HTML map rendering for web deployments

---

##  Repository Structure

The project directory is structured clean and decoupled to separate raw imagery assets, vector shapes, processing logic, and standalone interactive web deployments:

```text
LANDCLASSIFICATION/
│
├── data/
│   ├── raster/
│   │   ├── Kolkata_LC_2016.tif    # GeoTIFF classified land cover layer (2016)
│   │   └── Kolkata_LC_2022.tif    # GeoTIFF classified land cover layer (2022)
│   │
│   └── vector/
│       ├── 2022.shp               # Shapefile geometry for region of interest boundaries
│       ├── 2022.dbf               # Attribute classification tables
│       ├── 2022.prj               # CRS & Projection configuration details
│       └── 2022.shx               # Positional index format
│
├── notebooks/
│   └── finalproject.ipynb         # Pipeline engine for processing, area calculations, and export logic
│
├── outputs/
│   ├── 2016.html                  # Interactive standalone web visualization map (2016)
│   ├── 2022.html                  # Interactive standalone web visualization map (2022)
│   └── OUTPUT_HTML_FILE.html      # Comprehensive comparative layout map
│
├── .gitignore                     # Filter rules to exclude local GIS metadata (*.aux.xml)
└── project.qgz                    # QGIS desktop integration project workspace file