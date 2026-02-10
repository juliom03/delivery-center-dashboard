import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import plotly.express as px
import sys, os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.data_loader import load_hubs, load_stores, load_full_dataset

st.set_page_config(page_title="Geospatial", page_icon="🗺️", layout="wide")
st.title("🗺️ Geospatial Analysis")

hubs = load_hubs()
stores = load_stores()
df = load_full_dataset()

# ============================================
# HUB MAP
# ============================================
st.markdown("### Logistics Hub Map")

# Map center (Brazil)
center_lat = hubs["hub_latitude"].mean()
center_lon = hubs["hub_longitude"].mean()

m = folium.Map(location=[center_lat, center_lon], zoom_start=5, tiles="CartoDB positron")

# Add hubs as markers
for _, hub in hubs.iterrows():
    if pd.notna(hub["hub_latitude"]) and pd.notna(hub["hub_longitude"]):
        # Count orders per hub
        hub_orders = df[df["hub_id"] == hub["hub_id"]].shape[0]

        folium.CircleMarker(
            location=[hub["hub_latitude"], hub["hub_longitude"]],
            radius=max(3, min(hub_orders / 1000, 20)),  # Proportional size
            popup=f"""
                <b>{hub['hub_name']}</b><br>
                City: {hub['hub_city']}<br>
                State: {hub['hub_state']}<br>
                Orders: {hub_orders:,}
            """,
            color="#e74c3c",
            fill=True,
            fill_opacity=0.7
        ).add_to(m)

st_folium(m, width=None, height=500)

# ============================================
# STATE-LEVEL METRICS
# ============================================
st.markdown("### Performance by State")

state_metrics = df.groupby("hub_state").agg(
    total_orders=("order_id", "count"),
    avg_cycle_time=("order_metric_cycle_time", "mean"),
    avg_amount=("order_amount", "mean"),
    total_stores=("store_id", "nunique"),
    total_hubs=("hub_id", "nunique")
).reset_index().sort_values("total_orders", ascending=False)

fig = px.treemap(
    state_metrics,
    path=["hub_state"],
    values="total_orders",
    color="avg_cycle_time",
    color_continuous_scale="RdYlGn_r",
    title="States: size = volume, color = avg cycle time"
)
fig.update_layout(height=500, margin=dict(t=40))
st.plotly_chart(fig, use_container_width=True)

# Summary table
st.markdown("### State summary")
st.dataframe(
    state_metrics.style.format({
        "total_orders": "{:,.0f}",
        "avg_cycle_time": "{:.1f} min",
        "avg_amount": "R$ {:.2f}",
        "total_stores": "{:,.0f}",
        "total_hubs": "{:,.0f}"
    }),
    use_container_width=True,
    hide_index=True
)