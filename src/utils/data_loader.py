"""Data loading utilities for the agricultural land value system."""
import json
import numpy as np
import pandas as pd
import geopandas as gpd
import rasterio
from rasterio.sample import sample_gen
from shapely.geometry import Point, shape
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent.parent / "data"


def load_land_values():
    """Load agricultural land value points from GeoJSON."""
    path = DATA_DIR / "ludhiana_land_values.geojson"
    with open(path) as f:
        gj = json.load(f)
    records = []
    for feat in gj["features"]:
        props = feat["properties"]
        if props.get("land_type") == "Agricultural":
            records.append({
                "village_name": props["village_name"],
                "tehsil": props["tehsil"],
                "land_type": props["land_type"],
                "rate_per_acre_inr": props["rate_per_acre_inr"],
                "latitude": props["latitude"],
                "longitude": props["longitude"],
            })
    df = pd.DataFrame(records)
    return df


def load_mandis():
    """Load mandi (market) locations."""
    path = DATA_DIR / "ludhiana_mandis.geojson"
    with open(path) as f:
        gj = json.load(f)
    records = []
    for feat in gj["features"]:
        props = feat["properties"]
        records.append({
            "market": props["Market"],
            "latitude": props["Latitude"],
            "longitude": props["Longitude"],
        })
    return pd.DataFrame(records)


def load_apmc_markets():
    """Load APMC market locations."""
    path = DATA_DIR / "ludhiana_apmc_markets_lat_long.csv"
    return pd.read_csv(path)


def sample_raster_at_point(raster_path: Path, lat: float, lon: float) -> float:
    """Sample a raster value at a given lat/lon. Returns NaN if outside bounds."""
    try:
        with rasterio.open(raster_path) as src:
            coords = [(lon, lat)]
            vals = list(sample_gen(src, coords))
            val = float(vals[0][0])
            if src.nodata is not None and val == src.nodata:
                return np.nan
            return val
    except Exception:
        return np.nan


def get_soil_params_at_point(lat: float, lon: float) -> dict:
    """Extract all soil and environmental raster values at a point."""
    rasters = {
        "clay": DATA_DIR / "ludhiana_clay.tif",
        "nitrogen": DATA_DIR / "ludhiana_nitrogen.tif",
        "organic_carbon": DATA_DIR / "ludhiana_organic_carbon.tif",
        "pH": DATA_DIR / "ludhiana_pH.tif",
        "sand": DATA_DIR / "ludhiana_sand.tif",
        "silt": DATA_DIR / "ludhiana_silt.tif",
        "irrigation_modis": DATA_DIR / "ludhiana_irrigation_modis.tif",
    }
    result = {}
    for name, path in rasters.items():
        val = sample_raster_at_point(path, lat, lon)
        result[name] = val
    return result


def get_scaled_soil_params(lat: float, lon: float) -> dict:
    """Get soil params scaled to meaningful units (SoilGrids uses * 10 encoding)."""
    raw = get_soil_params_at_point(lat, lon)
    scaled = {}
    # SoilGrids convention: clay/sand/silt in g/kg (*10), pH in pH*10, N in cg/kg, OC in dg/kg
    scaled["clay_pct"] = raw["clay"] / 10.0 if not np.isnan(raw["clay"]) else np.nan
    scaled["sand_pct"] = raw["sand"] / 10.0 if not np.isnan(raw["sand"]) else np.nan
    scaled["silt_pct"] = raw["silt"] / 10.0 if not np.isnan(raw["silt"]) else np.nan
    scaled["pH"] = raw["pH"] / 10.0 if not np.isnan(raw["pH"]) else np.nan
    scaled["nitrogen_mg_kg"] = raw["nitrogen"] / 100.0 if not np.isnan(raw["nitrogen"]) else np.nan
    scaled["organic_carbon_pct"] = raw["organic_carbon"] / 100.0 if not np.isnan(raw["organic_carbon"]) else np.nan
    scaled["irrigation_index"] = raw["irrigation_modis"] if not np.isnan(raw.get("irrigation_modis", np.nan)) else np.nan
    return scaled
