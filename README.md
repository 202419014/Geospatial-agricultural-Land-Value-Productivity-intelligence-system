#  AgriLand Value Intelligence System
### Geospatial Agricultural Land Value & Productivity Intelligence — Ludhiana District, Punjab

> AI-powered land valuation platform built with Streamlit, Random Forest ML, Folium maps, and real geospatial data from SoilGrids & APMC market datasets.

---

##  What This Tool Does

AgriLand Value Intelligence helps **farmers** and **land buyers** in Ludhiana District, Punjab assess and explore agricultural land prices using machine learning. Users log in via OTP, select their role (Farmer / Buyer), and access an interactive map of 36+ land parcels with ML-predicted valuations based on real soil and market data.

**Key capabilities:**
-  Interactive Folium map — click any parcel to see price, soil quality, and market proximity
-  Draw your own parcel boundary and get an instant ML price estimate
-  Soil feature extraction (clay, sand, silt, pH, organic carbon, nitrogen) from raster data
-  Market proximity scoring using APMC mandi locations
-  Random Forest model with feature importance explanations
-  Filterable summary table of all land parcels

---

##  Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/202419014/Geospatial-agricultural-Land-Value-Productivity-intelligence-system.git
cd Geospatial-agricultural-Land-Value-Productivity-intelligence-system
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

>  Requires Python 3.9+. It is strongly recommended to use a virtual environment:
> ```bash
> python -m venv venv
> source venv/bin/activate        # macOS/Linux
> venv\Scripts\activate           # Windows
> pip install -r requirements.txt
> ```

### 3. Run the App
```bash
streamlit run main.py
```

The app will open automatically at **http://localhost:8501**

### 4. Login (Demo Mode)
- Enter any 10-digit mobile number (e.g. `9876543210`)
- Click **Send OTP** — the OTP will appear on screen (SMS disabled in demo)
- Enter the OTP and choose your role: **Farmer** or **Buyer**

---

##  Folder Structure

```
project-root/
│
├── main.py                            # Streamlit entry point & auth flow
│
├── src/
│   ├── gui/
│   │   ├── farmer_page.py             # Farmer dashboard (draw parcel, get prediction)
│   │   ├── buyer_page.py              # Buyer dashboard (explore map, compare parcels)
│   │   └── map_builder.py             # Folium map construction & popup HTML
│   │
│   ├── logic/
│   │   └── model.py                   # Random Forest training & prediction
│   │
│   └── utils/
│       ├── auth.py                    # OTP generation, user registration & verification
│       ├── data_loader.py             # GeoJSON / CSV / raster data loaders
│       └── feature_extraction.py     # Spatial feature computation (soil, market distance)
│
├── data/
│   ├── ludhiana_land_values.geojson   # 36 agricultural land parcels with attributes
│   ├── ludhiana_mandis.geojson        # Mandi market locations (GeoJSON)
│   ├── ludhiana_apmc_markets_lat_long.csv  # APMC market coordinates
│   ├── ludhiana_*.tif                 # Soil raster layers (SoilGrids)
│   └── rf_model.pkl                   # Pre-trained Random Forest (auto-generated on first run)
│
├── requirements.txt                   # Python dependencies
└── README.md                          # This file
```

---

##  Tech Stack & Libraries

| Library | Purpose |
|---|---|
| `streamlit` | Web UI framework |
| `streamlit-folium` | Embed Folium maps inside Streamlit |
| `folium` | Interactive Leaflet.js maps |
| `geopandas` | Geospatial data handling (GeoJSON, shapefiles) |
| `scikit-learn` | Random Forest ML model |
| `rasterio` | Read soil raster (.tif) files |
| `shapely` | Geometry operations (point-in-polygon, distance) |
| `pandas` / `numpy` | Data manipulation |

---

##  Sample Data

The `data/` folder contains a small ready-to-use dataset so instructors can run the tool immediately:

- **36 land regions** in Ludhiana District with price, soil type, irrigation status
- **APMC market locations** (CSV + GeoJSON) for proximity computation
- **Soil rasters** for clay, sand, silt, pH, organic carbon, nitrogen extraction

The Random Forest model (`rf_model.pkl`) is auto-generated on first run if not present.

---

##  Team Members

| Name | Role |
|---|---|
| D. Sushma | ML model development (Random Forest, feature engineering, tuning), Model evaluation and analysis |
| V. Jhaana Sreya | Geospatial processing (GeoPandas, Shapely, Rasterio), Data cleaning and feature preparation  |
| D. Sweta |Visualization integration and system integration, Documentation, README, presentation |
| B. Deepika |Streamlit GUI design and interaction handling, UI testing and refinement |


---

## 📄 License

This project was developed as an academic submission. All geospatial data is sourced from publicly available datasets (SoilGrids, data.gov.in).
