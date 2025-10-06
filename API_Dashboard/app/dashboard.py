import sys
import os
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.data_loader import fetch_data
from src.visualization import plot_all_relevant_charts, plot_correlation_heatmap, plot_latency_boxplot, plot_request_boxplot, plot_latency_histogram, plot_request_histogram, plot_latency_vs_requests
from src.llm_analysis import get_llm_response
from src.config import TABLE_NAMES

st.set_page_config(layout="wide", page_title="API Monitoring Dashboard")

# Initialize session state variables
if 'llm_plot' not in st.session_state:
    st.session_state.llm_plot = None
if 'messages' not in st.session_state:
    st.session_state.messages = []

# --- Sidebar for Navigation and LLM Chat ---
st.sidebar.title("API Monitoring & Insights")

# Table Selection
st.sidebar.header("Data Source Selection")
selected_table_display_name = st.sidebar.selectbox(
    "Choose a table to analyze:",
    list(TABLE_NAMES.keys())
)

st.sidebar.markdown("---")

# Visualization Options
st.sidebar.header("Visualization Options")
viz_option = st.sidebar.selectbox(
    "Request a visualization:",
    ["None", "Boxplot of Latency", "Boxplot of Requests", "Correlation Heatmap", 
     "Latency Histogram", "Request Histogram", "Latency vs Requests Scatter"]
)

if st.sidebar.button("Generate Visualization") and viz_option != "None":
    if 'current_df' in st.session_state and not st.session_state.current_df.empty:
        df_viz = st.session_state.current_df
        
        if viz_option == "Boxplot of Latency" and 'avg_latency' in df_viz.columns:
            fig = px.box(df_viz, y='avg_latency', title="Boxplot of Latency (ms)")
            st.session_state.llm_plot = fig
        elif viz_option == "Boxplot of Requests" and 'request_count' in df_viz.columns:
            fig = px.box(df_viz, y='request_count', title="Boxplot of Request Count")
            st.session_state.llm_plot = fig
        elif viz_option == "Correlation Heatmap":
            numeric_df = df_viz.select_dtypes(include=['number'])
            if not numeric_df.empty:
                corr_matrix = numeric_df.corr()
                fig = px.imshow(corr_matrix, text_auto=True, aspect="auto", title="Correlation Heatmap")
                st.session_state.llm_plot = fig
        elif viz_option == "Latency Histogram" and 'avg_latency' in df_viz.columns:
            fig = px.histogram(df_viz, x='avg_latency', title="Histogram of Latency (ms)")
            st.session_state.llm_plot = fig
        elif viz_option == "Request Histogram" and 'request_count' in df_viz.columns:
            fig = px.histogram(df_viz, x='request_count', title="Histogram of Request Count")
            st.session_state.llm_plot = fig
        elif viz_option == "Latency vs Requests Scatter" and 'avg_latency' in df_viz.columns and 'request_count' in df_viz.columns:
            fig = px.scatter(df_viz, x='request_count', y='avg_latency', title="Latency vs Request Count")
            st.session_state.llm_plot = fig
        
        st.rerun()  # Fixed: Changed from st.experimental_rerun()
    else:
        st.sidebar.warning("No data available to generate visualizations.")

st.sidebar.markdown("---")

# LLM Chat Interface
st.sidebar.header("Ask the LLM for Insights")
llm_question = st.sidebar.text_input("e.g., Which client has the highest latency? Show me a boxplot.")

# Display chat messages
for message in st.session_state.messages:
    with st.sidebar.chat_message(message["role"]):
        st.sidebar.markdown(message["content"])

if st.sidebar.button("Get Insight"):
    if llm_question:
        with st.sidebar.chat_message("user"):
            st.sidebar.markdown(llm_question)
        st.session_state.messages.append({"role": "user", "content": llm_question})

        # Fetch data for LLM
        if 'current_df' in st.session_state and st.session_state.current_table_display_name == selected_table_display_name:
             df_for_llm = st.session_state.current_df
        else:
             df_for_llm = fetch_data(selected_table_display_name)
        
        with st.spinner("Getting insight from LLM..."):
            llm_response = get_llm_response(llm_question, df_for_llm, selected_table_display_name)
            
        with st.sidebar.chat_message("assistant"):
            st.sidebar.markdown(llm_response)
        st.session_state.messages.append({"role": "assistant", "content": llm_response})
    else:
        st.sidebar.warning("Please enter a question for the LLM.")

# Clear chat history button
if st.sidebar.button("Clear LLM Chat"):
    st.session_state.messages = []
    st.session_state.llm_plot = None
    st.rerun()  # Fixed: Changed from st.experimental_rerun()

# --- Main Dashboard Area ---
st.title("API Usage & Performance Dashboard")
st.markdown(f"Currently displaying data for: **{selected_table_display_name}**")
st.markdown("---")

# Fetch data based on selected table
with st.spinner(f"Loading data from {selected_table_display_name} (Supabase)..."):
    df = fetch_data(selected_table_display_name)
    st.session_state.current_df = df
    st.session_state.current_table_display_name = selected_table_display_name

# Display visualizations
if not df.empty:
    plot_all_relevant_charts(df, selected_table_display_name)
    
    # Display LLM-generated plot if available
    if st.session_state.llm_plot is not None:
        st.header("LLM-Generated Visualization")
        st.plotly_chart(st.session_state.llm_plot, use_container_width=True)
        
        # Add a button to clear the plot
        if st.button("Clear LLM Visualization"):
            st.session_state.llm_plot = None
            st.rerun()  # Fixed: Changed from st.experimental_rerun()
else:
    st.info(f"No data available for {selected_table_display_name} or an error occurred during fetching. "
            f"Please ensure the table '{TABLE_NAMES[selected_table_display_name]}' exists in your Supabase project and has data.")