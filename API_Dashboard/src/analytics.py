# src/analytics.py
import pandas as pd

def get_summary(df):
    return df.describe(include='all')

def requests_over_time(df, freq='5min'):
    return df.groupby(pd.Grouper(key='timestamp', freq=freq)).size()

def avg_latency_per_api(df):
    return df.groupby('api_name')['latency_ms'].mean().sort_values(ascending=False)

def avg_latency_per_app(df):
    return df.groupby('app_name')['latency_ms'].mean().sort_values(ascending=False)

def top_clients(df, n=10):
    return df['client_id'].value_counts().head(n)

def top_endpoints(df, n=10):
    return df['uri_path'].value_counts().head(n)

def status_code_distribution(df):
    return df['status_code_cleaned'].value_counts()

def version_usage(df):
    return df['api_version'].value_counts()
