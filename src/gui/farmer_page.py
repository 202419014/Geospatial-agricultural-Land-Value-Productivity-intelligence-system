"""Farmer dashboard — 4 corner points OR draw on map interactively."""
import streamlit as st
import streamlit.components.v1 as components
import sys
import json
import math
import numpy as np
import folium
from pathlib import Path

ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT / "src"))

from src.utils.feature_extraction import extract_features_for_point
from src.logic.model import predict_land_value, get_price_tier
from src.gui.map_builder import build_base_map
from src.utils.auth import save_farmer_submission, get_farmer_submissions, get_user

TEHSILS = [
    "Ludhiana Central", "Ludhiana East", "Ludhiana West",
    "Khanna", "Samrala", "Jagraon", "Raikot", "Machhiwara",
    "Mullanpur Dakha", "Sahnewal", "Dehlon", "Payal",
]

TEHSIL_CENTERS = {
    "Ludhiana Central":  [30.9010, 75.8573],
    "Ludhiana East":     [30.9300, 75.8900],
    "Ludhiana West":     [30.8700, 75.7900],
    "Khanna":            [30.7050, 76.2200],
    "Samrala":           [30.8370, 76.1920],
    "Jagraon":           [30.7900, 75.4740],
    "Raikot":            [30.6490, 75.6030],
    "Machhiwara":        [30.9250, 76.1880],
    "Mullanpur Dakha":   [30.8990, 75.7650],
    "Sahnewal":          [30.8540, 75.9310],
    "Dehlon":            [30.7820, 75.8930],
    "Payal":             [30.6810, 76.0840],
}

SOIL_TYPES   = ["Loamy", "Sandy Loam", "Clay Loam", "Silty Clay", "Sandy", "Black Cotton"]
CROP_TYPES   = ["Wheat-Rice (Kharif-Rabi)", "Wheat Only", "Vegetables", "Sugarcane", "Mixed Crops", "Fallow"]
ROAD_OPTIONS = {
    "Highway Frontage": 5, "Main Pucca Road": 4,
    "Village Pucca Road": 3, "Kuccha Road": 2, "Remote / No Road": 1,
}
IRRIGATION_MAP = {
    "Canal Irrigated": 1.0, "Tube-well Irrigated": 0.8,
    "Rain-fed Only": 0.1,   "Mixed": 0.6,
}
LABELS = {
    "dist_city_km":         "🏙️ Distance from City",
    "dist_nearest_mandi_km":"🏪 Distance to Mandi",
    "dist_nearest_apmc_km": "🏬 Distance to APMC",
    "clay_pct":             "🟤 Clay Content",
    "sand_pct":             "🟡 Sand Content",
    "silt_pct":             "⚪ Silt Content",
    "pH":                   "🧪 Soil pH",
    "nitrogen_mg_kg":       "🌿 Nitrogen",
    "organic_carbon_pct":   "♻️ Organic Carbon",
    "irrigation_index":     "💧 Irrigation",
    "road_accessibility":   "🛣️ Road Access",
    "soil_fertility_score": "🌱 Soil Fertility",
}


# ── Geometry helpers ─────────────────────────────────────────────────────────

def polygon_area_acres(coords):
    if len(coords) < 3:
        return 0.0
    R = 6371000.0
    lat0 = sum(c[0] for c in coords) / len(coords)
    lon0 = sum(c[1] for c in coords) / len(coords)
    def to_xy(lat, lon):
        x = math.radians(lon - lon0) * R * math.cos(math.radians(lat0))
        y = math.radians(lat - lat0) * R
        return x, y
    pts  = [to_xy(c[0], c[1]) for c in coords]
    n    = len(pts)
    area = sum(pts[i][0]*pts[(i+1)%n][1] - pts[(i+1)%n][0]*pts[i][1] for i in range(n))
    return abs(area) / 2.0 / 4046.86

def centroid(coords):
    return sum(c[0] for c in coords)/len(coords), sum(c[1] for c in coords)/len(coords)


# ── Interactive draw map (pure HTML/JS — no copy-paste needed) ───────────────

