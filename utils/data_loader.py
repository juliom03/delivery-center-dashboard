import streamlit as st
import pandas as pd
from pathlib import Path
import gdown

BASE_DIR = Path(__file__).resolve().parents[1]
LOCAL_DATA_DIR = BASE_DIR / "data"
CACHE_DATA_DIR = BASE_DIR / "data_cache"
CACHE_DATA_DIR.mkdir(exist_ok=True)

ENCODING = "latin-1"

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
    p_local = LOCAL_DATA_DIR / name
    if p_local.exists():
        return p_local

    p_cache = CACHE_DATA_DIR / name
    if p_cache.exists() and p_cache.stat().st_size > 0:
        return p_cache

    file_id = GDRIVE_FILES.get(name)
    if not file_id or "PUT_" in file_id:
        raise FileNotFoundError(f"Missing {name}. Add it to /data or set its Google Drive file id.")

    url = f"https://drive.google.com/file/d/{file_id}/view?usp=sharing"
    gdown.download(url, str(p_cache), quiet=True, fuzzy=True)

    if not p_cache.exists() or p_cache.stat().st_size == 0:
        raise FileNotFoundError(f"Failed to download {name}. Check sharing + file id.")
    return p_cache

def _read_csv(name: str) -> pd.DataFrame:
    return pd.read_csv(_csv_path(name), encoding=ENCODING)

@st.cache_data
def load_orders():
    df = _read_csv("orders.csv")
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
        payment_fee=("payment_fee", "sum"),
        payment_method=("payment_method", lambda x: x.mode().iloc[0] if not x.mode().empty else None),
        payment_status=("payment_status", "first"),
    )
    df = df.merge(payments_agg, on="payment_order_id", how="left")

    deliveries_agg = deliveries.merge(drivers, on="driver_id", how="left").groupby(
        "delivery_order_id", as_index=False
    ).agg(
        delivery_distance_meters=("delivery_distance_meters", "sum"),
        delivery_status=("delivery_status", "first"),
        driver_modal=("driver_modal", "first"),
        driver_type=("driver_type", "first"),
    )
    df = df.merge(deliveries_agg, on="delivery_order_id", how="left")

    assert len(df) == len(orders), f"Row mismatch: orders={len(orders):,} merged={len(df):,}"
    return df