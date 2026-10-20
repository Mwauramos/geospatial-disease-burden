# src/spatial_analysis.py
# Spatial autocorrelation analysis using PySAL
# ZENIK.AI | Project 5: Geospatial Disease Burden Dashboard

import numpy as np
import pandas as pd
import geopandas as gpd
from libpysal.weights import Queen
from esda.moran import Moran, Moran_Local


def build_weights(gdf: gpd.GeoDataFrame) -> Queen:
    gdf_projected = gdf.to_crs(epsg=21037)
    w = Queen.from_dataframe(gdf_projected, silence_warnings=True)
    w.transform = "r"
    return w


def global_moran(gdf: gpd.GeoDataFrame, column: str, w: Queen) -> dict:
    y = gdf[column].fillna(gdf[column].median()).values
    moran = Moran(y, w, permutations=999)
    return {
        "column": column,
        "morans_i": round(moran.I, 4),
        "p_value": round(moran.p_sim, 4),
        "z_score": round(moran.z_sim, 4),
        "significant": moran.p_sim < 0.05,
        "interpretation": interpret_moran(moran.I, moran.p_sim)
    }


def interpret_moran(I: float, p: float) -> str:
    if p >= 0.05:
        return "No significant spatial clustering (random distribution)"
    if I > 0.3:
        return "Strong positive spatial clustering"
    if I > 0.1:
        return "Moderate positive spatial clustering"
    if I < -0.1:
        return "Negative spatial autocorrelation"
    return "Weak spatial pattern"


def local_moran(gdf: gpd.GeoDataFrame, column: str, w: Queen) -> gpd.GeoDataFrame:
    gdf = gdf.copy()
    y = gdf[column].fillna(gdf[column].median()).values
    lisa = Moran_Local(y, w, permutations=999, seed=42)

    gdf["lisa_ii"] = lisa.Is
    gdf["lisa_p"] = lisa.p_sim
    gdf["lisa_significant"] = lisa.p_sim < 0.05

    # Compute spatial lag manually using weights
    n = len(y)
    lag = np.zeros(n)
    for i in range(n):
        neighbors = list(w.neighbors[i])
        if neighbors:
            weights = [w.weights[i][j] for j, _ in enumerate(neighbors)]
            lag[i] = np.dot(weights, y[neighbors])

    y_std = (y - y.mean()) / (y.std() + 1e-9)
    lag_std = (lag - lag.mean()) / (lag.std() + 1e-9)

    conditions = [
        (y_std > 0) & (lag_std > 0),
        (y_std < 0) & (lag_std < 0),
        (y_std > 0) & (lag_std < 0),
        (y_std < 0) & (lag_std > 0),
    ]
    labels = ["HH", "LL", "HL", "LH"]
    gdf["lisa_quad"] = "NS"
    for cond, label in zip(conditions, labels):
        gdf.loc[cond & gdf["lisa_significant"], "lisa_quad"] = label

    return gdf


def run_full_spatial_analysis(gdf: gpd.GeoDataFrame) -> dict:
    w = build_weights(gdf)
    columns = ["malaria_rate", "cholera_rate", "dengue_rate",
               "measles_rate", "burden_score"]

    global_results = []
    for col in columns:
        result = global_moran(gdf, col, w)
        global_results.append(result)

    global_df = pd.DataFrame(global_results)
    gdf_lisa = local_moran(gdf, "burden_score", w)

    return {
        "weights": w,
        "global_df": global_df,
        "gdf_lisa": gdf_lisa
    }


if __name__ == "__main__":
    import sys
    sys.path.append(".")
    from src.data_prep import build_geodataframe

    gdf = build_geodataframe()
    results = run_full_spatial_analysis(gdf)
    print(results["global_df"].to_string(index=False))