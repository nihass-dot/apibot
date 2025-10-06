import streamlit as st
import pandas as pd
import plotly.express as px

def plot_client_request_counts(df: pd.DataFrame):
    """Plots top clients by request count from consumer_behavior_report."""
    if 'client_id' in df.columns and 'request_count' in df.columns:
        st.subheader("Top Clients by Request Count")
        plot_df = df[df['client_id'] != 'No Client ID'].sort_values('request_count', ascending=False).head(10)
        if not plot_df.empty:
            fig = px.bar(plot_df, x='client_id', y='request_count', 
                         title='Top 10 Clients by Total Request Count')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No client-specific data to plot request counts.")
    else:
        st.info("Client request counts cannot be plotted. Missing 'client_id' or 'request_count' column.")

def plot_consumer_avg_latency(df: pd.DataFrame):
    """Plots average latency for consumers, excluding (empty) client_id if present."""
    if 'client_id' in df.columns and 'avg_latency' in df.columns:
        st.subheader("Client Average Latency Distribution")
        plot_df = df[df['client_id'] != 'No Client ID'].sort_values('avg_latency', ascending=False).head(15)
        if not plot_df.empty:
            fig = px.bar(plot_df, x='client_id', y='avg_latency', 
                         title='Top 15 Clients by Average Latency (ms)')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No client-specific data to plot average latency.")
    else:
        st.info("Average latency by client cannot be plotted. Missing 'client_id' or 'avg_latency' column.")

def plot_error_rate_distribution(df: pd.DataFrame):
    """Plots distribution of error rates, useful for both consumer and predictive reports."""
    if 'error_rate_pct' in df.columns:
        st.subheader("Client Error Rate Distribution")
        plot_df = df[df['client_id'] != 'No Client ID'].sort_values('error_rate_pct', ascending=False).head(15)
        if not plot_df.empty:
            fig = px.bar(plot_df, x='client_id', y='error_rate_pct', 
                         title='Top 15 Clients by Error Rate (%)')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No client-specific data to plot error rates.")
    elif 'avg_error_rate' in df.columns and 'uri_path' in df.columns:
        st.subheader("API Average Error Rate Distribution")
        plot_df = df.sort_values('avg_error_rate', ascending=False).head(15)
        if not plot_df.empty:
            fig = px.bar(plot_df, x='uri_path', y='avg_error_rate', 
                         title='Top 15 URIs by Average Error Rate (%)')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No API-specific data to plot average error rates.")
    else:
        st.info("Error rate distribution cannot be plotted. Missing relevant error rate column.")

def plot_api_latency_and_requests(df: pd.DataFrame):
    """Plots API latency and request counts from resource_optimization_report."""
    if 'uri_path' in df.columns and 'avg_latency' in df.columns and 'request_count' in df.columns:
        st.subheader("API Latency vs. Request Count")
        fig = px.scatter(df, x='avg_latency', y='request_count', color='uri_path', 
                         size='request_count', hover_name='uri_path',
                         title='API Average Latency vs. Request Count')
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("Top APIs by Average Latency")
        top_latency_apis = df.sort_values('avg_latency', ascending=False).head(15)
        fig_lat = px.bar(top_latency_apis, x='uri_path', y='avg_latency', 
                         title='Top 15 APIs by Average Latency (ms)')
        st.plotly_chart(fig_lat, use_container_width=True)

        st.subheader("Top APIs by Request Count")
        top_request_apis = df.sort_values('request_count', ascending=False).head(15)
        fig_req = px.bar(top_request_apis, x='uri_path', y='request_count', 
                         title='Top 15 APIs by Request Count')
        st.plotly_chart(fig_req, use_container_width=True)
    else:
        st.info("API latency/request plots cannot be generated. Missing 'uri_path', 'avg_latency', or 'request_count'.")

def plot_resource_utilization(df: pd.DataFrame):
    """Plots resource utilization from resource_optimization_report."""
    if 'utilization' in df.columns and 'uri_path' in df.columns:
        st.subheader("API Utilization Distribution")
        utilization_counts = df['utilization'].value_counts().reset_index()
        utilization_counts.columns = ['Utilization Level', 'Count']
        fig = px.pie(utilization_counts, names='Utilization Level', values='Count', 
                     title='Distribution of API Utilization Levels')
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Resource utilization cannot be plotted. Missing 'utilization' or 'uri_path'.")

def plot_maintenance_priority(df: pd.DataFrame):
    """Plots maintenance priority from predictive_maintenance_report."""
    if 'maintenance_priority' in df.columns and 'uri_path' in df.columns:
        st.subheader("Maintenance Priority Distribution")
        priority_counts = df['maintenance_priority'].value_counts().reset_index()
        priority_counts.columns = ['Priority Level', 'Count']
        fig = px.pie(priority_counts, names='Priority Level', values='Count', 
                     title='Distribution of API Maintenance Priorities')
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("APIs by Maintenance Priority")
        high_priority_apis = df[df['maintenance_priority'].isin(['High', 'Medium'])].sort_values('maintenance_priority').head(20)
        if not high_priority_apis.empty:
            fig_bar = px.bar(high_priority_apis, x='uri_path', y='avg_error_rate' if 'avg_error_rate' in high_priority_apis.columns else None,
                             color='maintenance_priority', title='APIs with High/Medium Maintenance Priority',
                             hover_data=['avg_error_rate', 'max_error_rate'])
            st.plotly_chart(fig_bar, use_container_width=True)
        else:
            st.info("No high/medium priority APIs to display.")
    else:
        st.info("Maintenance priority cannot be plotted. Missing 'maintenance_priority' or 'uri_path'.")

