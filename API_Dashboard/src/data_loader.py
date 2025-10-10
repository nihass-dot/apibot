from supabase import create_client, Client
import pandas as pd
import streamlit as st
from src.config import SUPABASE_URL, SUPABASE_KEY, SAMPLE_ROWS, TABLE_NAMES

@st.cache_resource
def init_supabase() -> Client:
    """Initializes and returns a Supabase client."""
    if not SUPABASE_URL or not SUPABASE_KEY:
        st.error("Supabase URL or Key not found. Please set environment variables.")
        st.stop()
    return create_client(SUPABASE_URL, SUPABASE_KEY)

def fetch_data(table_display_name: str) -> pd.DataFrame:
    """Fetches *all* data from Supabase and returns it as a DataFrame."""
    supabase = init_supabase()
    actual_table_name = TABLE_NAMES[table_display_name]
    all_data = []
    batch_size = 1000
    start = 0

    try:
        while True:
            response = supabase.from_(actual_table_name).select("*").range(start, start + batch_size - 1).execute()

            if not response.data:
                break

            all_data.extend(response.data)
            start += batch_size

            # Stop if we get less than the batch size (means no more data)
            if len(response.data) < batch_size:
                break

        if all_data:
            df = pd.DataFrame(all_data)

            # 🧹 Optional: cleanup for consumer behavior data
            if "Consumer Behavior" in table_display_name:
                df['first_seen'] = pd.to_datetime(df['first_seen'], errors='coerce')
                df['last_seen'] = pd.to_datetime(df['last_seen'], errors='coerce')
                if 'client_id' in df.columns:
                    df['client_id'] = df['client_id'].replace('(empty)', 'No Client ID')

            st.write(f"✅ Rows fetched from {actual_table_name}: {len(df)}")
            return df
        else:
            st.warning(f"No data found in table: {actual_table_name}")
            return pd.DataFrame()

    except Exception as e:
        st.error(f"Error fetching data from Supabase table '{actual_table_name}': {e}")
        return pd.DataFrame()
