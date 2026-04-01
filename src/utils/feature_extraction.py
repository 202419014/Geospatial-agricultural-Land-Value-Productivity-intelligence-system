"""Geospatial feature extraction for land value prediction."""
import numpy as np
import pandas as pd
from math import radians, sin, cos, sqrt, atan2
from shapely.geometry import Point, Polygon
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.data_loader import load_mandis, load_apmc_markets, get_scaled_soil_params


def haversine_km(lat1, lon1, lat2, lon2):
    """Compute distance in km between two lat/lon points."""
    R = 6371.0
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    return R * 2 * atan2(sqrt(a), sqrt(1 - a))


def distance_to_nearest_market(lat: float, lon: float) -> dict:
    """Find distance to nearest mandi and APMC market."""
    mandis = load_mandis()
    apmc = load_apmc_markets()

    mandi_dists = mandis.apply(
        lambda r: haversine_km(lat, lon, r["latitude"], r["longitude"]), axis=1
    )
    apmc_dists = apmc.apply(
        lambda r: haversine_km(lat, lon, r["Latitude"], r["Longitude"]), axis=1
    )

    nearest_mandi_idx = mandi_dists.idxmin()
    nearest_apmc_idx = apmc_dists.idxmin()

    return {
        "dist_nearest_mandi_km": round(mandi_dists.min(), 2),
        "nearest_mandi_name": mandis.loc[nearest_mandi_idx, "market"],
        "dist_nearest_apmc_km": round(apmc_dists.min(), 2),
        "nearest_apmc_name": apmc.loc[nearest_apmc_idx, "Market"],
    }


def extract_features_for_point(
    lat: float,
    lon: float,
    user_inputs: dict = None,
) -> dict:
    """
    Extract all features for a point needed for land value prediction.
    user_inputs can override/supplement raster-derived values.
    """
    soil = get_scaled_soil_params(lat, lon)
    market = distance_to_nearest_market(lat, lon)

    # Ludhiana city center for urban proximity
    city_lat, city_lon = 30.9010, 75.8573
    dist_city = haversine_km(lat, lon, city_lat, city_lon)

    features = {
        "latitude": lat,
        "longitude": lon,
        "dist_city_km": round(dist_city, 2),
        **soil,
        **market,
    }

    # Merge user inputs (sliders/dropdowns override defaults)
    if user_inputs:
        features.update(user_inputs)

    return features


def features_to_model_array(features: dict) -> np.ndarray:
    """Convert feature dict to model input array (must match training order)."""
    FEATURE_ORDER = [
        "dist_city_km",
        "dist_nearest_mandi_km",
        "dist_nearest_apmc_km",
        "clay_pct",
        "sand_pct",
        "silt_pct",
        "pH",
        "nitrogen_mg_kg",
        "organic_carbon_pct",
        "irrigation_index",
        "road_accessibility",   # 1-5 user input
        "soil_fertility_score", # 1-5 user input
    ]
    row = []
    for k in FEATURE_ORDER:
        val = features.get(k, 0)
        if val is None or (isinstance(val, float) and np.isnan(val)):
            val = 0.0
        row.append(float(val))
    return np.array(row).reshape(1, -1), FEATURE_ORDER


def compute_polygon_centroid(geojson_polygon: dict):
    """Return centroid lat/lon of a drawn polygon."""
    try:
        poly = shape(geojson_polygon)
        centroid = poly.centroid
        return centroid.y, centroid.x  # lat, lon
    except Exception:
        return None, None
