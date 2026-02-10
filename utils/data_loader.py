import streamlit as st
import pandas as pd
from pathlib import Path
import gdown
import os

# Path Configuration
BASE_DIR = Path(__file__).resolve().parents[1]
LOCAL_DATA_DIR = BASE_DIR / "data"
CACHE_DATA_DIR = BASE_DIR / "data_cache"

# Ensure the cache directory exists
CACHE_DATA_DIR.mkdir(parents=True, exist_ok=True)

ENCODING = "latin-1"

# Google Drive File IDs
GDRIVE_FILES = {
    "orders.csv": "1_xETc5dummDrBqwStB0bVEgpJd8Y-kpl",
    "stores.csv": "12m8cV5bgbilWfDGKD5l3Tungvmt3aq_D",
    "hubs.csv": "1SPwz8GttbQjOP9JdqKhzeJv56KB1xSzy",
    "deliveries.csv": "1z5ZpuXekP9Xy2Rw3mB7Cld3wC2M-vI2e",
    "drivers.csv": "1EeecFK-4J4RzWXpAnz3eICpfvx0HEz63",
    "payments.csv": "1KOHJII8tkk8kaXpCKbsEJLMXAz-ehh_w",
    "channels.csv": "1xeU9ttngdzf-JOxEdn1MIzbhDiA7_bXn",
}

def _csv_path(name: str) -> Path:
    """Gets path or downloads file using ID directly."""
    p_local = LOCAL_DATA_DIR / name
    if p_local.exists():
        return p_local

    p_cache = CACHE_DATA_DIR / name
    
    # Download if not exists or file is empty
    if not p_cache.exists() or p_cache.stat().st_size == 0:
        file_id = GDRIVE_FILES.get(name)
        if not file_id:
            raise FileNotFoundError(f"No ID found for {name}")
        
        # We use id= instead of url= to bypass regex issues in gdown
        try:
            gdown.download(id=file_id, output=str(p_cache), quiet=False, use_cookies=False)
        except Exception as e:
            st.error(f"Critical error downloading {name}. Check Drive permissions.")
            raise e

    return p_cache

def _read_csv(name: str) -> pd.DataFrame:
    path = _csv_path(name)
    return pd.read_csv(path, encoding=ENCODING)

# --- Loading Functions ---

@st.cache_data
def load_orders():
    df = _read_csv("orders.csv")
    moment_cols = [c for c in df.columns if "order_moment" in c]
    for c in moment_cols:
        df[c] = pd.to_datetime(df[c], errors="coerce")
    return df

@st.cache_data
def load_stores(): return _read_csv("stores.csv")

@st.cache_data
def load_hubs(): return _read_csv("hubs.csv")

@st.cache_data
def load_deliveries(): return _read_csv("deliveries.csv")

@st.cache_data
def load_drivers(): return _read_csv("drivers.csv")

@st.cache_data
def load_payments(): return _read_csv("payments.csv")

@st.cache_data
def load_channels(): return _read_csv("channels.csv")

@st.cache_data
def load_full_dataset():
    orders = load_orders()
    stores = load_stores()
    hubs = load_hubs()
    channels = load_channels()
    deliveries = load_deliveries()
    drivers = load_drivers()
    payments = load_payments()

    df = orders.merge(stores, on="store_id", how="left")
    df = df.merge(hubs, on="hub_id", how="left")
    df = df.merge(channels, on="channel_id", how="left")

    payments_agg = payments.groupby("payment_order_id", as_index=False).agg(
        payment_amount=("payment_amount", "sum"),
        payment_status=("payment_status", "first"),
    )
    df = df.merge(payments_agg, left_on="payment_order_id", right_on="payment_order_id", how="left")

    deliveries_agg = deliveries.groupby("delivery_order_id", as_index=False).agg(
        delivery_distance_meters=("delivery_distance_meters", "sum"),
        delivery_status=("delivery_status", "first"),
    )
    df = df.merge(deliveries_agg, left_on="delivery_order_id", right_on="delivery_order_id", how="left")

    return df