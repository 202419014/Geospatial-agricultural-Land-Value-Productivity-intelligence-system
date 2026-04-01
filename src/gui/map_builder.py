"""Folium map generation for the agricultural land value GUI."""
import folium
from folium.plugins import Draw, MeasureControl
import pandas as pd
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from logic.model import get_price_tier


LUDHIANA_CENTER = [30.85, 75.85]


def make_feature_explanation(row: dict) -> str:
    """Build a human-readable HTML popup explaining land value factors."""
    val_lakh = row.get("predicted_value_lakh", row.get("rate_per_acre_inr", 0) / 100000)
    val_inr = row.get("predicted_value_inr", row.get("rate_per_acre_inr", 0))
    color, tier = get_price_tier(val_inr)

    contribs = row.get("contributions", {})
    top_factors_html = ""
    if contribs:
        LABELS = {
            "dist_city_km": "Distance from City",
            "dist_nearest_mandi_km": "Distance to Nearest Mandi",
            "dist_nearest_apmc_km": "Distance to Nearest APMC",
            "clay_pct": "Clay Content (%)",
            "sand_pct": "Sand Content (%)",
            "silt_pct": "Silt Content (%)",
            "pH": "Soil pH",
            "nitrogen_mg_kg": "Nitrogen (mg/kg)",
            "organic_carbon_pct": "Organic Carbon (%)",
            "irrigation_index": "Irrigation Availability",
            "road_accessibility": "Road Accessibility (1–5)",
            "soil_fertility_score": "Soil Fertility Score (1–5)",
        }
        top_factors_html = "<br><b>Key Price Drivers:</b><table style='width:100%;font-size:12px;margin-top:4px'>"
        for feat, info in list(contribs.items())[:6]:
            label = LABELS.get(feat, feat)
            imp = info["importance"]
            val = info["value"]
            bar_width = min(int(imp * 3), 100)
            top_factors_html += f"""
            <tr>
              <td style='padding:2px 4px;width:48%'>{label}</td>
              <td style='padding:2px;width:20%'>{val:.2f}</td>
              <td style='padding:2px;width:32%'>
                <div style='background:#ddd;border-radius:3px'>
                  <div style='background:{color};width:{bar_width}%;height:10px;border-radius:3px'></div>
                </div>
                <span style='font-size:10px'>{imp:.1f}%</span>
              </td>
            </tr>"""
        top_factors_html += "</table>"

    soil_html = ""
    if "clay_pct" in row:
        ph = row.get('pH', 0)
        ph_str = f"{ph:.1f}" if ph else "N/A"
        oc = row.get('organic_carbon_pct', 0)
        oc_str = f"{oc:.2f}%" if oc else "N/A"
        irr = row.get('irrigation_index', 0)
        irr_str = "Yes" if irr and irr > 0.5 else "No/Low"
        soil_html = f"""<br><b>Soil & Environment:</b>
        <div style='font-size:12px;background:#f9f9f9;padding:4px;border-radius:4px;margin-top:2px'>
          pH: {ph_str} &nbsp;|&nbsp; Organic Carbon: {oc_str} &nbsp;|&nbsp; Irrigation: {irr_str}
        </div>"""

    mkt_html = ""
    if "nearest_mandi_name" in row:
        mkt_html = f"""<br><b>Market Access:</b>
        <div style='font-size:12px;background:#f0f8ff;padding:4px;border-radius:4px;margin-top:2px'>
          Nearest Mandi: <b>{row['nearest_mandi_name']}</b> ({row.get('dist_nearest_mandi_km','?')} km)<br>
          Nearest APMC: <b>{row.get('nearest_apmc_name','?')}</b> ({row.get('dist_nearest_apmc_km','?')} km)<br>
          Distance from City: <b>{row.get('dist_city_km','?')} km</b>
        </div>"""

    popup_html = f"""
    <div style='font-family:Arial,sans-serif;min-width:280px;max-width:340px'>
      <div style='background:{color};color:white;padding:8px;border-radius:6px 6px 0 0;'>
        <b style='font-size:15px'>🌾 {row.get('village_name','Unknown')}</b><br>
        <span style='font-size:12px'>Tehsil: {row.get('tehsil','?')}</span>
      </div>
      <div style='padding:8px;border:1px solid #ddd;border-top:none;border-radius:0 0 6px 6px'>
        <div style='display:flex;justify-content:space-between;align-items:center'>
          <div>
            <span style='font-size:18px;font-weight:bold;color:{color}'>₹{val_lakh:.1f}L</span>
            <span style='font-size:11px;color:#666'>/acre</span>
          </div>
          <div style='background:{color}20;padding:3px 8px;border-radius:12px;font-size:11px;color:{color};font-weight:bold'>
            {tier}
          </div>
        </div>
        <div style='font-size:11px;color:#888;margin-top:2px'>
          Actual Rate: ₹{row.get('rate_per_acre_inr',0)/100000:.1f}L/acre
        </div>
        {soil_html}
        {mkt_html}
        {top_factors_html}
      </div>
    </div>
    """
    return popup_html


