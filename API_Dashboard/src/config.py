import os

# Supabase Configuration
SUPABASE_URL = os.environ.get("SUPABASE_URL", "SUPABASE_URL")  # Replace with your default URL or leave empty
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "SUPABASE_KEY")  # Replace with your default key or leave empty

# Table names for the dashboard
TABLE_NAMES = {
    "Consumer Behavior": "consumer_behavior",
    "Resource Optimization": "resource_optimization",
    "Predictive Maintenance": "predictive_maintenance_report"
}

# Sample size for data fetching
SAMPLE_ROWS = 1000

# LLM Configuration
LLM_MODEL_NAME = os.environ.get("LLM_MODEL_NAME", "llama2")  # Default to llama2 if not specified