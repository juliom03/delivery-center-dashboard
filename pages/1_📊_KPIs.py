import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys
import os

# Allow importing utils from the project root (from inside /pages)
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.data_loader import load_full_dataset, load_orders

st.set_page_config(page_title="KPIs", page_icon="📊", layout="wide")
st.title("📊 Marketplace KPIs")

# Load data
df = load_full_dataset()
orders = load_orders()

# ============================================
# SIDEBAR FILTERS
# ============================================
with st.sidebar:
    st.header("Filters")

    # City filter
    cities = ["All"] + sorted(df["hub_city"].dropna().unique().tolist())
    city_sel = st.selectbox("City", cities)

    # Channel filter
    channels = ["All"] + sorted(df["channel_name"].dropna().unique().tolist())
    channel_sel = st.selectbox("Channel", channels)

    # Store segment filter
    segments = ["All"] + sorted(df["store_segment"].dropna().unique().tolist())
    segment_sel = st.selectbox("Segment", segments)

# Apply filters
df_filtered = df.copy()
if city_sel != "All":
    df_filtered = df_filtered[df_filtered["hub_city"] == city_sel]
if channel_sel != "All":
    df_filtered = df_filtered[df_filtered["channel_name"] == channel_sel]
if segment_sel != "All":
    df_filtered = df_filtered[df_filtered["store_segment"] == segment_sel]

# ============================================
# KEY METRICS (KPI CARDS)
# ============================================
st.markdown("### Overview")

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric("Total Orders", f"{df_filtered['order_id'].nunique():,}")
with col2:
    st.metric("Active Stores", f"{df_filtered['store_id'].nunique():,}")
with col3:
    st.metric("Hubs", f"{df_filtered['hub_id'].nunique():,}")
with col4:
    avg_amount = df_filtered["order_amount"].mean()
    st.metric("Avg Ticket", f"R$ {avg_amount:,.2f}")
with col5:
    avg_cycle = df_filtered["order_metric_cycle_time"].mean()
    st.metric("Avg Cycle Time", f"{avg_cycle:,.0f} min")

st.divider()

# ============================================
# CHARTS
# ============================================

# Row 1: Orders over time + Order status
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("#### Orders by month")

    # Group by year-month
    orders_time = (
    df_filtered.groupby(['order_created_year', 'order_created_month'])['order_id']
    .nunique()
    .reset_index(name='total_orders')
    )
    

    orders_time["date"] = pd.to_datetime(
        orders_time["order_created_year"].astype(str)
        + "-"
        + orders_time["order_created_month"].astype(str).str.zfill(2)
        + "-01"
    )

    fig = px.line(
        orders_time.sort_values("date"),
        x="date",
        y="total_orders",
        markers=True
    )
    fig.update_layout(
        xaxis_title="",
        yaxis_title="Orders",
        height=350,
        margin=dict(t=10)
    )
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.markdown("#### Order status")
    status_counts = df_filtered["order_status"].value_counts().reset_index()
    status_counts.columns = ["status", "count"]

    fig = px.pie(
        status_counts,
        values="count",
        names="status",
        color_discrete_sequence=px.colors.qualitative.Set2
    )
    fig.update_layout(height=350, margin=dict(t=10))
    st.plotly_chart(fig, use_container_width=True)

# Row 2: Top cities + Channels
col1, col2 = st.columns(2)

with col1:
    st.markdown("#### Top 10 cities by order volume")
    top_cities = (
        df_filtered.groupby("hub_city")
        .size()
        .nlargest(10)
        .reset_index(name="orders")
    )

    fig = px.bar(
        top_cities,
        x="orders",
        y="hub_city",
        orientation="h",
        color="orders",
        color_continuous_scale="Blues"
    )
    fig.update_layout(
        yaxis={"categoryorder": "total ascending"},
        height=400,
        margin=dict(t=10),
        xaxis_title="Orders",
        yaxis_title="",
        showlegend=False,
        coloraxis_showscale=False
    )
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.markdown("#### Order volume by channel")
    channel_data = df_filtered.groupby("channel_name").size().reset_index(name="orders")

    fig = px.bar(
        channel_data.sort_values("orders", ascending=False),
        x="channel_name",
        y="orders",
        color="channel_name",
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    fig.update_layout(
        height=400,
        margin=dict(t=10),
        xaxis_title="",
        yaxis_title="Orders",
        showlegend=False
    )
    st.plotly_chart(fig, use_container_width=True)

# Row 3: Heatmap of orders by hour and weekday
st.markdown("#### Heatmap: Orders by hour of day and day of week")

# Create day-of-week column
df_filtered["day_of_week"] = df_filtered["order_moment_created"].dt.day_name()
heatmap_data = (
    df_filtered.groupby(["day_of_week", "order_created_hour"])
    .size()
    .reset_index(name="orders")
)

# Pivot to matrix format
day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
heatmap_pivot = (
    heatmap_data.pivot(index="day_of_week", columns="order_created_hour", values="orders")
    .reindex(day_order)
    .fillna(0)
)

fig = px.imshow(
    heatmap_pivot,
    labels=dict(x="Hour of day", y="Day", color="Orders"),
    color_continuous_scale="YlOrRd",
    aspect="auto"
)
fig.update_layout(height=350, margin=dict(t=10))
st.plotly_chart(fig, use_container_width=True)