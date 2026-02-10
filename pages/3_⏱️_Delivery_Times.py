import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys, os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.data_loader import load_full_dataset

st.set_page_config(page_title="Delivery Times", page_icon="⏱️", layout="wide")
st.title("⏱️ Delivery Time Analysis")

df = load_full_dataset()

# ============================================
# DELIVERY CYCLE BREAKDOWN
# ============================================
st.markdown("### Cycle Time Breakdown")
st.markdown("""
The delivery cycle is made up of multiple stages.
Finding **where the most time is lost** is key to improving operations.
""")

# Compute averages for each time metric
time_metrics = {
    "Production Time": df["order_metric_production_time"].mean(),
    "Collected Time": df["order_metric_collected_time"].mean(),
    "Walking Time": df["order_metric_walking_time"].mean(),
    "Expedition Speed": df["order_metric_expediton_speed_time"].mean(),
    "Transit Time": df["order_metric_transit_time"].mean(),
}

time_df = (
    pd.DataFrame(list(time_metrics.items()), columns=["Stage", "Avg time (min)"])
    .sort_values("Avg time (min)", ascending=True)
)

# Remove NaNs and non-positive values
time_df = time_df[time_df["Avg time (min)"] > 0]

col1, col2 = st.columns([2, 1])

with col1:
    fig = px.bar(
        time_df,
        x="Avg time (min)",
        y="Stage",
        orientation="h",
        color="Avg time (min)",
        color_continuous_scale="Reds"
    )
    fig.update_layout(
        height=350,
        margin=dict(t=10),
        showlegend=False,
        coloraxis_showscale=False
    )
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.markdown("#### What does each stage mean?")
    st.markdown("""
    - **Production Time**: Time the store takes to prepare the order
    - **Collected Time**: Time until the driver picks up the order
    - **Walking Time**: Driver walking time to the pickup point
    - **Expedition Speed**: Dispatch/hand-off speed
    - **Transit Time**: Time in transit to the customer
    """)

st.divider()

# ============================================
# CYCLE TIME BY OPERATIONAL VARIABLES
# ============================================
st.markdown("### Cycle Time by operational drivers")

tab1, tab2, tab3, tab4 = st.tabs([
    "🚲 By vehicle", "🏪 By segment", "📱 By channel", "🏙️ By city"
])

with tab1:
    if "driver_modal" in df.columns:
        vehicle_time = df.groupby("driver_modal")["order_metric_cycle_time"].agg(
            ["mean", "median", "count"]
        ).reset_index()
        vehicle_time.columns = ["Vehicle", "Mean", "Median", "Orders"]
        vehicle_time = vehicle_time[vehicle_time["Orders"] > 100]  # Reduce noise

        fig = px.bar(
            vehicle_time.sort_values("Mean"),
            x="Vehicle",
            y=["Mean", "Median"],
            barmode="group",
            title="Average cycle time by vehicle type"
        )
        fig.update_layout(height=400, yaxis_title="Minutes")
        st.plotly_chart(fig, use_container_width=True)

        st.info("""
        💡 **Insight**: Compare mean vs median.
        If the mean is much higher than the median, outliers
        (very long deliveries) are pulling the average up.
        """)

with tab2:
    segment_time = df.groupby("store_segment")["order_metric_cycle_time"].agg(
        ["mean", "median", "count"]
    ).reset_index()
    segment_time.columns = ["Segment", "Mean", "Median", "Orders"]

    fig = px.bar(
        segment_time.sort_values("Mean"),
        x="Segment",
        y="Mean",
        color="Mean",
        color_continuous_scale="RdYlGn_r"
    )
    fig.update_layout(height=400, yaxis_title="Minutes", coloraxis_showscale=False)
    st.plotly_chart(fig, use_container_width=True)

with tab3:
    channel_time = df.groupby("channel_name")["order_metric_cycle_time"].agg(
        ["mean", "median", "count"]
    ).reset_index()
    channel_time.columns = ["Channel", "Mean", "Median", "Orders"]

    fig = px.bar(
        channel_time.sort_values("Mean"),
        x="Channel",
        y="Mean",
        color="Mean",
        color_continuous_scale="RdYlGn_r"
    )
    fig.update_layout(height=400, yaxis_title="Minutes", coloraxis_showscale=False)
    st.plotly_chart(fig, use_container_width=True)

with tab4:
    city_time = df.groupby("hub_city")["order_metric_cycle_time"].agg(
        ["mean", "median", "count"]
    ).reset_index()
    city_time.columns = ["City", "Mean", "Median", "Orders"]
    city_time = city_time[city_time["Orders"] > 500]  # Keep relevant cities

    fig = px.scatter(
        city_time,
        x="Orders",
        y="Mean",
        size="Orders",
        hover_name="City",
        title="Cities: volume vs cycle time"
    )
    fig.update_layout(
        height=450,
        xaxis_title="Order volume",
        yaxis_title="Cycle Time (min)"
    )
    st.plotly_chart(fig, use_container_width=True)

st.divider()

# ============================================
# CYCLE TIME DISTRIBUTION
# ============================================
st.markdown("### Cycle Time Distribution")

cycle_data = df["order_metric_cycle_time"].dropna()

# Remove extreme outliers for visualization
cycle_data = cycle_data[(cycle_data > 0) & (cycle_data < cycle_data.quantile(0.99))]

fig = px.histogram(
    cycle_data,
    nbins=50,
    title="Cycle Time distribution (extreme outliers removed)",
    labels={"value": "Cycle Time (min)", "count": "Frequency"}
)

fig.add_vline(
    x=cycle_data.mean(),
    line_dash="dash",
    line_color="red",
    annotation_text=f"Mean: {cycle_data.mean():.0f} min",
    annotation_position="top",
    annotation_xshift=20,
    annotation_yshift=10
)

fig.add_vline(
    x=cycle_data.median(),
    line_dash="dash",
    line_color="green",
    annotation_text=f"Median: {cycle_data.median():.0f} min",
    annotation_position="top",
    annotation_xshift=-20,
    annotation_yshift=30
)

fig.update_layout(height=400, showlegend=False)
st.plotly_chart(fig, use_container_width=True)