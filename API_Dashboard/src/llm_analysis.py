import streamlit as st
import pandas as pd
import plotly.express as px
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from src.config import LLM_MODEL_NAME, LLM_PROVIDER

# Dynamically load the chosen LLM provider
def load_llm():
    """Load a local or cloud LLM in a modular way."""
    if LLM_PROVIDER == "ollama":
        from langchain_community.llms import Ollama
        return Ollama(model=LLM_MODEL_NAME)
    elif LLM_PROVIDER == "openai":
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(model=LLM_MODEL_NAME, temperature=0.3)
    elif LLM_PROVIDER == "anthropic":
        from langchain_anthropic import ChatAnthropic
        return ChatAnthropic(model=LLM_MODEL_NAME)
    else:
        raise ValueError(f"Unsupported LLM provider: {LLM_PROVIDER}")

# -------------------
# Visualization logic
# -------------------
def generate_plot_from_question(question: str, df: pd.DataFrame):
    q_lower = question.lower()

    # Boxplot
    if "boxplot" in q_lower:
        if "latency" in q_lower and 'avg_latency' in df.columns:
            return px.box(df, y='avg_latency', title="Boxplot of Latency (ms)")
        elif "request" in q_lower and 'request_count' in df.columns:
            return px.box(df, y='request_count', title="Boxplot of Request Count")

    # Heatmap
    if "heatmap" in q_lower and "correlation" in q_lower:
        numeric_df = df.select_dtypes(include=['number'])
        if not numeric_df.empty:
            corr_matrix = numeric_df.corr()
            return px.imshow(corr_matrix, text_auto=True, aspect="auto", title="Correlation Heatmap")

    # Histogram
    if "histogram" in q_lower:
        if "latency" in q_lower and 'avg_latency' in df.columns:
            return px.histogram(df, x='avg_latency', title="Histogram of Latency (ms)")
        elif "request" in q_lower and 'request_count' in df.columns:
            return px.histogram(df, x='request_count', title="Histogram of Request Count")

    # Scatter plot
    if ("scatter" in q_lower or "relationship" in q_lower) and \
       'avg_latency' in df.columns and 'request_count' in df.columns:
        return px.scatter(df, x='request_count', y='avg_latency', title="Latency vs Request Count")

    return None

# -------------------
# LLM logic
# -------------------
def get_llm_response(question: str, df: pd.DataFrame, report_name: str) -> str:
    """Processes a natural language question and returns an analytical answer."""
    if df.empty:
        return f"The selected '{report_name}' table has no data to analyze."

    # Generate a plot if applicable
    plot_fig = generate_plot_from_question(question, df)
    if plot_fig:
        st.session_state.llm_plot = plot_fig
        return "I've generated the requested visualization in the main dashboard area."

    # Basic manual logic
    q_lower = question.lower()
    if "total rows" in q_lower or "entries" in q_lower:
        return f"There are **{len(df)}** entries in the **{report_name}** dataset."

    if "columns" in q_lower:
        return f"The available columns in this **{report_name}** are: {', '.join(df.columns)}."

    # Prepare a **summary of the data** to pass to the LLM
    summary = {}
    for col in df.columns:
        if pd.api.types.is_numeric_dtype(df[col]):
            summary[col] = {
                "min": df[col].min(),
                "max": df[col].max(),
                "mean": df[col].mean(),
                "top_3": df[col].nlargest(3).tolist()
            }
        else:
            summary[col] = {
                "top_5": df[col].value_counts().head(5).to_dict()
            }

    # Construct a concise textual representation
    data_context = ""
    for col, stats in summary.items():
        data_context += f"\nColumn '{col}': {stats}"

    # Use LLM
    llm = load_llm()
    prompt = PromptTemplate(
        input_variables=["question", "report_name", "data_context"],
        template=(
            "You are a data analyst assistant. "
            "Analyze the '{report_name}' dataset using the following summarized data context: {data_context}. "
            "Answer the question clearly and concisely: {question}"
        )
    )
    chain = LLMChain(llm=llm, prompt=prompt)
    response = chain.run({
        "question": question,
        "report_name": report_name,
        "data_context": data_context
    })

    return response or "I'm unable to derive insights from this question right now."
