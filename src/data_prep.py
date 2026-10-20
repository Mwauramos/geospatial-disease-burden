# src/data_prep.py
# Kenya county shapefile loading and disease burden data preparation
# ZENIK.AI | Project 5: Geospatial Disease Burden Dashboard

import numpy as np
import pandas as pd
import geopandas as gpd
import requests
import zipfile
import io
import os

# 47 Kenya counties
KENYA_COUNTIES = [
    "Mombasa", "Kwale", "Kilifi", "Tana River", "Lamu", "Taita Taveta",
    "Garissa", "Wajir", "Mandera", "Marsabit", "Isiolo", "Meru",
    "Tharaka Nithi", "Embu", "Kitui", "Machakos", "Makueni", "Nyandarua",
    "Nyeri", "Kirinyaga", "Murang'a", "Kiambu", "Turkana", "West Pokot",
    "Samburu", "Trans Nzoia", "Uasin Gishu", "Elgeyo Marakwet", "Nandi",
    "Baringo", "Laikipia", "Nakuru", "Narok", "Kajiado", "Kericho",
    "Bomet", "Kakamega", "Vihiga", "Bungoma", "Busia", "Siaya",
    "Kisumu", "Homa Bay", "Migori", "Kisii", "Nyamira", "Nairobi"
]

DISEASES = ["Malaria", "Cholera", "Dengue", "Measles"]


def generate_county_burden(seed: int = 42) -> pd.DataFrame:
    """
    Generate synthetic annual disease burden per county.
    Returns incidence rate per 100,000 population for each disease.
    """
    np.random.seed(seed)

    # Population estimates (thousands) per county
    populations = {
        "Nairobi": 4500, "Kiambu": 2500, "Nakuru": 2100, "Kakamega": 1900,
        "Bungoma": 1700, "Meru": 1600, "Machakos": 1400, "Kisumu": 1300,
        "Kilifi": 1300, "Mombasa": 1200, "Uasin Gishu": 1100, "Murang'a": 1000,
        "Kericho": 950, "Trans Nzoia": 950, "Siaya": 920, "Homa Bay": 900,
        "Migori": 900, "Kisii": 880, "Nyeri": 860, "Kitui": 850,
    }

    records = []
    for county in KENYA_COUNTIES:
        pop = populations.get(county, np.random.randint(200, 800)) * 1000
        record = {"county": county, "population": pop}

        # Malaria: higher in lake region and coast
        if county in ["Kisumu", "Homa Bay", "Siaya", "Migori", "Kisii",
                      "Mombasa", "Kilifi", "Kwale", "Lamu"]:
            record["malaria_rate"] = np.random.uniform(150, 400)
        elif county in ["Garissa", "Wajir", "Mandera", "Turkana"]:
            record["malaria_rate"] = np.random.uniform(80, 200)
        else:
            record["malaria_rate"] = np.random.uniform(10, 80)

        # Cholera: higher in arid and semi-arid counties
        if county in ["Garissa", "Wajir", "Mandera", "Turkana", "Marsabit"]:
            record["cholera_rate"] = np.random.uniform(20, 60)
        else:
            record["cholera_rate"] = np.random.uniform(0.5, 15)

        # Dengue: coastal counties
        if county in ["Mombasa", "Kilifi", "Kwale", "Lamu", "Tana River"]:
            record["dengue_rate"] = np.random.uniform(15, 50)
        else:
            record["dengue_rate"] = np.random.uniform(0.1, 8)

        # Measles: higher in remote/low-vaccination counties
        if county in ["Turkana", "Marsabit", "Mandera", "Wajir", "Garissa"]:
            record["measles_rate"] = np.random.uniform(10, 35)
        else:
            record["measles_rate"] = np.random.uniform(0.5, 10)

        # Composite burden score (weighted average)
        record["burden_score"] = (
            0.4 * record["malaria_rate"] +
            0.3 * record["cholera_rate"] +
            0.2 * record["dengue_rate"] +
            0.1 * record["measles_rate"]
        )

        records.append(record)

    return pd.DataFrame(records)


def load_kenya_shapefile(data_dir: str = "data") -> gpd.GeoDataFrame:
    """
    Load Kenya county shapefile. Downloads from geoBoundaries if not cached.
    Returns GeoDataFrame with county geometries.
    """
    shapefile_path = os.path.join(data_dir, "kenya_counties.gpkg")

    if os.path.exists(shapefile_path):
        return gpd.read_file(shapefile_path)

    os.makedirs(data_dir, exist_ok=True)
    print("Downloading Kenya shapefile from geoBoundaries...")

    url = "https://github.com/wmgeolab/geoBoundaries/raw/main/releaseData/gbOpen/KEN/ADM1/geoBoundaries-KEN-ADM1.geojson"
    response = requests.get(url, timeout=30)
    response.raise_for_status()

    gdf = gpd.read_file(io.BytesIO(response.content))
    gdf = gdf.rename(columns={"shapeName": "county"})
    gdf = gdf[["county", "geometry"]]
    gdf.to_file(shapefile_path, driver="GPKG")
    print(f"Saved shapefile to {shapefile_path}")
    return gdf


def build_geodataframe(data_dir: str = "data") -> gpd.GeoDataFrame:
    """
    Merge Kenya shapefile with disease burden data.
    Returns merged GeoDataFrame ready for mapping.
    """
    gdf = load_kenya_shapefile(data_dir)
    burden_df = generate_county_burden()

    # Normalise county names for merging
    gdf["county_key"] = gdf["county"].str.strip().str.title()
    burden_df["county_key"] = burden_df["county"].str.strip().str.title()

    merged = gdf.merge(burden_df, on="county_key", how="left")
    merged = merged.drop(columns=["county_key"])
    merged = merged.rename(columns={"county_x": "county"})

    # Fill missing burden data with median
    for col in ["malaria_rate", "cholera_rate", "dengue_rate",
                "measles_rate", "burden_score"]:
        merged[col] = merged[col].fillna(merged[col].median())

    return merged


if __name__ == "__main__":
    gdf = build_geodataframe()
    print(f"GeoDataFrame shape: {gdf.shape}")
    print(gdf[["county", "malaria_rate", "burden_score"]].head(10))