## Project Proposal (PGP) 
**Group Name** ***Agri Land Analytics*
Members: ** D. Sushma, D. Sweta, V. Jhaana Sreya, B. Deepika
## Project Title
**Geospatial Agricultural Land Value & Productivity Intelligence System**

# Problem Statement
## Spatial Problem
In most rural and semi-urban regions of India, agricultural land is valued through informal, subjective estimation rather than any systematic spatial analysis. Factors like soil quality, access to irrigation, proximity to mandis or APMC markets, and connectivity to road networks have a significant bearing on land productivity — and therefore on value — but these factors are rarely quantified together in a single tool accessible to non-technical users.

## Target Users
The system is designed for:
- Farmers
- Landowners
- Agricultural planners
- Land investors
- Government policy analysts

# 2. Technical Stack & Libraries

## GUI Framework

**Streamlit** - lets us build an interactive, browser-based dashboard quickly, with native support for file uploads, sliders, and embedded map widgets.

## Core Geospatial Processing
• GeoPandas  — reading and processing vector spatial data (shapefiles, GeoJSON), performing spatial joins between land parcels and ancillary layers
• Shapely    — computing geometric relationships such as distance from a parcel centroid to the nearest road or market point
• Folium / PyDeck — rendering prediction output as an interactive choropleth map embedded in the Streamlit interface

## Machine Learning Component
**Scikit-learn**
-The project will use a **Random Forest Regressor** trained on land parcels with known values and spatial attributes.
-The trained model will then predict values for new parcels based on spatial features.

## Raster Processing
**Rasterio**
Used to process **Sentinel-2 satellite imagery**.

We will compute:
**NDVI (Normalized Difference Vegetation Index)**
NDVI serves as an indicator of vegetation health and soil productivity and will be included as an input feature for the ML model.

## Data Sources
- **NBSS&LUP Soil Data Portal** — Soil fertility and classification
- **OpenStreetMap (OSMnx)** — Road network data
- **APMC / Mandi Locations** — Market coordinates
- **GEE** — Satellite imagery for NDVI
- **Soil grid** - Soil map
- **District Administration(Ludhiana)** - Land value 
- **Soil Health Card Scheme**- Soil Nutrients
- **NIC(data.gov.in)**- Irrigation
# 3. Proposed GUI Architecture

## Input Section
The GUI will include an input panel where users can locate their land in particular  District and draw the boundary of the agricultural parcel directly on an interactive map. Users can zoom to the required location and create a polygon to mark the exact area of the land being analyzed.
After drawing the parcel boundary, users can provide important information related to the land such as soil fertility, irrigation availability, distance to nearby markets, and road accessibility. These factors help in evaluating agricultural land value and productivity.
The interface will include map drawing tools for marking the land parcel and simple selection options such as dropdown menus, checkboxes, or sliders to enter the required agricultural and spatial information.
## Processing Section
When the user clicks the “Run Prediction” button, the system will process the uploaded spatial data using GeoPandas and Shapely to extract relevant spatial features. Distances to markets and road networks will be computed, and the prepared dataset will be passed to a Random Forest regression model implemented using Scikit-learn. The model will then generate predicted land values for each spatial unit.
## Output / Visualization
The predicted land values will be visualized through an interactive map displayed within the GUI. The map will be generated using Folium and will show spatial units colored according to predicted land value categories. In addition, a summary table of predicted values will be displayed to allow users to examine the results numerically.

# 4. GitHub Repository Setup

**Repository URL**
https://github.com/202419014/Geospatial-agricultural-Land-Value-Productivity-intelligence-system.git

## Initial Folder Structure

  project-root/
  ├── data/           # Sample GeoJSON and CSV for immediate testing
  ├── docs/           # Proposal PDF and architecture diagram
  ├── src/
  │   ├── gui/        # Streamlit layout scripts
  │   ├── logic/      # ML model training, prediction, geospatial processing
  │   └── utils/      # Helper functions (data loading, feature extraction)
  ├── main.py         # Entry point  →  streamlit run main.py
  └── requirements.txt

# 5. Preliminary Task Distribution

| Member | Primary Responsibility | Secondary Responsibility |
|------|------|------|
| D. Sushma | ML model development (Random Forest, feature engineering, tuning) | Model evaluation and analysis |
| B. Deepika | Streamlit GUI design and interaction handling | UI testing and refinement |
| V. J. Sreya | Geospatial processing (GeoPandas, Shapely, Rasterio) | Data cleaning and feature preparation |
| D. Sweta | Visualization integration and system integration | Documentation, README, presentation |

# AI Usage Disclosure

AI tools were used only for initial structuring assistance.  
All technical decisions, architecture design, and implementation strategies were reviewed and approved by the entire group. Every member understands the full content of this proposal.
