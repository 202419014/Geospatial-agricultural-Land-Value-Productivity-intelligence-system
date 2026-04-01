"""Buyer dashboard — explore the map, click parcels, compare land values."""
import streamlit as st
import streamlit.components.v1 as components
import sys
import json
import numpy as np
import pandas as pd
import folium
from pathlib import Path

ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT / "src"))

from src.logic.model import predict_all_known_points, predict_land_value, get_price_tier, train_model
from src.utils.feature_extraction import extract_features_for_point
from src.gui.map_builder import build_base_map, add_land_value_points, add_prediction_marker
from src.utils.auth import get_user

PRICE_FILTERS = {
    "All Prices": (0, 999),
    "Below ₹25L": (0, 25),
    "₹25L – ₹35L": (25, 35),
    "₹35L – ₹45L": (35, 45),
    "₹45L – ₹60L": (45, 60),
    "Above ₹60L": (60, 999),
}


def build_buyer_map(df: pd.DataFrame, price_filter: tuple, show_mandis: bool) -> str:
    """Build Folium map filtered by price range."""
    m = build_base_map(show_mandis=show_mandis)
    low, high = price_filter
    filtered = df[
        (df["predicted_value_lakh"] >= low) &
        (df["predicted_value_lakh"] < high)
    ]
    m = add_land_value_points(m, filtered)
    return m._repr_html_()


