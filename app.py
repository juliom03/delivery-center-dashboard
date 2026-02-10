import streamlit as st

# ==================================================
# PAGE SETUP
# ==================================================
st.set_page_config(
    page_title="Delivery Center Brazil — Dashboard",
    page_icon="📦", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================================================
# SIDEBAR
# ==================================================
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/delivery-scooter.png", width=80)
    st.title("Delivery Center")
    st.caption("Operational analysis of a delivery marketplace in Brazil")
    st.divider()
    st.markdown("**Built by:** [Julio Díaz de León](https://linkedin.com/in/juliomigueldiazdeleon)")
    st.markdown("**Dataset:** [Kaggle](https://www.kaggle.com/datasets/nosbielcs/brazilian-delivery-center)")
    st.divider()
    st.caption("Built with Streamlit and love · 2026")

# ==================================================
# MAIN CONTENT
# ==================================================
st.title("📦 Delivery Center Brazil")
st.markdown("### Operational analysis of a three-sided delivery marketplace")

st.markdown("""
> *This project shows an fast view of marketplace operations dataset."*
""")

st.divider()

# Project summary section
col1, col2 = st.columns(2)

with col1:
    st.markdown("#### 🧾 About the project")
    st.markdown("""
    This dashboard analyzes **370,000+ orders** from a delivery center in Brazil,
    focusing on operational efficiency in a marketplace that connects:

    - 🏪 **Stores** (restaurants and retail)
    - 🚴‍♂️ **Drivers** (bike, motorbike, car)
    - 📱 **Channels** (apps and platforms)
    """)

with col2:
    st.markdown("#### Business questions")
    st.markdown("""
    1. Where are the main **bottlenecks** in the delivery lifecycle?
    2. Which **hubs and cities** are most efficient?
    3. How does **vehicle type** impact cycle times?
    4. Which **channels** generate the most revenue?
    5. Where are the **best optimization opportunities**?
    """)

st.divider()

st.markdown("#### 👈 Use the sidebar to navigate")
st.markdown("""
| Page | Description |
|------|-------------|
| 📊 KPIs | Key metrics and marketplace overview |
| 🗺️ Geospatial | Maps for hubs, stores, and coverage |
| ⏱️ Delivery Times | Delivery lifecycle time analysis |
| 💳 Revenue | Revenue by channel, segment, and payment method |
""")