def build_base_map(show_mandis: bool = True) -> folium.Map:
    """Create a base Folium map centered on Ludhiana."""
    m = folium.Map(
        location=LUDHIANA_CENTER,
        zoom_start=10,
        tiles="CartoDB positron",
        attr="CartoDB",
    )
    # Satellite layer option
    folium.TileLayer(
        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
        attr="Esri",
        name="Satellite",
        overlay=False,
        control=True,
    ).add_to(m)

    folium.TileLayer("OpenStreetMap", name="Street Map").add_to(m)

    if show_mandis:
        mandi_group = folium.FeatureGroup(name="🏪 Mandis / Markets")
        try:
            with open(Path(__file__).parent.parent.parent / "data" / "ludhiana_mandis.geojson") as f:
                mandis = json.load(f)
            for feat in mandis["features"]:
                p = feat["properties"]
                lat = p["Latitude"]
                lon = p["Longitude"]
                folium.Marker(
                    [lat, lon],
                    popup=folium.Popup(f"<b>🏪 {p['Market']}</b>", max_width=200),
                    tooltip=p["Market"],
                    icon=folium.Icon(color="blue", icon="shopping-cart", prefix="fa"),
                ).add_to(mandi_group)
        except Exception:
            pass
        mandi_group.add_to(m)

    # Draw tools
    Draw(
        draw_options={
            "polygon": True,
            "rectangle": True,
            "polyline": False,
            "circle": False,
            "marker": True,
            "circlemarker": False,
        },
        edit_options={"edit": True, "remove": True},
    ).add_to(m)

    MeasureControl(position="bottomleft", primary_length_unit="kilometers").add_to(m)
    folium.LayerControl().add_to(m)

    return m


def add_land_value_points(m: folium.Map, df: pd.DataFrame) -> folium.Map:
    """Add agricultural land value points as colored DivIcon markers directly on map."""

    for _, row in df.iterrows():
        val_inr = row.get("predicted_value_inr", row.get("rate_per_acre_inr", 0))
        color, tier = get_price_tier(val_inr)
        val_lakh = val_inr / 100000

        popup_html = make_feature_explanation(row.to_dict())

        # DivIcon circle — renders reliably inside components.html
        icon_html = f"""
        <div style="
            width:22px; height:22px; border-radius:50%;
            background:{color}; border:3px solid white;
            box-shadow:0 0 4px rgba(0,0,0,0.5);
            cursor:pointer;
        "></div>"""

        folium.Marker(
            location=[row["latitude"], row["longitude"]],
            icon=folium.DivIcon(
                html=icon_html,
                icon_size=(22, 22),
                icon_anchor=(11, 11),
            ),
            tooltip=folium.Tooltip(
                f"<b>{row['village_name']}</b><br>₹{val_lakh:.1f}L/acre — {tier}",
                sticky=True,
            ),
            popup=folium.Popup(popup_html, max_width=360),
        ).add_to(m)

    # Legend
    legend_html = """
    <div style="position:fixed;bottom:30px;right:10px;z-index:1000;background:white;
         border:1px solid #ccc;border-radius:8px;padding:12px;font-size:12px;
         box-shadow:2px 2px 6px rgba(0,0,0,0.2);font-family:Arial">
      <b>Land Value (per acre)</b><br>
      <div style="margin-top:6px">
        <span style="background:#d73027;display:inline-block;width:14px;height:14px;border-radius:50%;margin-right:6px;vertical-align:middle"></span>Very High ≥60L<br>
        <span style="background:#fc8d59;display:inline-block;width:14px;height:14px;border-radius:50%;margin-right:6px;vertical-align:middle"></span>High 45–60L<br>
        <span style="background:#fee08b;display:inline-block;width:14px;height:14px;border-radius:50%;margin-right:6px;vertical-align:middle"></span>Medium-High 35–45L<br>
        <span style="background:#91cf60;display:inline-block;width:14px;height:14px;border-radius:50%;margin-right:6px;vertical-align:middle"></span>Medium 25–35L<br>
        <span style="background:#1a9850;display:inline-block;width:14px;height:14px;border-radius:50%;margin-right:6px;vertical-align:middle"></span>Low &lt;25L
      </div>
    </div>
    """
    m.get_root().html.add_child(folium.Element(legend_html))
    return m


def add_prediction_marker(m: folium.Map, lat: float, lon: float, pred_result: dict, features: dict) -> folium.Map:
    """Add a prediction result marker to the map."""
    val_inr = pred_result["predicted_value_inr"]
    val_lakh = pred_result["predicted_value_lakh"]
    color, tier = get_price_tier(val_inr)
    contribs = pred_result["contributions"]

    row_data = {
        "village_name": "Your Selected Parcel",
        "tehsil": f"({lat:.4f}, {lon:.4f})",
        "rate_per_acre_inr": val_inr,
        "predicted_value_inr": val_inr,
        "predicted_value_lakh": val_lakh,
        "contributions": contribs,
        **features,
    }
    popup_html = make_feature_explanation(row_data)

    pred_icon_html = f"""
    <div style="
        width:30px; height:30px; border-radius:50%;
        background:{color}; border:4px solid black;
        box-shadow:0 0 8px rgba(0,0,0,0.7);
        cursor:pointer; display:flex; align-items:center; justify-content:center;
        font-size:14px;
    ">📍</div>"""

    folium.Marker(
        location=[lat, lon],
        icon=folium.DivIcon(
            html=pred_icon_html,
            icon_size=(30, 30),
            icon_anchor=(15, 15),
        ),
        tooltip=f"📍 Your Parcel — ₹{val_lakh:.1f}L/acre",
        popup=folium.Popup(popup_html, max_width=360),
    ).add_to(m)

    return m
