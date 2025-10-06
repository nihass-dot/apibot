from supabase import create_client, Client
import pandas as pd
import streamlit as st
from src.config import SUPABASE_URL, SUPABASE_KEY, SAMPLE_ROWS, TABLE_NAMES

@st.cache_resource
def init_supabase() -> Client:
    """Initializes and returns a Supabase client."""
    if not SUPABASE_URL or not SUPABASE_KEY:
        st.error("Supabase URL or Key not found. Please set SUPABASE_URL and SUPABASE_KEY environment variables.")
        st.stop()
    return create_client(SUPABASE_URL, SUPABASE_KEY)

def fetch_data(table_display_name: str) -> pd.DataFrame:
    """
    Fetches a sample of data from the specified Supabase table.
    Caches the data for performance within the Streamlit session.
    """
    supabase = init_supabase()
    
    # Get the actual database table name from the display name
    actual_table_name = TABLE_NAMES[table_display_name]

    try:
        # Fetch data
        response = supabase.from_(actual_table_name).select("*").limit(SAMPLE_ROWS).execute()
        
        if response.data:
            df = pd.DataFrame(response.data)
            
            # Apply type conversions based on the column structures
            if "Consumer Behavior" in table_display_name:
                df['first_seen'] = pd.to_datetime(df['first_seen'], errors='coerce')
                df['last_seen'] = pd.to_datetime(df['last_seen'], errors='coerce')
                if 'client_id' in df.columns:
                     df['client_id'] = df['client_id'].replace('(empty)', 'No Client ID')
            
            return df
        else:
            st.warning(f"No data found in table: {actual_table_name}")
            return pd.DataFrame()
    except Exception as e:
        st.error(f"Error fetching data from Supabase table '{actual_table_name}': {e}")
        return pd.DataFrame()