# Delivery Center Brazil

Streamlit dashboard analyzing 369,000+ orders from a delivery marketplace in Brazil. Covers operational efficiency, delivery times, geospatial distribution, and revenue across stores, drivers, and digital channels.

**Live app:** [delivery-center-dashboard-2026.streamlit.app](https://delivery-center-dashboard-2026.streamlit.app)

## Dataset

Seven relational tables (orders, stores, hubs, channels, deliveries, drivers, payments) with over 1.1 million rows total. Pre-aggregated before joining to prevent row duplication from one-to-many relationships.

Source: [Brazilian Delivery Center on Kaggle](https://www.kaggle.com/datasets/nosbielcs/brazilian-delivery-center), open license.

## Pages

**KPIs**: Marketplace metrics with filters by city, channel, and store segment. Order trends, status breakdown, and demand heatmap by hour and weekday.

**Geospatial**: Hub map with markers sized by order volume. State-level treemap comparing volume vs. cycle time.

**Delivery Times**: Cycle time decomposition across five stages (production, collection, walking, expedition, transit). Comparisons by vehicle, segment, channel, and city.

**Revenue**: Delivery fee vs. cost analysis. Revenue by store type and payment method. City-level margin scatter plot.

## Key Findings

- Store preparation time is the main bottleneck, not transit or driver availability.
- Several cities operate with negative delivery margins, suggesting volume-driven subsidization.
- Online payments represent ~88% of transactions.
- Demand peaks at 18:00-21:00 with a secondary lunch window.

## Tech Stack

Python, Pandas, Streamlit, Plotly, Folium, gdown

## Running Locally

```bash
git clone https://github.com/your-username/delivery-center-dashboard.git
cd delivery-center-dashboard
pip install -r requirements.txt
streamlit run app.py
```

## Author

[Julio Diaz de Leon](https://linkedin.com/in/juliomigueldiazdeleon)