import streamlit as st
import pandas as pd
import plotly.express as px
import sys, os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.data_loader import load_full_dataset

st.set_page_config(page_title="Revenue", page_icon="💰", layout="wide")
st.title("💰 Revenue & Payment Analytics")

df = load_full_dataset()

# ============================================
# REVENUE KPIs
# ============================================
col1, col2, col3, col4 = st.columns(4)

with col1:
    total_revenue = df["order_amount"].sum()
    st.metric("Total Revenue", f"R$ {total_revenue:,.0f}")
with col2:
    total_fees = df["payment_fee"].sum()
    st.metric("Total Fees", f"R$ {total_fees:,.0f}")
with col3:
    avg_delivery_fee = df["order_delivery_fee"].mean()
    st.metric("Avg Delivery Fee", f"R$ {avg_delivery_fee:,.2f}")
with col4:
    avg_delivery_cost = df["order_delivery_cost"].mean()
    st.metric("Avg Delivery Cost", f"R$ {avg_delivery_cost:,.2f}")

st.divider()

# ============================================
# REVENUE BY DIMENSIONS
# ============================================
col1, col2 = st.columns(2)

with col1:
    st.markdown("#### Revenue by store segment")
    segment_rev = df.groupby("store_segment").agg(
        revenue=("order_amount", "sum"),
        orders=("order_id", "count"),
        avg_ticket=("order_amount", "mean")
    ).reset_index().sort_values("revenue", ascending=False)

    fig = px.bar(
        segment_rev,
        x="store_segment",
        y="revenue",
        color="avg_ticket",
        color_continuous_scale="Greens",
        hover_data=["orders", "avg_ticket"]
    )
    fig.update_layout(height=400, coloraxis_showscale=False)
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.markdown("#### Payment methods")
    payment_dist = df["payment_method"].value_counts().reset_index()
    payment_dist.columns = ["method", "count"]

    fig = px.pie(
        payment_dist,
        values="count",
        names="method",
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)

# ============================================
# UNIT ECONOMICS: FEE vs COST
# ============================================
st.markdown("### 📊 Unit Economics: Delivery Fee vs Delivery Cost")
st.markdown("""
**Is the marketplace profitable on delivery?**  
If the fee charged to the customer is higher than the delivery cost, the margin is positive.
""")

# Compute per-order margin
df["delivery_margin"] = df["order_delivery_fee"] - df["order_delivery_cost"]

col1, col2 = st.columns(2)

with col1:
    margin_positive = (df["delivery_margin"] > 0).sum()
    margin_negative = (df["delivery_margin"] <= 0).sum()
    total = margin_positive + margin_negative

    st.metric(
        "Orders with positive margin",
        f"{margin_positive / total * 100:.1f}%"
    )

with col2:
    avg_margin = df["delivery_margin"].mean()
    st.metric(
        "Avg margin per delivery",
        f"R$ {avg_margin:,.2f}",
        delta=f"{'Positive ✅' if avg_margin > 0 else 'Negative ⚠️'}"
    )

# Margin by city
city_margin = df.groupby("hub_city").agg(
    avg_margin=("delivery_margin", "mean"),
    total_orders=("order_id", "count")
).reset_index()
city_margin = city_margin[city_margin["total_orders"] > 500]

fig = px.scatter(
    city_margin,
    x="total_orders",
    y="avg_margin",
    size="total_orders",
    hover_name="hub_city",
    color="avg_margin",
    color_continuous_scale="RdYlGn",
    title="Delivery margin by city (cities with 500+ orders only)"
)
fig.add_hline(y=0, line_dash="dash", line_color="red")
fig.update_layout(
    height=500,
    xaxis_title="Order volume",
    yaxis_title="Avg margin (R$)"
)
st.plotly_chart(fig, use_container_width=True)