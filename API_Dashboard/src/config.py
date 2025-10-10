import os

# Supabase Configuration
SUPABASE_URL = "https://ulqxtrftzvefnlzcmoti.supabase.co" # Replace with your default URL or leave empty
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InVscXh0cmZ0enZlZm5semNtb3RpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTQzOTAzMjcsImV4cCI6MjA2OTk2NjMyN30.UOq0LGSIqDrtI1o0KZCpoOtGY4_Zm9WBDMlOHYMbn6s"  # Replace with your default key or leave empty

TABLE_NAMES = {
    "Consumer Behavior": "consumer_behavior",
    "Resource Optimization": "resource_optimization",
    "Predictive Maintenance": "predictive_maintenance_report",
    "Preprocessed API": "preprocessed_api",
}

# Sample size for data fetching
SAMPLE_ROWS = 5000

# LLM configuration
LLM_MODEL_NAME = os.environ.get("LLM_MODEL_NAME", "llama3")  # default local LLM
LLM_PROVIDER = os.environ.get("LLM_PROVIDER", "ollama")  # options: "ollama", "openai", "anthropic"