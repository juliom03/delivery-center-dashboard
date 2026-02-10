import streamlit as st
import pandas as pd
from pathlib import Path
import gdown
import os
import sys

# Path Configuration
# Navigates from /pages/ or /utils/ up to the root directory
BASE_DIR = Path(__file__).resolve().parents[1]
LOCAL_DATA_DIR = BASE_DIR / "data"
CACHE_DATA_DIR = BASE_DIR / "data_cache"

# Ensure the cache directory exists in the Streamlit environment
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
    Retrieves the local path of the CSV. 
    Downloads from Drive if missing, using a robust method to avoid 'NoneType' errors.
    """
    # 1. Check local /data folder (development mode)
    p_local = LOCAL_DATA_DIR / name
    if p_local.exists():
        return p_local

    # 2. Check /data_cache folder (Streamlit Cloud mode)
    p_cache = CACHE_DATA_DIR / name
    
    # Download if file doesn't exist or is empty (failed previous download)
    if not p_cache.exists() or p_cache.stat().st_size == 0:
        file_id = GDRIVE_FILES.get(name)
        
        if not file_id:
            raise FileNotFoundError(f"No Google Drive ID mapped for {name}")
        
        try:
            # Format as direct download link
            url = f'https://drive.google.com/uc?id={file_id}'
            
            # fuzzy=False is THE FIX. It stops gdown from trying to guess the filename
            # from headers that Google Drive is currently hiding or changing.
            gdown.download(url, str(p_cache), quiet=False, fuzzy=False)
            
        except Exception as e:
            st.error(f"Failed to download {name}. Ensure the file is set to 'Anyone with the link' on Drive.")
            raise e

    if not p_cache.exists() or p_cache.stat().st_size == 0:
        raise FileNotFoundError(f"File {name} is missing and could not be downloaded.")
        
    return p_cache

def _read_csv(name: str) -> pd.DataFrame:
    """Reads CSV with the specific encoding required for this dataset."""
    return pd.read_csv(_csv_path(name), encoding=ENCODING)

# --- Data Loading Functions with Streamlit Cache ---

@st.cache_data
def load_orders():
    df = _read_csv("orders.csv")
    # Pre-process dates immediately
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
    """
    Main Data Pipeline: Loads all CSVs and performs left joins to create 
    the master analytical dataframe.
    """
    orders = load_orders()
    stores = load_stores()
    hubs = load_hubs()
    channels = load_channels()
    deliveries = load_deliveries()
    drivers = load_drivers()
    payments = load_payments()

    # Core joins
    df = orders.merge(stores, on="store_id", how="left")
    df = df.merge(hubs, on="hub_id", how="left")
    df = df.merge(channels, on="channel_id", how="left")

        # Aggregate Payments (Sum amounts per order, keep method and fee)
    payments_agg = payments.groupby("payment_order_id", as_index=False).agg(
        payment_amount=("payment_amount", "sum"),
        payment_fee=("payment_fee", "sum"),
        payment_method=("payment_method", "first"),
        payment_status=("payment_status", "first"),
    )
    df = df.merge(payments_agg, left_on="payment_order_id", right_on="payment_order_id", how="left")

    # Aggregate Deliveries & Drivers
    deliveries_drivers = deliveries.merge(drivers, on="driver_id", how="left")
    deliveries_agg = deliveries_drivers.groupby("delivery_order_id", as_index=False).agg(
        delivery_distance_meters=("delivery_distance_meters", "sum"),
        driver_modal=("driver_modal", "first"),
        delivery_status=("delivery_status", "first")
    )
    df = df.merge(deliveries_agg, left_on="delivery_order_id", right_on="delivery_order_id", how="left")

    return df