def build_interactive_draw_map(tehsil: str, existing_coords: list = None) -> str:
    """
    Full Leaflet map with draw tools.
    When user finishes drawing, coordinates are written into a hidden input
    and a Streamlit-compatible query param update triggers re-read.
    Coordinates are stored in sessionStorage as JSON so Streamlit can read
    them via st.query_params after the user clicks 'Use This Boundary'.
    """
    center = TEHSIL_CENTERS.get(tehsil, [30.85, 75.85])
    clat, clon = center

    existing_js = "null"
    if existing_coords and len(existing_coords) >= 3:
        existing_js = json.dumps(existing_coords)

    html = f"""
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/leaflet.draw/1.0.4/leaflet.draw.css"/>
  <style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{ font-family: Arial, sans-serif; }}
    #map {{ width: 100%; height: 460px; }}
    #controls {{
      background: #1b2631; color: white; padding: 10px 14px;
      font-size: 13px; display: flex; align-items: center;
      justify-content: space-between; flex-wrap: wrap; gap: 8px;
    }}
    #status {{ color: #27ae60; font-weight: bold; flex: 1; }}
    #coords-display {{
      background: #0d1b2a; border-radius: 6px; padding: 6px 10px;
      font-size: 11px; color: #aed6f1; max-width: 420px;
      overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
    }}
    #use-btn {{
      background: linear-gradient(90deg,#1a5276,#27ae60);
      color: white; border: none; border-radius: 6px;
      padding: 8px 18px; font-weight: bold; font-size: 13px;
      cursor: pointer; white-space: nowrap;
    }}
    #use-btn:hover {{ opacity: 0.9; }}
    #use-btn:disabled {{ background: #555; cursor: not-allowed; }}
    #clear-btn {{
      background: #c0392b; color: white; border: none;
      border-radius: 6px; padding: 8px 14px; font-size: 13px;
      cursor: pointer;
    }}
    .info-banner {{
      position: absolute; top: 10px; left: 50%; transform: translateX(-50%);
      background: rgba(26,82,118,0.92); color: white;
      padding: 7px 16px; border-radius: 20px; font-size: 12px;
      z-index: 1000; pointer-events: none; white-space: nowrap;
    }}
  </style>
</head>
<body>
<div style="position:relative">
  <div id="map"></div>
  <div class="info-banner" id="banner">
    🖊️ Use polygon tool (left) to draw boundary &nbsp;|&nbsp; Switch to 🛰️ Satellite for better view
  </div>
</div>
<div id="controls">
  <div id="status">Draw your land boundary on the map above</div>
  <div id="coords-display">No polygon drawn yet</div>
  <button id="clear-btn" onclick="clearAll()" disabled>🗑️ Clear</button>
  <button id="use-btn" onclick="useCoords()" disabled>✅ Use This Boundary</button>
</div>

<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/leaflet.draw/1.0.4/leaflet.draw.js"></script>
<script>
  var map = L.map('map').setView([{clat}, {clon}], 14);

  // Tile layers
  var street = L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
    attribution: '© OpenStreetMap', maxZoom: 20
  }});
  var satellite = L.tileLayer(
    'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{{z}}/{{y}}/{{x}}',
    {{ attribution: '© Esri', maxZoom: 20 }}
  );
  satellite.addTo(map);  // default to satellite for farmland visibility

  L.control.layers({{"🗺️ Street": street, "🛰️ Satellite": satellite}}).addTo(map);
  L.control.scale({{imperial: false}}).addTo(map);

  // Draw feature group
  var drawnItems = new L.FeatureGroup();
  map.addLayer(drawnItems);

  var drawControl = new L.Control.Draw({{
    draw: {{
      polygon: {{
        allowIntersection: false,
        showArea: true,
        shapeOptions: {{ color: '#27ae60', fillOpacity: 0.2, weight: 3 }}
      }},
      rectangle: {{
        shapeOptions: {{ color: '#1a5276', fillOpacity: 0.2, weight: 3 }}
      }},
      polyline:     false,
      circle:       false,
      marker:       false,
      circlemarker: false,
    }},
    edit: {{ featureGroup: drawnItems, remove: true }}
  }});
  map.addControl(drawControl);

  var currentCoords = null;

  // Restore existing polygon if coming back to this step
  var existing = {existing_js};
  if (existing && existing.length >= 3) {{
    var latlngs = existing.map(function(c) {{ return [c[0], c[1]]; }});
    var poly = L.polygon(latlngs, {{color:'#27ae60', fillOpacity:0.2, weight:3}});
    drawnItems.addLayer(poly);
    currentCoords = existing;
    updateUI(existing);
    map.fitBounds(poly.getBounds().pad(0.2));
  }}

  map.on(L.Draw.Event.CREATED, function(e) {{
    drawnItems.clearLayers();
    drawnItems.addLayer(e.layer);
    var latlngs = e.layer.getLatLngs()[0];
    currentCoords = latlngs.map(function(ll) {{ return [ll.lat, ll.lng]; }});
    updateUI(currentCoords);
  }});

  map.on(L.Draw.Event.EDITED, function(e) {{
    e.layers.eachLayer(function(layer) {{
      var latlngs = layer.getLatLngs()[0];
      currentCoords = latlngs.map(function(ll) {{ return [ll.lat, ll.lng]; }});
      updateUI(currentCoords);
    }});
  }});

  map.on(L.Draw.Event.DELETED, function() {{
    currentCoords = null;
    document.getElementById('status').innerText = 'Draw your land boundary on the map above';
    document.getElementById('coords-display').innerText = 'No polygon drawn yet';
    document.getElementById('use-btn').disabled = true;
    document.getElementById('clear-btn').disabled = true;
  }});

  function updateUI(coords) {{
    var n = coords.length;
    document.getElementById('status').innerText =
      '✅ Polygon drawn — ' + n + ' corners detected. Click "Use This Boundary" to proceed.';
    document.getElementById('coords-display').innerText =
      'Coords: ' + coords.map(function(c){{
        return c[0].toFixed(5)+','+c[1].toFixed(5);
      }}).join(' | ');
    document.getElementById('use-btn').disabled  = false;
    document.getElementById('clear-btn').disabled = false;
  }}

  function clearAll() {{
    drawnItems.clearLayers();
    currentCoords = null;
    document.getElementById('status').innerText = 'Draw your land boundary on the map above';
    document.getElementById('coords-display').innerText = 'No polygon drawn yet';
    document.getElementById('use-btn').disabled  = true;
    document.getElementById('clear-btn').disabled = true;
  }}

  function useCoords() {{
    if (!currentCoords) return;
    var json = JSON.stringify(currentCoords);
    // Send to Streamlit parent via postMessage
    window.parent.postMessage({{
      type: 'streamlit:setComponentValue',
      value: json
    }}, '*');
    // Also store in sessionStorage as fallback
    window.parent.sessionStorage.setItem('drawn_polygon', json);
    document.getElementById('status').innerText =
      '📋 Coordinates sent! Paste into the box below if not auto-filled.';
    document.getElementById('coords-display').innerText = json;
  }}
</script>
</body>
</html>
"""
    return html


