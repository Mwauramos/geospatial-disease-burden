# app.py
# Streamlit dashboard — Geospatial Disease Burden
# ZENIK.AI | Project 5

import sys
sys.path.append(".")

import streamlit as st
import plotly.express as px
from streamlit_folium import st_folium

from src.data_prep import build_geodataframe
from src.spatial_analysis import run_full_spatial_analysis
from src.visualisation import choropleth_map, lisa_map, bar_chart_data

st.set_page_config(
    page_title="Geospatial Disease Burden | ZENIK.AI",
    page_icon="🗺️",
    layout="wide"
)

@st.cache_data
def load_data():
    gdf = build_geodataframe()
    results = run_full_spatial_analysis(gdf)
    return gdf, results

with st.spinner("Loading Kenya county data and running spatial analysis..."):
    gdf, results = load_data()

gdf_lisa = results["gdf_lisa"]
global_df = results["global_df"]

st.title("🗺️ Kenya Geospatial Disease Burden Dashboard")

st.sidebar.header("Controls")
disease_options = {
    "Overall Burden Score": "burden_score",
    "Malaria (per 100k)": "malaria_rate",
    "Cholera (per 100k)": "cholera_rate",
    "Dengue (per 100k)": "dengue_rate",
    "Measles (per 100k)": "measles_rate",
}
selected_label = st.sidebar.selectbox("Disease / Indicator", list(disease_options.keys()))
selected_col = disease_options[selected_label]
top_n = st.sidebar.slider("Top N counties (bar chart)", 5, 47, 10)

k1, k2, k3, k4 = st.columns(4)
k1.metric("Counties", len(gdf))
k2.metric("Hotspots (HH)", int((gdf_lisa["lisa_quad"] == "HH").sum()))
k3.metric("Cold Spots (LL)", int((gdf_lisa["lisa_quad"] == "LL").sum()))
sig_row = global_df[global_df["column"] == selected_col]
if not sig_row.empty:
    mi = sig_row.iloc[0]["morans_i"]
    pv = sig_row.iloc[0]["p_value"]
    k4.metric("Global Moran's I", f"{mi:.3f}", f"p={pv:.3f}")

st.divider()

col_map, col_lisa = st.columns(2)

with col_map:
    st.subheader(f"Choropleth: {selected_label}")
    m_choro = choropleth_map(gdf, selected_col, selected_label)
    st_folium(m_choro, width=520, height=430, returned_objects=[])

with col_lisa:
    st.subheader("LISA Cluster Map (Burden Score)")
    m_lisa = lisa_map(gdf_lisa)
    st_folium(m_lisa, width=520, height=430, returned_objects=[])

st.divider()

st.subheader(f"Top {top_n} Counties by {selected_label}")
bar_df = bar_chart_data(gdf, selected_col, top_n)
fig = px.bar(
    bar_df,
    x=selected_col,
    y="county",
    orientation="h",
    color=selected_col,
    color_continuous_scale="YlOrRd",
    labels={"county": "County", selected_col: selected_label},
)
fig.update_layout(
    yaxis=dict(autorange="reversed"),
    coloraxis_showscale=False,
    margin=dict(l=10, r=10, t=10, b=10),
    height=380,
)
st.plotly_chart(fig, use_container_width=True)

st.divider()

st.subheader("Global Moran's I — All Indicators")
display_df = global_df[["column", "morans_i", "p_value", "significant", "interpretation"]].copy()
display_df.columns = ["Indicator", "Moran's I", "p-value", "Significant", "Interpretation"]
st.dataframe(display_df, use_container_width=True, hide_index=True)

st.subheader("LISA Cluster Summary")
quad_counts = gdf_lisa["lisa_quad"].value_counts().reset_index()
quad_counts.columns = ["Cluster Type", "Count"]
labels = {"HH": "Hotspot", "LL": "Cold Spot", "HL": "High Outlier",
          "LH": "Low Outlier", "NS": "Not Significant"}
quad_counts["Cluster Type"] = quad_counts["Cluster Type"].map(labels)
fig2 = px.pie(quad_counts, values="Count", names="Cluster Type",
              color="Cluster Type",
              color_discrete_map={
                  "Hotspot": "#d7191c", "Cold Spot": "#2c7bb6",
                  "High Outlier": "#fdae61", "Low Outlier": "#abd9e9",
                  "Not Significant": "#eeeeee"
              })
fig2.update_layout(margin=dict(l=0, r=0, t=20, b=0), height=300)
st.plotly_chart(fig2, use_container_width=True)

st.caption("Data: Synthetic Kenya county-level disease burden | ZENIK.AI 2024")