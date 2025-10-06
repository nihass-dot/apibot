import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from langchain_community.llms import Ollama
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from src.config import LLM_MODEL_NAME

def generate_plot_from_question(question: str, df: pd.DataFrame):
    """Generate a plot based on user's natural language question"""
    q_lower = question.lower()
    
    # Boxplot generation
    if "boxplot" in q_lower:
        if "latency" in q_lower and 'avg_latency' in df.columns:
            title = "Boxplot of Latency (ms)"
            fig = px.box(df, y='avg_latency', title=title)
            return fig
        elif "request" in q_lower and 'request_count' in df.columns:
            title = "Boxplot of Request Count"
            fig = px.box(df, y='request_count', title=title)
            return fig
    
    # Heatmap generation
    if "heatmap" in q_lower:
        if "correlation" in q_lower:
            numeric_df = df.select_dtypes(include=['number'])
            if not numeric_df.empty:
                corr_matrix = numeric_df.corr()
                title = "Correlation Heatmap"
                fig = px.imshow(corr_matrix, text_auto=True, aspect="auto", title=title)
                return fig
    
    # Histogram generation
    if "histogram" in q_lower:
        if "latency" in q_lower and 'avg_latency' in df.columns:
            title = "Histogram of Latency (ms)"
            fig = px.histogram(df, x='avg_latency', title=title)
            return fig
        elif "request" in q_lower and 'request_count' in df.columns:
            title = "Histogram of Request Count"
            fig = px.histogram(df, x='request_count', title=title)
            return fig
    
    # Scatter plot
    if "scatter" in q_lower or "relationship" in q_lower:
        if "latency" in q_lower and "request" in q_lower and 'avg_latency' in df.columns and 'request_count' in df.columns:
            title = "Latency vs Request Count"
            fig = px.scatter(df, x='request_count', y='avg_latency', title=title)
            return fig
    
    return None

def get_llm_response(question: str, df: pd.DataFrame, report_name: str) -> str:
    """
    Processes a natural language question and returns an analytical answer.
    Now includes dynamic plot generation.
    """
    if df.empty:
        return f"The selected '{report_name}' table has no data to analyze."
    
    # Generate plot if requested
    plot_fig = generate_plot_from_question(question, df)
    if plot_fig:
        # Store plot in session state for display
        st.session_state.llm_plot = plot_fig
        return "I've generated the requested visualization in the main dashboard area."
    
    # Standardize question for easier matching
    q_lower = question.lower()
    
    # Dynamic analysis based on available columns
    response = "I can provide insights based on the available columns in this report. "
    
    # General data questions
    if "total rows" in q_lower or "number of entries" in q_lower:
        return f"There are **{len(df)}** entries in the **{report_name}**."
    
    if "columns available" in q_lower:
        return f"The available columns in the current **{report_name}** are: {', '.join(df.columns.tolist())}."
    
    # Dynamic analysis based on actual columns in the dataframe
    if "highest average latency" in q_lower:
        latency_cols = [col for col in df.columns if 'latency' in col.lower()]
        if latency_cols:
            group_cols = [col for col in df.columns if 'client' in col.lower() or 'api' in col.lower() or 'uri' in col.lower()]
            if group_cols:
                grouped = df.groupby(group_cols[0])[latency_cols[0]].mean().sort_values(ascending=False)
                if not grouped.empty:
                    top_item = grouped.index[0]
                    top_value = grouped.iloc[0]
                    return f"The {group_cols[0]} with the highest average latency is **'{top_item}'** with **{top_value:.2f} ms**."
    
    if "highest error rate" in q_lower:
        error_cols = [col for col in df.columns if 'error' in col.lower()]
        if error_cols:
            group_cols = [col for col in df.columns if 'client' in col.lower() or 'api' in col.lower() or 'uri' in col.lower()]
            if group_cols:
                grouped = df.groupby(group_cols[0])[error_cols[0]].mean().sort_values(ascending=False)
                if not grouped.empty:
                    top_item = grouped.index[0]
                    top_value = grouped.iloc[0]
                    return f"The {group_cols[0]} with the highest error rate is **'{top_item}'** with **{top_value:.2f}%**."
    
    if "top" in q_lower and "request" in q_lower:
        request_cols = [col for col in df.columns if 'request' in col.lower()]
        if request_cols:
            group_cols = [col for col in df.columns if 'client' in col.lower() or 'api' in col.lower() or 'uri' in col.lower()]
            if group_cols:
                grouped = df.groupby(group_cols[0])[request_cols[0]].sum().sort_values(ascending=False)
                if not grouped.empty:
                    top_items = grouped.head(3)
                    items_str = ", ".join([f"{item} ({value} requests)" for item, value in top_items.items()])
                    return f"The top {group_cols[0]}s by request count are: {items_str}."
    
    # Default response if no specific question is matched
    return "I can analyze this data for you. Try asking about latency, error rates, request counts, or request visualizations like boxplots or heatmaps."