def build_boundary_map(coords, color="#27ae60", result=None, tehsil=""):
    clat, clon = centroid(coords) if coords else TEHSIL_CENTERS.get(tehsil, [30.85, 75.85])
    m = folium.Map(location=[clat, clon], zoom_start=15, tiles="CartoDB positron", attr="CartoDB")
    folium.TileLayer(
        "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
        attr="Esri", name="Satellite 🛰️", overlay=False, control=True,
    ).add_to(m)
    folium.TileLayer("OpenStreetMap", name="Street Map").add_to(m)

    if len(coords) >= 3:
        folium.Polygon(
            locations=coords, color=color, weight=3,
            fill=True, fill_color=color, fill_opacity=0.25,
        ).add_to(m)
        for i, (lat, lon) in enumerate(coords):
            folium.Marker(
                [lat, lon],
                icon=folium.DivIcon(
                    html=f"""<div style="background:#1a5276;color:white;border-radius:50%;
                             width:22px;height:22px;display:flex;align-items:center;
                             justify-content:center;font-size:11px;font-weight:bold;
                             border:2px solid white;box-shadow:0 0 4px rgba(0,0,0,.5)">
                             {i+1}</div>""",
                    icon_size=(22,22), icon_anchor=(11,11),
                ),
                tooltip=f"Corner {i+1}: {lat:.5f}, {lon:.5f}",
            ).add_to(m)

        val_lakh = result["predicted_value_lakh"] if result else None
        popup_html = f"""<div style='font-family:Arial;padding:8px;min-width:160px'>
          <b style='color:{color}'>🌾 Your Parcel</b><br>
          {'<span style="font-size:18px;font-weight:bold;color:'+color+'">₹'+str(val_lakh)+'L/acre</span><br>' if val_lakh else ''}
          <span style='font-size:11px;color:#555'>{clat:.5f}°N, {clon:.5f}°E</span></div>"""
        folium.Marker(
            [clat, clon],
            icon=folium.DivIcon(
                html=f"""<div style="background:{color};color:white;border-radius:50%;
                         width:30px;height:30px;display:flex;align-items:center;
                         justify-content:center;font-size:16px;
                         border:3px solid black;box-shadow:0 0 6px rgba(0,0,0,.6)">🌾</div>""",
                icon_size=(30,30), icon_anchor=(15,15),
            ),
            tooltip=f"Centroid{' — ₹'+str(val_lakh)+'L/acre' if val_lakh else ''}",
            popup=folium.Popup(popup_html, max_width=220),
        ).add_to(m)

    folium.LayerControl().add_to(m)
    return m._repr_html_()


