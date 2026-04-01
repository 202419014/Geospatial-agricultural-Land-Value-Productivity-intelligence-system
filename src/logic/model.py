"""Random Forest model for agricultural land value prediction."""
import numpy as np
import pandas as pd
import pickle
from pathlib import Path
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_absolute_error
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.data_loader import load_land_values, get_scaled_soil_params
from utils.feature_extraction import extract_features_for_point, features_to_model_array

MODEL_PATH = Path(__file__).parent.parent.parent / "data" / "rf_model.pkl"

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
    "road_accessibility",
    "soil_fertility_score",
]


def build_training_data():
    """Build training dataset from known land value points."""
    df = load_land_values()
    rows = []
    for _, row in df.iterrows():
        feats = extract_features_for_point(row["latitude"], row["longitude"])
        # Default user-input features based on proximity/soil (heuristic for training)
        dist_city = feats["dist_city_km"]
        road_acc = max(1, min(5, round(5 - dist_city / 8)))
        ph = feats.get("pH", 7.0) or 7.0
        oc = feats.get("organic_carbon_pct", 1.0) or 1.0
        soil_fertility = max(1, min(5, round((ph / 8.5 + oc / 2.0) * 2.5)))
        feats["road_accessibility"] = road_acc
        feats["soil_fertility_score"] = soil_fertility
        feats["target"] = row["rate_per_acre_inr"]
        rows.append(feats)
    return pd.DataFrame(rows)


def train_model(force_retrain=False):
    """Train RF model and cache it. Returns (model, feature_importances)."""
    if MODEL_PATH.exists() and not force_retrain:
        with open(MODEL_PATH, "rb") as f:
            return pickle.load(f)

    df = build_training_data()

    X = df[FEATURE_ORDER].fillna(df[FEATURE_ORDER].median())
    y = df["target"]

    model = RandomForestRegressor(
        n_estimators=200,
        max_depth=8,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1,
    )
    model.fit(X, y)

    importances = dict(zip(FEATURE_ORDER, model.feature_importances_))

    result = {"model": model, "importances": importances, "feature_order": FEATURE_ORDER}
    with open(MODEL_PATH, "wb") as f:
        pickle.dump(result, f)

    return result


def predict_land_value(features: dict) -> dict:
    """
    Predict land value for a set of features.
    Returns prediction and explanation.
    """
    trained = train_model()
    model = trained["model"]
    importances = trained["importances"]

    X, feat_names = features_to_model_array(features)
    # Use DataFrame to avoid feature name warnings
    X_df = pd.DataFrame(X, columns=feat_names)
    pred = model.predict(X_df)[0]

    # Feature contributions (importance * feature value normalized)
    feat_vals = X[0]
    contributions = {}
    for name, val in zip(feat_names, feat_vals):
        imp = importances.get(name, 0)
        contributions[name] = {"importance": round(imp * 100, 1), "value": val}

    # Sort by importance
    sorted_contribs = sorted(contributions.items(), key=lambda x: -x[1]["importance"])

    return {
        "predicted_value_inr": round(pred),
        "predicted_value_lakh": round(pred / 100000, 2),
        "contributions": dict(sorted_contribs),
    }


def predict_all_known_points():
    """Predict land values for all known agricultural points (for map display)."""
    trained = train_model()
    model = trained["model"]

    df = load_land_values()
    results = []
    for _, row in df.iterrows():
        feats = extract_features_for_point(row["latitude"], row["longitude"])
        dist_city = feats["dist_city_km"]
        road_acc = max(1, min(5, round(5 - dist_city / 8)))
        ph = feats.get("pH", 7.0) or 7.0
        oc = feats.get("organic_carbon_pct", 1.0) or 1.0
        soil_fertility = max(1, min(5, round((ph / 8.5 + oc / 2.0) * 2.5)))
        feats["road_accessibility"] = road_acc
        feats["soil_fertility_score"] = soil_fertility

        pred_result = predict_land_value(feats)
        results.append({
            **row.to_dict(),
            **feats,
            "predicted_value_inr": pred_result["predicted_value_inr"],
            "predicted_value_lakh": pred_result["predicted_value_lakh"],
            "contributions": pred_result["contributions"],
        })
    return pd.DataFrame(results)


def get_price_tier(value_inr: float) -> tuple:
    """Return color and label for a land value."""
    lakh = value_inr / 100000
    if lakh >= 60:
        return "#d73027", "Very High (≥60L)"
    elif lakh >= 45:
        return "#fc8d59", "High (45–60L)"
    elif lakh >= 35:
        return "#fee08b", "Medium-High (35–45L)"
    elif lakh >= 25:
        return "#91cf60", "Medium (25–35L)"
    else:
        return "#1a9850", "Low (<25L)"
