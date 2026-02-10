# utils/data_loader.py
# Centralized data loading and preprocessing for the Delivery Center dashboard.
# All join logic lives here so every page works with the same clean dataset.

import streamlit as st
import pandas as pd
import os

DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")


@st.cache_data
def load_orders():
    """Load and preprocess the orders table."""
    df = pd.read_csv(os.path.join(DATA_PATH, "orders.csv"))

    # Convert moment columns to datetime
    moment_cols = [col for col in df.columns if "order_moment" in col]
    for col in moment_cols:
        df[col] = pd.to_datetime(df[col], errors="coerce")

    return df


@st.cache_data
def load_stores():
    return pd.read_csv(os.path.join(DATA_PATH, "stores.csv"))


@st.cache_data
def load_hubs():
    return pd.read_csv(os.path.join(DATA_PATH, "hubs.csv"))


@st.cache_data
def load_deliveries():
    return pd.read_csv(os.path.join(DATA_PATH, "deliveries.csv"))


@st.cache_data
def load_drivers():
    return pd.read_csv(os.path.join(DATA_PATH, "drivers.csv"))


@st.cache_data
def load_payments():
    return pd.read_csv(os.path.join(DATA_PATH, "payments.csv"))


@st.cache_data
def load_channels():
    return pd.read_csv(os.path.join(DATA_PATH, "channels.csv"))


@st.cache_data
def load_full_dataset():
    """
    Build the full analytical dataset by merging all tables.

    IMPORTANT — join strategy to avoid row duplication:
    - stores, hubs, channels: many-to-one from orders → safe direct merge
    - payments: may have multiple rows per order (e.g. split payments)
      → aggregate FIRST, then merge
    - deliveries + drivers: may have multiple deliveries per order
      → aggregate FIRST, then merge
    """
    orders = load_orders()
    stores = load_stores()
    hubs = load_hubs()
    channels = load_channels()
    deliveries = load_deliveries()
    drivers = load_drivers()
    payments = load_payments()

    # --------------------------------------------------
    # Step 1: Safe many-to-one joins (no duplication risk)
    # --------------------------------------------------
    df = orders.merge(stores, on="store_id", how="left")
    df = df.merge(hubs, on="hub_id", how="left")
    df = df.merge(channels, on="channel_id", how="left")

    # --------------------------------------------------
    # Step 2: Aggregate payments BEFORE joining
    # One row per payment_order_id with summed amounts
    # --------------------------------------------------
    payments_agg = (
        payments
        .groupby("payment_order_id")
        .agg(
            payment_amount=("payment_amount", "sum"),
            payment_fee=("payment_fee", "sum"),
            # Keep the most common payment method per order
            payment_method=("payment_method", lambda x: x.mode().iloc[0] if len(x.mode()) > 0 else None),
            payment_status=("payment_status", "first"),
        )
        .reset_index()
    )
    df = df.merge(payments_agg, on="payment_order_id", how="left")

    # --------------------------------------------------
    # Step 3: Aggregate deliveries BEFORE joining
    # One row per delivery_order_id with key delivery info
    # --------------------------------------------------
    deliveries_with_drivers = deliveries.merge(drivers, on="driver_id", how="left")

    deliveries_agg = (
        deliveries_with_drivers
        .groupby("delivery_order_id")
        .agg(
            delivery_distance_meters=("delivery_distance_meters", "sum"),
            delivery_status=("delivery_status", "first"),
            driver_modal=("driver_modal", "first"),
            driver_type=("driver_type", "first"),
        )
        .reset_index()
    )
    df = df.merge(deliveries_agg, on="delivery_order_id", how="left")

    # --------------------------------------------------
    # Sanity check: row count should match original orders
    # --------------------------------------------------
    assert len(df) == len(orders), (
        f"Row count mismatch after joins! "
        f"Orders: {len(orders):,}, Merged: {len(df):,}. "
        f"Check for duplicate keys in dimension tables."
    )

    return df