# ── Main page ────────────────────────────────────────────────────────────────

def show_farmer_page():
    user = get_user(st.session_state.phone)
    name = user.get("name", "Farmer")

    st.markdown(f"""
    <div style='background:linear-gradient(135deg,#1a5276,#27ae60);padding:18px 24px;
         border-radius:12px;margin-bottom:20px;display:flex;align-items:center;gap:14px'>
      <span style='font-size:36px'>🌾</span>
      <div>
        <h2 style='color:white;margin:0;font-size:22px'>Welcome, {name}!</h2>
        <p style='color:#d5f5e3;margin:0;font-size:13px'>
          Mark your land boundary and get an AI-powered valuation
        </p>
      </div>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["📋 New Land Valuation", "📁 My Previous Valuations"])

    with tab1:

        # Step 1 ───────────────────────────────────────────────────────────────
        st.markdown("### 🏠 Step 1 — Basic Land Information")
        col1, col2, col3 = st.columns(3)
        with col1: tehsil  = st.selectbox("Tehsil / Block", TEHSILS)
        with col2: village = st.text_input("Village Name", placeholder="e.g. Gill, Doraha")
        with col3: khasra  = st.text_input("Khasra / Survey No.", placeholder="e.g. 123/4")

        # Step 2 — Toggle ──────────────────────────────────────────────────────
        st.markdown("---")
        st.markdown("### 📍 Step 2 — Mark Your Land Boundary")

        method = st.radio(
            "Choose how to mark your land boundary:",
            ["📌 Enter 4 Corner Coordinates", "✏️ Draw Boundary on Map"],
            horizontal=True,
        )

        corners = []

        # ── Option A: 4 coordinates ──────────────────────────────────────────
        if method == "📌 Enter 4 Corner Coordinates":
            st.info("💡 Open **Google Maps** → Long press on each corner of your land → note the coordinates → enter below going **clockwise**")

            default = TEHSIL_CENTERS.get(tehsil, [30.85, 75.85])
            offsets = [[0,0],[0,0.001],[0.001,0.001],[0.001,0]]
            labels  = ["↖️ Corner 1 — North-West","↗️ Corner 2 — North-East",
                       "↘️ Corner 3 — South-East","↙️ Corner 4 — South-West"]

            for i in range(4):
                st.markdown(f"**{labels[i]}**")
                c1, c2 = st.columns(2)
                with c1:
                    lat_i = st.number_input(f"Latitude — Corner {i+1}",
                        value=round(default[0]+offsets[i][0], 5),
                        min_value=30.4, max_value=31.2,
                        step=0.00001, format="%.5f", key=f"lat_{i}")
                with c2:
                    lon_i = st.number_input(f"Longitude — Corner {i+1}",
                        value=round(default[1]+offsets[i][1], 5),
                        min_value=75.2, max_value=76.5,
                        step=0.00001, format="%.5f", key=f"lon_{i}")
                corners.append([lat_i, lon_i])

            st.markdown("#### 🗺️ Live Boundary Preview")
            components.html(build_boundary_map(corners, tehsil=tehsil), height=380, scrolling=False)

        # ── Option B: Draw on map ─────────────────────────────────────────────
        else:
            st.markdown(f"""
            <div style='background:#eaf4fb;border:1px solid #2e86c1;border-radius:8px;
                 padding:10px 14px;margin-bottom:8px;font-size:13px'>
              🗺️ Map zoomed to <b>{tehsil}</b>.
              &nbsp;1️⃣ Switch to <b>Satellite 🛰️</b> view &nbsp;
              2️⃣ Click the <b>polygon tool ✏️</b> on the left &nbsp;
              3️⃣ Click each corner of your land &nbsp;
              4️⃣ Double-click to finish &nbsp;
              5️⃣ Click <b>✅ Use This Boundary</b>
            </div>
            """, unsafe_allow_html=True)

            # Show existing drawn corners if already set in session
            existing = st.session_state.get("drawn_corners_raw", None)

            # Render the interactive draw map
            draw_html = build_interactive_draw_map(tehsil, existing_coords=existing)
            components.html(draw_html, height=520, scrolling=False)

            st.markdown("#### 📋 Step 5 — Paste Coordinates Here")
            st.caption(
                "After clicking **✅ Use This Boundary** on the map, "
                "the coordinates appear in the green display bar. "
                "Copy that JSON and paste it below."
            )

            raw_input = st.text_area(
                "Paste coordinates JSON from map",
                value=st.session_state.get("drawn_corners_raw", ""),
                height=80,
                placeholder='[[30.85123,75.85456],[30.85234,75.85567],...]',
                key="coord_paste_box",
            )

            if raw_input and raw_input.strip():
                try:
                    parsed = json.loads(raw_input.strip())
                    # Accept [[lat,lon],...] format
                    if (isinstance(parsed, list) and len(parsed) >= 3
                            and isinstance(parsed[0], list)):
                        corners = [[float(c[0]), float(c[1])] for c in parsed]
                        st.session_state["drawn_corners_raw"] = raw_input.strip()
                        st.success(f"✅ {len(corners)} corner points loaded successfully!")

                        # Preview
                        st.markdown("#### 🗺️ Your Drawn Boundary")
                        components.html(
                            build_boundary_map(corners, tehsil=tehsil),
                            height=340, scrolling=False,
                        )
                    else:
                        st.error("❌ Format not recognised. Expected: [[lat,lon],[lat,lon],...]")
                except Exception:
                    st.error("❌ Invalid JSON. Copy the full text from the map's green display bar.")
            else:
                st.info("👆 Draw your boundary above then paste the coordinates here")

        # ── Area & centroid ───────────────────────────────────────────────────
        if len(corners) >= 3:
            computed_area  = polygon_area_acres(corners)
            clat, clon     = centroid(corners)
            st.markdown("---")
            ca, cb, cc = st.columns(3)
            ca.metric("📐 Computed Area",      f"{computed_area:.3f} acres")
            cb.metric("📍 Centroid Latitude",  f"{clat:.5f}")
            cc.metric("📍 Centroid Longitude", f"{clon:.5f}")
            use_comp   = st.checkbox(f"Use auto-computed area ({computed_area:.3f} acres)", value=True)
            area_acres = computed_area if use_comp else st.number_input(
                "Enter Area Manually (Acres)", min_value=0.1, max_value=500.0,
                value=round(computed_area,2), step=0.1)
        else:
            clat, clon, area_acres = 30.85, 75.85, 1.0

        # Step 3 ───────────────────────────────────────────────────────────────
        st.markdown("---")
        st.markdown("### 🌱 Step 3 — Land Details")
        col6, col7, col8 = st.columns(3)
        with col6: soil_type  = st.selectbox("Soil Type", SOIL_TYPES)
        with col7: crop_type  = st.selectbox("Current Crop / Land Use", CROP_TYPES)
        with col8: irrigation = st.selectbox("Irrigation Source", list(IRRIGATION_MAP.keys()))
        road_access = st.selectbox("Road Accessibility", list(ROAD_OPTIONS.keys()))
        road_score  = ROAD_OPTIONS[road_access]

        # Step 4 ───────────────────────────────────────────────────────────────
        st.markdown("---")
        st.markdown("### 🧪 Step 4 — Soil Quality")
        soil_fertility = st.slider("Overall Soil Fertility", 1, 5, 3, help="1=Poor 5=Excellent")
        st.caption({1:"🔴 Poor",2:"🟠 Below Average",3:"🟡 Average",4:"🟢 Good",5:"🌟 Excellent"}[soil_fertility])
        use_manual = st.checkbox("I have soil test results (optional)")
        manual_ph = manual_oc = manual_n = None
        if use_manual:
            c1,c2,c3 = st.columns(3)
            with c1: manual_ph = st.slider("Soil pH", 5.0, 9.0, 7.5, 0.1)
            with c2: manual_oc = st.slider("Organic Carbon (%)", 0.1, 3.0, 0.8, 0.1)
            with c3: manual_n  = st.slider("Nitrogen (mg/kg)", 50, 500, 200)

        st.markdown("---")

        # Run ──────────────────────────────────────────────────────────────────
        if st.button("🚀 Get Land Valuation", use_container_width=True, type="primary"):
            if len(corners) < 3:
                st.error("⚠️ Please enter or draw your land boundary first.")
                st.stop()
            if len(set((round(c[0],4), round(c[1],4)) for c in corners)) < 3:
                st.error("⚠️ Corner points are too close. Please enter distinct corners.")
                st.stop()

            with st.spinner("Extracting satellite soil data & running AI model…"):
                clat, clon = centroid(corners)
                features   = extract_features_for_point(clat, clon)
                features["road_accessibility"]   = road_score
                features["soil_fertility_score"] = soil_fertility
                features["irrigation_index"]     = IRRIGATION_MAP[irrigation]
                if use_manual:
                    if manual_ph: features["pH"]                 = manual_ph
                    if manual_oc: features["organic_carbon_pct"] = manual_oc
                    if manual_n:  features["nitrogen_mg_kg"]     = manual_n

                result    = predict_land_value(features)
                val_inr   = result["predicted_value_inr"]
                val_lakh  = result["predicted_value_lakh"]
                total_val = val_inr * area_acres
                color, tier = get_price_tier(val_inr)

                save_farmer_submission(st.session_state.phone, {
                    "village": village or tehsil, "tehsil": tehsil, "khasra": khasra,
                    "corners": corners, "centroid_lat": clat, "centroid_lon": clon,
                    "area_acres": area_acres, "input_method": method,
                    "predicted_per_acre_lakh": val_lakh,
                    "total_value_lakh": round(total_val/100000, 2),
                    "tier": tier, "irrigation": irrigation,
                    "soil_type": soil_type, "crop_type": crop_type,
                })

            st.markdown("---")
            st.markdown("## 📊 Your Land Valuation Report")
            st.markdown(f"""
            <div style='background:linear-gradient(135deg,{color}15,{color}30);
                 border:2px solid {color};border-radius:14px;padding:24px;
                 margin:12px 0;text-align:center'>
              <div style='font-size:13px;color:#555'>AI-Estimated Market Value</div>
              <div style='font-size:46px;font-weight:bold;color:{color};margin:8px 0'>
                ₹{val_lakh:.1f}L <span style='font-size:18px;color:#777;font-weight:normal'>/acre</span>
              </div>
              <div style='font-size:24px;font-weight:bold;color:#1a5276'>
                Total ({area_acres:.2f} acres) : ₹{total_val/100000:.1f}L
              </div>
              <div style='margin-top:10px'>
                <span style='background:{color};color:white;padding:5px 20px;
                      border-radius:20px;font-size:14px;font-weight:bold'>{tier}</span>
              </div>
            </div>""", unsafe_allow_html=True)

            m1,m2,m3,m4 = st.columns(4)
            m1.metric("Per Acre",    f"₹{val_lakh:.1f}L")
            m2.metric("Total Value", f"₹{total_val/100000:.1f}L")
            m3.metric("Area",        f"{area_acres:.2f} acres")
            m4.metric("Category",    tier.split("(")[0].strip())

            st.markdown("### 🗺️ Your Land Boundary")
            components.html(
                build_boundary_map(corners, color=color, result=result, tehsil=tehsil),
                height=430, scrolling=False,
            )
            st.markdown(f"""
            <div style='background:#f0f9f4;border-radius:8px;padding:10px 14px;font-size:13px;margin:8px 0'>
              📐 <b>Area:</b> {area_acres:.3f} acres &nbsp;|&nbsp;
              📍 <b>Centroid:</b> {clat:.5f}°N, {clon:.5f}°E &nbsp;|&nbsp;
              🔢 <b>Corners:</b> {len(corners)} points
            </div>""", unsafe_allow_html=True)

            st.markdown("### 🔍 Why This Value? — Key Price Factors")
            for feat, info in list(result["contributions"].items())[:8]:
                imp = info["importance"]; val_f = info["value"]
                bar = min(int(imp*4), 100)
                st.markdown(f"""
                <div style='margin:6px 0'>
                  <div style='display:flex;justify-content:space-between;font-size:13px'>
                    <span>{LABELS.get(feat,feat)}</span>
                    <span><b>{val_f:.2f}</b><span style='color:#999'> — {imp:.1f}% influence</span></span>
                  </div>
                  <div style='background:#ecf0f1;border-radius:4px;height:10px'>
                    <div style='background:{color};width:{bar}%;height:10px;border-radius:4px'></div>
                  </div>
                </div>""", unsafe_allow_html=True)

            with st.expander("🔬 Soil Parameters"):
                s1,s2,s3 = st.columns(3)
                s1.metric("pH",             f"{features.get('pH',0):.1f}"                if features.get('pH') else "N/A")
                s2.metric("Organic Carbon", f"{features.get('organic_carbon_pct',0):.2f}%" if features.get('organic_carbon_pct') else "N/A")
                s3.metric("Nitrogen",       f"{features.get('nitrogen_mg_kg',0):.1f} mg/kg" if features.get('nitrogen_mg_kg') else "N/A")
                s4,s5,s6 = st.columns(3)
                s4.metric("Clay", f"{features.get('clay_pct',0):.1f}%")
                s5.metric("Sand", f"{features.get('sand_pct',0):.1f}%")
                s6.metric("Silt", f"{features.get('silt_pct',0):.1f}%")

            st.markdown("### 🏪 Nearest Markets")
            c1,c2,c3 = st.columns(3)
            c1.metric("Nearest Mandi", features.get("nearest_mandi_name","?"), f"{features.get('dist_nearest_mandi_km','?')} km away")
            c2.metric("Nearest APMC",  features.get("nearest_apmc_name","?"),  f"{features.get('dist_nearest_apmc_km','?')} km away")
            c3.metric("From City",     f"{features.get('dist_city_km','?')} km", "Ludhiana")
            st.success("✅ Valuation saved! View it in **My Previous Valuations** tab.")

    # Tab 2 ────────────────────────────────────────────────────────────────────
    with tab2:
        submissions = get_farmer_submissions(st.session_state.phone)
        if not submissions:
            st.info("No valuations yet. Go to **New Land Valuation** tab to get started.")
        else:
            st.markdown(f"### Your {len(submissions)} Saved Valuation(s)")
            for i, s in enumerate(reversed(submissions), 1):
                with st.expander(
                    f"#{i} — {s.get('village','?')}, {s.get('tehsil','?')} | "
                    f"₹{s.get('predicted_per_acre_lakh','?')}L/acre | "
                    f"{s.get('area_acres','?')} acres | {s.get('timestamp','')}"
                ):
                    c1,c2,c3 = st.columns(3)
                    c1.metric("Per Acre",    f"₹{s.get('predicted_per_acre_lakh','?')}L")
                    c2.metric("Total Value", f"₹{s.get('total_value_lakh','?')}L")
                    c3.metric("Area",        f"{s.get('area_acres','?')} acres")
                    st.write(f"**Khasra:** {s.get('khasra','N/A')} | **Soil:** {s.get('soil_type','?')} | "
                             f"**Crop:** {s.get('crop_type','?')} | **Irrigation:** {s.get('irrigation','?')}")
                    st.write(f"**Method:** {s.get('input_method','?')} | **Category:** {s.get('tier','?')}")
                    if s.get("corners") and len(s["corners"]) >= 3:
                        st.markdown("**Land Boundary:**")
                        components.html(
                            build_boundary_map(s["corners"], tehsil=s.get("tehsil","")),
                            height=280, scrolling=False,
                        )
