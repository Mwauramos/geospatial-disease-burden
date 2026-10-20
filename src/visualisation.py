# src/visualisation.py
# Choropleth and LISA cluster maps using Folium
# ZENIK.AI | Project 5: Geospatial Disease Burden Dashboard

import folium
import numpy as np
import geopandas as gpd
from folium.plugins import Fullscreen
import branca.colormap as cm


LISA_COLORS = {
    "HH": "#d7191c",
    "LL": "#2c7bb6",
    "HL": "#fdae61",
    "LH": "#abd9e9",
    "NS": "#eeeeee",
}

LISA_LABELS = {
    "HH": "Hotspot (High-High)",
    "LL": "Cold spot (Low-Low)",
    "HL": "High outlier (High-Low)",
    "LH": "Low outlier (Low-High)",
    "NS": "Not significant",
}


def choropleth_map(gdf: gpd.GeoDataFrame, column: str,
                   title: str = "Disease Burden") -> folium.Map:
    gdf = gdf.to_crs(epsg=4326).copy()
    center = [0.0236, 37.9062]

    m = folium.Map(location=center, zoom_start=6,
                   tiles="OpenStreetMap")
    Fullscreen().add_to(m)

    values = gdf[column].fillna(0)
    colormap = cm.linear.YlOrRd_09.scale(values.min(), values.max())
    colormap.caption = title
    colormap.add_to(m)

    for _, row in gdf.iterrows():
        val = row[column] if not np.isnan(row[column]) else 0
        folium.GeoJson(
            row["geometry"].__geo_interface__,
            style_function=lambda feat, v=val: {
                "fillColor": colormap(v),
                "color": "#333333",
                "weight": 0.8,
                "fillOpacity": 0.75,
            },
            tooltip=folium.Tooltip(
                f"<b>{row['county']}</b><br>{title}: {val:,.1f}"
            ),
        ).add_to(m)

    return m


def lisa_map(gdf: gpd.GeoDataFrame) -> folium.Map:
    gdf = gdf.to_crs(epsg=4326).copy()
    center = [0.0236, 37.9062]

    m = folium.Map(location=center, zoom_start=6,
                   tiles="OpenStreetMap")
    Fullscreen().add_to(m)

    for _, row in gdf.iterrows():
        quad = row.get("lisa_quad", "NS")
        folium.GeoJson(
            row["geometry"].__geo_interface__,
            style_function=lambda feat, q=quad: {
                "fillColor": LISA_COLORS.get(q, "#eeeeee"),
                "color": "#333333",
                "weight": 0.8,
                "fillOpacity": 0.8,
            },
            tooltip=folium.Tooltip(
                f"<b>{row['county']}</b><br>"
                f"Cluster: {LISA_LABELS.get(quad, quad)}<br>"
                f"Burden score: {row.get('burden_score', 0):,.1f}"
            ),
        ).add_to(m)

    legend_html = """
    <div style="position:fixed;bottom:30px;left:30px;z-index:1000;
         background:white;padding:12px;border-radius:6px;
         border:1px solid #ccc;font-size:12px;line-height:2;">
    <b style="color:#000000;">LISA Cluster Type</b><br>
    """
    for code, color in LISA_COLORS.items():
        label = LISA_LABELS[code]
        legend_html += (
            f'<span style="background:{color};display:inline-block;'
            f'width:14px;height:14px;margin-right:6px;'
            f'border:1px solid #999;vertical-align:middle;"></span>'
            f'<span style="color:#000000;">{label}</span><br>'
        )
    legend_html += "</div>"
    m.get_root().html.add_child(folium.Element(legend_html))

    return m


def bar_chart_data(gdf: gpd.GeoDataFrame, column: str, top_n: int = 10):
    return (
        gdf[["county", column]]
        .dropna()
        .sort_values(column, ascending=False)
        .head(top_n)
        .reset_index(drop=True)
    )