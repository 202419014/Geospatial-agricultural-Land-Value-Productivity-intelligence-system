# AgriLand Value Intelligence System
*Geospatial Agricultural Land Valuation — Ludhiana District, Punjab*

**Project Writeup | Submitted: April 01, 2026**

**Group Members:** [Member 1] | [Member 2] | [Member 3] | [Member 4]

---

## 1. Problem Statement

Agricultural land valuation in India — particularly in Punjab's Ludhiana District — is largely informal, opaque, and inconsistent. Farmers rely on word-of-mouth or local brokers to price their land, while buyers have no data-driven way to assess fair market value. This information asymmetry leads to exploitative transactions, undervaluation of productive farmland, and poor investment decisions.

This project addresses that gap by building an AI-powered geospatial platform that combines real soil quality data, irrigation coverage, and proximity to APMC mandis (agricultural markets) to predict land values using a trained Random Forest model. The result is a transparent, evidence-based valuation tool accessible to both farmers and buyers.

---

## 2. Logic Flow

### 2.1 Authentication Flow

The application uses a simulated OTP-based login system. When a user enters their 10-digit mobile number, a 6-digit OTP is generated (displayed on screen in demo mode). After OTP verification, new users complete a profile by entering their name and selecting a role (Farmer or Buyer). Returning users are recognized by phone number lookup and redirected immediately to their dashboard. User records are stored in session state.

### 2.2 Data Loading Pipeline

On startup, the application loads three types of geospatial data through the `data_loader` module:

- GeoJSON files for 36 land parcels and mandi locations (loaded via GeoPandas)
- CSV file of APMC market coordinates (loaded via Pandas, converted to GeoDataFrame)
- Raster `.tif` files for soil properties — clay, sand, silt, pH, organic carbon, nitrogen (loaded via Rasterio)

### 2.3 Feature Extraction

For each land parcel, spatial features are computed by the `feature_extraction` module:

- Soil values are sampled at the parcel centroid from each raster layer using Rasterio's `sample()` method
- Market proximity is computed as the minimum Haversine distance from the parcel centroid to all APMC/mandi market points
- Additional binary features include canal irrigation access and highway proximity

### 2.4 Machine Learning Model

A Random Forest Regressor (scikit-learn) is trained on the 36-parcel dataset using the extracted features. Key design decisions:

- **Feature set:** soil clay%, sand%, silt%, pH, organic carbon, nitrogen, market distance (km), irrigation binary, area (acres)
- **Target variable:** land value in INR per acre
- Model is trained once and cached to `rf_model.pkl` to avoid re-training on every page load
- Streamlit's `@st.cache_resource` decorator ensures the model is loaded only once per session
- Feature importance scores are extracted and displayed to explain each prediction

### 2.5 GUI Interaction Flow

**Farmer view:** The user can draw a custom parcel boundary on the Folium map using Leaflet Draw controls. The drawn polygon's centroid is computed, soil features are sampled from that point, market distance is calculated, and the trained model returns a price estimate with a feature importance bar chart.

**Buyer view:** The user sees all 36 parcels color-coded by value tier on the Folium map. Clicking a parcel opens a popup with full details. A filterable summary table below the map allows sorting and searching across all parcels.

---

## 3. GUI & Advanced Components

### 3.1 Streamlit Framework

The application uses Streamlit as its web framework. The entire UI is driven by Python — no HTML/CSS files are needed beyond inline injection. Streamlit's reactive model means the UI automatically re-renders when session state changes (e.g., after login, after parcel drawing). `st.set_page_config()` sets the page title, icon, and wide layout.

### 3.2 Custom CSS Theming

The app features a fully custom dark agricultural theme injected via `st.markdown()` with `unsafe_allow_html=True`. Key UI elements styled include: animated gradient background, golden wheat color palette, custom input fields, buttons with hover effects, metric cards, tab bars, sidebar, and a scrollbar. An animated SVG layer shows a tractor crossing a wheat field, and six real farmland photographs crossfade in the background using CSS animations.

### 3.3 Folium Interactive Map

The core visualization is built using Folium, a Python library that generates Leaflet.js maps. The `map_builder` module constructs:

- Choropleth-style parcel polygons color-coded by value (green = low, red = high)
- Custom popup HTML for each parcel showing price, soil grade, irrigation status, and market distance
- Leaflet Draw plugin enabling users to draw their own polygon boundaries
- Mandi marker layer with custom icons indicating market locations

The map is embedded inside Streamlit using the `streamlit-folium` component (`st_folium()`), which returns the last drawn shape as a Python dictionary that drives the prediction pipeline.

### 3.4 Role-Based Dashboard

After login, users are routed to different dashboard modules (`farmer_page.py` or `buyer_page.py`) based on their registered role. This separation ensures the feature set shown to a farmer (draw + predict) differs from what a buyer sees (explore + compare). Role data is persisted in session state and retrieved by `get_user()` from the auth module.

### 3.5 OTP Authentication Module

The auth module (`src/utils/auth.py`) implements a stateful three-step login: phone entry, OTP verification, and profile completion. OTPs are stored in session state with a timestamp for expiry checking. The `is_registered()` function checks whether a phone number has an existing user record, allowing returning users to skip registration.

---

## 4. Contribution Table

| **Module / File** | **Responsibility** | **Built By** |
|---|---|---|
| `main.py` | App entry point, session state, OTP auth UI, login flow | Member 1 |
| `src/utils/auth.py` | OTP generation, user registration, verification logic | Member 1 |
| `src/gui/map_builder.py` | Folium map, parcel polygons, popup HTML, Draw plugin | Member 2 |
| `src/gui/farmer_page.py` | Farmer dashboard, draw-to-predict workflow, UI layout | Member 2 |
| `src/gui/buyer_page.py` | Buyer dashboard, parcel explorer, filter table | Member 3 |
| `src/logic/model.py` | Random Forest training, prediction, feature importance | Member 3 |
| `src/utils/data_loader.py` | GeoJSON, CSV, raster data loading with GeoPandas/Rasterio | Member 4 |
| `src/utils/feature_extraction.py` | Soil raster sampling, market distance computation | Member 4 |
| `data/` (dataset curation) | GeoJSON parcels, APMC CSV, soil raster preparation | All Members |
| `README.md` & Documentation | Installation guide, folder structure, usage docs | Member 1 |

> *Note: All team members contributed to testing, debugging, and the final presentation preparation. The contribution table reflects primary module ownership.*

---

## 5. Library Choice Justification

| **Library** | **Why We Chose It** |
|---|---|
| Streamlit | Fastest Python-native web framework for data apps. No JavaScript required. Built-in widgets, caching, and session state. |
| Folium | Best Python wrapper for Leaflet.js. Supports GeoJSON overlays, draw plugins, custom popups, and choropleth — all needed for this project. |
| streamlit-folium | The only production-ready bridge between Folium and Streamlit that returns user-drawn shapes as Python objects. |
| GeoPandas | Extends Pandas to handle geospatial data natively. Handles CRS transformations, spatial joins, and GeoJSON I/O cleanly. |
| scikit-learn | Industry-standard ML library. Random Forest is well-suited for tabular data with mixed feature types and small datasets. |
| Rasterio | Gold standard for reading geospatial raster files (`.tif`). Efficient point sampling without loading full raster into memory. |
| Shapely | Geometry operations (centroid, distance, polygon containment) required for spatial feature computation. |

---

*AgriLand Value Intelligence | Group Project Writeup | April 2026*