def display_dataframe_summary(df: pd.DataFrame, title: str):
    """Displays a summary of the dataframe and its first few rows."""
    if not df.empty:
        st.subheader(f"Data Overview: {title} (Sampled)")
        st.write(f"Number of rows: {len(df)}")
        st.write(f"Number of columns: {len(df.columns)}")
        st.dataframe(df.head())
        st.subheader("Descriptive Statistics")
        st.write(df.describe(include='all'))
    else:
        st.info("No data available to display summary.")

def plot_correlation_heatmap(df: pd.DataFrame):
    """Plots a correlation heatmap for numeric columns."""
    st.subheader("Correlation Heatmap")
    numeric_df = df.select_dtypes(include=['number'])
    if not numeric_df.empty:
        corr_matrix = numeric_df.corr()
        fig = px.imshow(corr_matrix, text_auto=True, aspect="auto", title="Correlation Heatmap")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No numeric columns available for correlation heatmap.")

def plot_latency_boxplot(df: pd.DataFrame):
    """Plots a boxplot of latency values."""
    st.subheader("Latency Boxplot")
    if 'avg_latency' in df.columns:
        fig = px.box(df, y='avg_latency', title="Boxplot of Latency (ms)")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No latency data available for boxplot.")

def plot_request_boxplot(df: pd.DataFrame):
    """Plots a boxplot of request counts."""
    st.subheader("Request Count Boxplot")
    if 'request_count' in df.columns:
        fig = px.box(df, y='request_count', title="Boxplot of Request Count")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No request count data available for boxplot.")

def plot_latency_histogram(df: pd.DataFrame):
    """Plots a histogram of latency values."""
    st.subheader("Latency Histogram")
    if 'avg_latency' in df.columns:
        fig = px.histogram(df, x='avg_latency', title="Histogram of Latency (ms)")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No latency data available for histogram.")

def plot_request_histogram(df: pd.DataFrame):
    """Plots a histogram of request counts."""
    st.subheader("Request Count Histogram")
    if 'request_count' in df.columns:
        fig = px.histogram(df, x='request_count', title="Histogram of Request Count")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No request count data available for histogram.")

def plot_latency_vs_requests(df: pd.DataFrame):
    """Plots a scatter plot of latency vs request count."""
    st.subheader("Latency vs Request Count")
    if 'avg_latency' in df.columns and 'request_count' in df.columns:
        fig = px.scatter(df, x='request_count', y='avg_latency', title="Latency vs Request Count")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Both latency and request count data are required for this plot.")

def plot_all_relevant_charts(df: pd.DataFrame, display_name: str):
    """
    Analyzes the dataframe and plots relevant charts based on available columns,
    adapting to the selected report.
    """
    if df.empty:
        st.warning(f"No data available for {display_name}.")
        return

    st.header(f"Dashboard for: {display_name}")
    st.markdown("---")

    # Always show basic data summary
    display_dataframe_summary(df, display_name)
    st.markdown("---")

    # Logic to plot charts based on the selected report type
    if "Consumer Behavior" in display_name:
        plot_client_request_counts(df)
        plot_consumer_avg_latency(df)
        plot_error_rate_distribution(df)
        
        if 'api_diversity' in df.columns and 'client_id' in df.columns:
            st.subheader("Client API Diversity")
            plot_df = df[df['client_id'] != 'No Client ID'].sort_values('api_diversity', ascending=False).head(15)
            if not plot_df.empty:
                fig = px.bar(plot_df, x='client_id', y='api_diversity', 
                             title='Top 15 Clients by API Diversity')
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No client-specific data to plot API diversity.")

    elif "Resource Optimization" in display_name:
        plot_api_latency_and_requests(df)
        plot_resource_utilization(df)
        if 'efficiency_score' in df.columns and 'uri_path' in df.columns:
            st.subheader("API Efficiency Score")
            plot_df = df.sort_values('efficiency_score', ascending=False).head(15)
            fig = px.bar(plot_df, x='uri_path', y='efficiency_score', 
                         title='Top 15 APIs by Efficiency Score')
            st.plotly_chart(fig, use_container_width=True)

    elif "Predictive Maintenance" in display_name:
        plot_error_rate_distribution(df)
        plot_maintenance_priority(df)
        if 'prediction_score' in df.columns and 'uri_path' in df.columns:
            st.subheader("API Anomaly Prediction Scores")
            plot_df = df.sort_values('prediction_score', ascending=False).head(15)
            fig = px.bar(plot_df, x='uri_path', y='prediction_score', 
                         title='Top 15 APIs by Anomaly Prediction Score')
            st.plotly_chart(fig, use_container_width=True)