def show_buyer_page():
    user = get_user(st.session_state.phone)
    name = user.get("name", "Buyer")

    st.markdown(f"""
    <div style='background:linear-gradient(135deg,#1a5276,#2e86c1);padding:18px 24px;
         border-radius:12px;margin-bottom:20px;display:flex;align-items:center;gap:14px'>
      <span style='font-size:36px'>🏡</span>
      <div>
        <h2 style='color:white;margin:0;font-size:22px'>Welcome, {name}!</h2>
        <p style='color:#d6eaf8;margin:0;font-size:13px'>
          Explore agricultural land values across Ludhiana District
        </p>
      </div>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["🗺️ Explore Map", "🔎 Check Any Location"])

    # ── Tab 1: Explore map ──────────────────────────────────────────────────────
    with tab1:
        col_ctrl, col_map = st.columns([1, 3])

        with col_ctrl:
            st.markdown("### 🎛️ Filter & Search")

            price_label = st.selectbox("Filter by Price Range", list(PRICE_FILTERS.keys()))
            price_range = PRICE_FILTERS[price_label]

            tehsil_filter = st.selectbox("Filter by Tehsil", ["All Tehsils"] + [
                "Ludhiana Central","Ludhiana East","Ludhiana West",
                "Khanna","Samrala","Jagraon","Raikot","Machhiwara",
                "Mullanpur Dakha","Sahnewal","Dehlon","Payal",
            ])

            show_mandis = st.checkbox("Show Mandi locations", value=True)

            st.markdown("---")
            st.markdown("### 🎨 Colour Legend")
            for col_hex, label in [
                ("#d73027","🔴 Very High ≥₹60L"),
                ("#fc8d59","🟠 High ₹45–60L"),
                ("#fee08b","🟡 Med-High ₹35–45L"),
                ("#91cf60","🟢 Medium ₹25–35L"),
                ("#1a9850","🟩 Low <₹25L"),
            ]:
                st.markdown(
                    f"<span style='background:{col_hex};display:inline-block;"
                    f"width:16px;height:16px;border-radius:50%;margin-right:8px;"
                    f"vertical-align:middle'></span>{label}",
                    unsafe_allow_html=True
                )

            st.markdown("---")
            st.markdown("💡 **Click any dot** on the map to see full price details and soil/market factors.")

        with col_map:
            st.markdown("### 🗺️ Ludhiana District — Agricultural Land Values")

            if "all_points_df" not in st.session_state or st.session_state.all_points_df is None:
                with st.spinner("Loading land data…"):
                    st.session_state.all_points_df = predict_all_known_points()

            df = st.session_state.all_points_df.copy()

            # Apply tehsil filter
            if tehsil_filter != "All Tehsils":
                df = df[df["tehsil"] == tehsil_filter]

            map_html = build_buyer_map(df, price_range, show_mandis)
            components.html(map_html, height=560, scrolling=False)

        # ── Summary cards ───────────────────────────────────────────────────────
        st.markdown("---")
        st.markdown("### 📊 District Summary")

        all_df = st.session_state.all_points_df
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Parcels", len(all_df))
        c2.metric("Avg Value", f"₹{all_df['predicted_value_lakh'].mean():.1f}L/acre")
        c3.metric("Highest Value", f"₹{all_df['predicted_value_lakh'].max():.1f}L/acre")
        c4.metric("Lowest Value", f"₹{all_df['predicted_value_lakh'].min():.1f}L/acre")

        # ── Data table ──────────────────────────────────────────────────────────
        st.markdown("### 📋 All Land Parcels")
        search = st.text_input("🔍 Search by village or tehsil", "")

        show_df = all_df[["village_name","tehsil","predicted_value_lakh",
                           "rate_per_acre_inr","dist_city_km",
                           "dist_nearest_mandi_km","irrigation_index"]].copy()
        show_df.columns = ["Village","Tehsil","Predicted (L/Acre)","Actual Rate","Dist City (km)",
                            "Dist Mandi (km)","Irrigation"]
        show_df["Predicted (L/Acre)"] = show_df["Predicted (L/Acre)"].apply(lambda x: f"₹{x:.1f}L")
        show_df["Actual Rate"]        = show_df["Actual Rate"].apply(lambda x: f"₹{x/100000:.1f}L")
        show_df["Irrigation"]         = show_df["Irrigation"].apply(lambda x: "✅" if x and x > 0.5 else "❌")

        if search:
            mask = (show_df["Village"].str.contains(search, case=False) |
                    show_df["Tehsil"].str.contains(search, case=False))
            show_df = show_df[mask]

        st.dataframe(show_df, use_container_width=True, height=300)

    # ── Tab 2: Check any custom location ───────────────────────────────────────
    with tab2:
        st.markdown("### 🔎 Check Value of Any Location in Ludhiana")
        st.markdown("Enter coordinates of any agricultural land to get an instant valuation.")

        col1, col2 = st.columns(2)
        with col1:
            b_lat = st.number_input("Latitude", value=30.85, min_value=30.4, max_value=31.2,
                                     step=0.001, format="%.4f", key="buyer_lat")
        with col2:
            b_lon = st.number_input("Longitude", value=75.85, min_value=75.2, max_value=76.5,
                                     step=0.001, format="%.4f", key="buyer_lon")

        st.info("💡 Open Google Maps → Long press on any agricultural land → copy the coordinates shown")

        if st.button("🔍 Check Land Value", use_container_width=True, type="primary"):
            with st.spinner("Fetching satellite data and computing value…"):
                features = extract_features_for_point(b_lat, b_lon)
                features["road_accessibility"]   = 3
                features["soil_fertility_score"] = 3
                features["irrigation_index"]     = features.get("irrigation_index", 0.5) or 0.5

                result = predict_land_value(features)
                val_inr  = result["predicted_value_inr"]
                val_lakh = result["predicted_value_lakh"]
                color, tier = get_price_tier(val_inr)

            # Result card
            st.markdown(f"""
            <div style='background:linear-gradient(135deg,{color}22,{color}44);
                 border:2px solid {color};border-radius:12px;padding:20px;
                 margin:12px 0;text-align:center'>
              <div style='font-size:13px;color:#555'>Estimated Land Value at ({b_lat:.4f}, {b_lon:.4f})</div>
              <div style='font-size:42px;font-weight:bold;color:{color};margin-top:8px'>
                ₹{val_lakh:.1f}L <span style='font-size:18px;color:#555'>/ acre</span>
              </div>
              <div style='margin-top:10px'>
                <span style='background:{color};color:white;padding:5px 18px;
                      border-radius:20px;font-size:14px;font-weight:bold'>{tier}</span>
              </div>
            </div>
            """, unsafe_allow_html=True)

            # Factor breakdown
            st.markdown("### 🔍 Price Factors")
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
            for feat, info in list(result["contributions"].items())[:8]:
                imp = info["importance"]
                val_f = info["value"]
                bar = min(int(imp * 4), 100)
                st.markdown(f"""
                <div style='margin:5px 0'>
                  <div style='display:flex;justify-content:space-between;font-size:13px'>
                    <span>{LABELS.get(feat, feat)}</span>
                    <span><b>{val_f:.2f}</b> &nbsp;
                    <span style='color:#999'>{imp:.1f}% influence</span></span>
                  </div>
                  <div style='background:#ecf0f1;border-radius:4px;height:10px'>
                    <div style='background:{color};width:{bar}%;height:10px;border-radius:4px'></div>
                  </div>
                </div>""", unsafe_allow_html=True)

            # Market info
            st.markdown("### 🏪 Nearest Markets")
            c1, c2, c3 = st.columns(3)
            c1.metric("Nearest Mandi", features.get("nearest_mandi_name","?"),
                      f"{features.get('dist_nearest_mandi_km','?')} km")
            c2.metric("Nearest APMC", features.get("nearest_apmc_name","?"),
                      f"{features.get('dist_nearest_apmc_km','?')} km")
            c3.metric("From City", f"{features.get('dist_city_km','?')} km")

            # Map
            st.markdown("### 🗺️ Location on Map")
            m_map = build_base_map(show_mandis=True)
            if st.session_state.get("all_points_df") is not None:
                m_map = add_land_value_points(m_map, st.session_state.all_points_df)
            m_map = add_prediction_marker(m_map, b_lat, b_lon, result, features)
            components.html(m_map._repr_html_(), height=400, scrolling=False)
