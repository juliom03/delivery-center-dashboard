import streamlit as st
import pandas as pd
from pathlib import Path
import gdown
import os

# Path Configuration
# Navigating from /pages/2_🗺️_Geospatial.py up to the root directory
BASE_DIR = Path(__file__).resolve().parents[1]
LOCAL_DATA_DIR = BASE_DIR / "data"
CACHE_DATA_DIR = BASE_DIR / "data_cache"

# Ensure the cache directory exists
CACHE_DATA_DIR.mkdir(parents=True, exist_ok=True)

ENCODING = "latin-1"

# Google Drive File IDs mapping
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
    """
    Returns the path to the CSV file. 
    Downloads from Google Drive if not found locally or in cache.
    """
    # 1. Check if the file exists in the local /data folder
    p_local = LOCAL_DATA_DIR / name
    if p_local.exists():
        return p_local

    # 2. Check the /data_cache folder
    p_cache = CACHE_DATA_DIR / name
    
    # If the file is missing or empty in cache, download it
    if not p_cache.exists() or p_cache.stat().st_size == 0:
        file_id = GDRIVE_FILES.get(name)
        
        if not file_id or "PUT_" in file_id:
            raise FileNotFoundError(f"Missing file ID for {name}. Please check GDRIVE_FILES dictionary.")
        
        try:
            # FIXED: Using id= instead of the full URL to prevent AttributeError
            gdown.download(id=file_id, output=str(p_cache), quiet=False)
        except Exception as e:
            st.error(f"Failed to download {name} from Google Drive: {e}")
            raise e

    # Final validation
    if not p_cache.exists() or p_cache.stat().st_size == 0:
        raise FileNotFoundError(f"Could not retrieve {name} from any source.")
        
    return p_cache

def _read_csv(name: str) -> pd.DataFrame:
    """Helper to read CSV files with the specified encoding."""
    return pd.read_csv(_csv_path(name), encoding=ENCODING)

# --- Cached Data Loading Functions ---

@st.cache_data
def load_orders():
    df = _read_csv("orders.csv")
    # Convert time-related columns to datetime objects
    moment_cols = [c for c in df.columns if "order_moment" in c]
    for c in moment_cols:
        df[c] = pd.to_datetime(df[c], errors="coerce")
    return df

@st.cache_data
def load_stores():
    return _read_csv("stores.csv")

@st.cache_data
def load_hubs():
    return _read_csv("hubs.csv")

@st.cache_data
def load_deliveries():
    return _read_csv("deliveries.csv")

@st.cache_data
def load_drivers():
    return _read_csv("drivers.csv")

@st.cache_data
def load_payments():
    return _read_csv("payments.csv")

@st.cache_data
def load_channels():
    return _read_csv("channels.csv")

@st.cache_data
def load_full_dataset():
    """
    Performs the full data pipeline: 
    Loading all tables and merging them into a single analytical dataframe.
    """
    orders = load_orders()
    stores = load_stores()
    hubs = load_hubs()
    channels = load_channels()
    deliveries = load_deliveries()
    drivers = load_drivers()
    payments = load_payments()

    # Primary Merges: Adding store, hub, and channel info to orders
    df = orders.merge(stores, on="store_id", how="left")
    df = df.merge(hubs, on="hub_id", how="left")
    df = df.merge(channels, on="channel_id", how="left")

    # Payment Aggregation: A single order might have multiple payment attempts
    payments_agg = payments.groupby("payment_order_id", as_index=False).agg(
        payment_amount=("payment_amount", "sum"),
        payment_fee=("payment_fee", "sum"),
        # Get the most frequent payment method (mode)
        payment_method=("payment_method", lambda x: x.mode().iloc[0] if not x.mode().empty else None),
        payment_status=("payment_status", "first"),
    )
    df = df.merge(payments_agg, left_on="payment_order_id", right_on="payment_order_id", how="left")

    # Deliveries and Drivers Aggregation
    deliveries_drivers = deliveries.merge(drivers, on="driver_id", how="left")
    deliveries_agg = deliveries_drivers.groupby("delivery_order_id", as_index=False).agg(
        delivery_distance_meters=("delivery_distance_meters", "sum"),
        delivery_status=("delivery_status", "first"),
        driver_modal=("driver_modal", "first"),
        driver_type=("driver_type", "first"),
    )
    df = df.merge(deliveries_agg, left_on="delivery_order_id", right_on="delivery_order_id", how="left")

    # Data Integrity Check
    if len(df) != len(orders):
        st.warning(f"Integrity Alert: The merge process changed the row count (Original: {len(orders):,}, Final: {len(df):,})")
        
    return df