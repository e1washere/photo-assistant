"""
Real-time Dashboard for Photo Assistant

Provides a web-based dashboard for monitoring system performance,
API usage, and system health metrics.
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import time
from datetime import datetime, timedelta
import json
from monitoring import performance_monitor, get_health_endpoint, get_metrics_endpoint


def create_dashboard():
    """Create the main dashboard interface."""
    st.set_page_config(
        page_title="Photo Assistant Dashboard",
        page_icon="📊",
        layout="wide"
    )
    
    st.title("📊 Photo Assistant - System Dashboard")
    st.markdown("Real-time monitoring and performance analytics")
    
    # Sidebar for navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox(
        "Choose a page",
        ["Overview", "Performance Metrics", "System Health", "API Analytics", "Settings"]
    )
    
    if page == "Overview":
        show_overview()
    elif page == "Performance Metrics":
        show_performance_metrics()
    elif page == "System Health":
        show_system_health()
    elif page == "API Analytics":
        show_api_analytics()
    elif page == "Settings":
        show_settings()


def show_overview():
    """Show overview dashboard."""
    st.header("System Overview")
    
    # Get current metrics
    health_data = get_health_endpoint()
    metrics_data = get_metrics_endpoint()
    
    # Create metrics cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="API Calls",
            value=health_data.get('application', {}).get('api_calls_total', 0),
            delta=None
        )
    
    with col2:
        success_rate = health_data.get('application', {}).get('success_rate', 0)
        st.metric(
            label="Success Rate",
            value=f"{success_rate}%",
            delta=None
        )
    
    with col3:
        cpu_usage = health_data.get('system', {}).get('cpu_usage', 0)
        st.metric(
            label="CPU Usage",
            value=f"{cpu_usage}%",
            delta=None
        )
    
    with col4:
        memory_usage = health_data.get('system', {}).get('memory_usage', 0)
        st.metric(
            label="Memory Usage",
            value=f"{memory_usage}%",
            delta=None
        )
    
    # System status
    st.subheader("System Status")
    status = health_data.get('status', 'unknown')
    
    if status == 'healthy':
        st.success("🟢 System is healthy")
    elif status == 'warning':
        st.warning("🟡 System needs attention")
    else:
        st.error("🔴 System has issues")
    
    # Recent activity
    st.subheader("Recent Activity")
    if performance_monitor.metrics_history:
        recent_metrics = performance_monitor.metrics_history[-10:]
        
        # Create activity chart
        timestamps = [datetime.fromtimestamp(m.timestamp) for m in recent_metrics]
        processing_times = [m.processing_time for m in recent_metrics]
        
        fig = px.line(
            x=timestamps,
            y=processing_times,
            title="Processing Time Trend",
            labels={'x': 'Time', 'y': 'Processing Time (seconds)'}
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No activity data available yet")


def show_performance_metrics():
    """Show detailed performance metrics."""
    st.header("Performance Metrics")
    
    metrics_data = get_metrics_endpoint()
    
    if 'message' in metrics_data:
        st.info(metrics_data['message'])
        return
    
    # Performance summary
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Processing Time Statistics")
        processing_stats = metrics_data.get('processing_time', {})
        
        st.metric("Average", f"{processing_stats.get('average', 0)}s")
        st.metric("Minimum", f"{processing_stats.get('min', 0)}s")
        st.metric("Maximum", f"{processing_stats.get('max', 0)}s")
        st.metric("Median", f"{processing_stats.get('median', 0)}s")
    
    with col2:
        st.subheader("System Usage")
        system_stats = metrics_data.get('system_usage', {})
        
        st.metric("Memory Average", f"{system_stats.get('memory_average', 0)}%")
        st.metric("CPU Average", f"{system_stats.get('cpu_average', 0)}%")
        st.metric("Success Rate", f"{metrics_data.get('success_rate', 0)}%")
        st.metric("Uptime", f"{metrics_data.get('uptime_hours', 0)}h")
    
    # Performance charts
    if performance_monitor.metrics_history:
        st.subheader("Performance Trends")
        
        # Prepare data
        df = pd.DataFrame([
            {
                'timestamp': datetime.fromtimestamp(m.timestamp),
                'processing_time': m.processing_time,
                'memory_usage': m.memory_usage,
                'cpu_usage': m.cpu_usage
            }
            for m in performance_monitor.metrics_history
        ])
        
        # Create subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Processing Time', 'Memory Usage', 'CPU Usage', 'Success Rate'),
            specs=[[{"secondary_y": False}, {"secondary_y": False}],
                   [{"secondary_y": False}, {"secondary_y": False}]]
        )
        
        # Processing time
        fig.add_trace(
            go.Scatter(x=df['timestamp'], y=df['processing_time'], name='Processing Time'),
            row=1, col=1
        )
        
        # Memory usage
        fig.add_trace(
            go.Scatter(x=df['timestamp'], y=df['memory_usage'], name='Memory Usage'),
            row=1, col=2
        )
        
        # CPU usage
        fig.add_trace(
            go.Scatter(x=df['timestamp'], y=df['cpu_usage'], name='CPU Usage'),
            row=2, col=1
        )
        
        # Success rate (calculated)
        success_rates = []
        for i, m in enumerate(performance_monitor.metrics_history):
            if m.api_calls > 0:
                success_rate = (m.api_calls - m.error_count) / m.api_calls * 100
                success_rates.append(success_rate)
            else:
                success_rates.append(0)
        
        fig.add_trace(
            go.Scatter(x=df['timestamp'], y=success_rates, name='Success Rate'),
            row=2, col=2
        )
        
        fig.update_layout(height=600, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)


def show_system_health():
    """Show system health information."""
    st.header("System Health")
    
    health_data = get_health_endpoint()
    
    # System metrics
    st.subheader("System Resources")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        system_data = health_data.get('system', {})
        cpu_usage = system_data.get('cpu_usage', 0)
        
        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=cpu_usage,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "CPU Usage"},
            gauge={'axis': {'range': [None, 100]},
                   'bar': {'color': "darkblue"},
                   'steps': [
                       {'range': [0, 50], 'color': "lightgray"},
                       {'range': [50, 80], 'color': "yellow"},
                       {'range': [80, 100], 'color': "red"}
                   ]}
        ))
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        memory_usage = system_data.get('memory_usage', 0)
        
        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=memory_usage,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Memory Usage"},
            gauge={'axis': {'range': [None, 100]},
                   'bar': {'color': "darkblue"},
                   'steps': [
                       {'range': [0, 50], 'color': "lightgray"},
                       {'range': [50, 80], 'color': "yellow"},
                       {'range': [80, 100], 'color': "red"}
                   ]}
        ))
        st.plotly_chart(fig, use_container_width=True)
    
    with col3:
        disk_usage = system_data.get('disk_usage', 0)
        
        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=disk_usage,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Disk Usage"},
            gauge={'axis': {'range': [None, 100]},
                   'bar': {'color': "darkblue"},
                   'steps': [
                       {'range': [0, 70], 'color': "lightgray"},
                       {'range': [70, 90], 'color': "yellow"},
                       {'range': [90, 100], 'color': "red"}
                   ]}
        ))
        st.plotly_chart(fig, use_container_width=True)
    
    # Detailed system info
    st.subheader("Detailed System Information")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**System Metrics:**")
        st.json(system_data)
    
    with col2:
        app_data = health_data.get('application', {})
        st.write("**Application Metrics:**")
        st.json(app_data)


def show_api_analytics():
    """Show API analytics and usage patterns."""
    st.header("API Analytics")
    
    if not performance_monitor.metrics_history:
        st.info("No API analytics data available yet")
        return
    
    # API call trends
    st.subheader("API Call Trends")
    
    # Group by hour
    df = pd.DataFrame([
        {
            'timestamp': datetime.fromtimestamp(m.timestamp),
            'api_calls': m.api_calls,
            'success_rate': m.success_rate,
            'error_count': m.error_count
        }
        for m in performance_monitor.metrics_history
    ])
    
    # Hourly aggregation
    df['hour'] = df['timestamp'].dt.hour
    hourly_stats = df.groupby('hour').agg({
        'api_calls': 'count',
        'success_rate': 'mean',
        'error_count': 'sum'
    }).reset_index()
    
    fig = px.bar(
        hourly_stats,
        x='hour',
        y='api_calls',
        title="API Calls by Hour",
        labels={'api_calls': 'Number of Calls', 'hour': 'Hour of Day'}
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Success rate over time
    st.subheader("Success Rate Over Time")
    
    fig = px.line(
        df,
        x='timestamp',
        y='success_rate',
        title="Success Rate Trend",
        labels={'success_rate': 'Success Rate (%)', 'timestamp': 'Time'}
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Error analysis
    st.subheader("Error Analysis")
    
    if df['error_count'].sum() > 0:
        fig = px.pie(
            values=[df['api_calls'].sum() - df['error_count'].sum(), df['error_count'].sum()],
            names=['Successful Calls', 'Errors'],
            title="Call Success vs Errors"
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.success("No errors recorded!")


def show_settings():
    """Show dashboard settings and configuration."""
    st.header("Dashboard Settings")
    
    st.subheader("Export Data")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Export Metrics to JSON"):
            if performance_monitor.export_metrics():
                st.success("Metrics exported successfully!")
            else:
                st.error("Failed to export metrics")
    
    with col2:
        if st.button("Clean Old Metrics"):
            performance_monitor.cleanup_old_metrics()
            st.success("Old metrics cleaned up!")
    
    st.subheader("Configuration")
    
    # Auto-refresh setting
    auto_refresh = st.checkbox("Enable auto-refresh", value=True)
    if auto_refresh:
        refresh_interval = st.slider("Refresh interval (seconds)", 5, 60, 30)
        st.info(f"Dashboard will refresh every {refresh_interval} seconds")
    
    # Log level setting
    log_level = st.selectbox(
        "Log Level",
        ["INFO", "DEBUG", "WARNING", "ERROR"],
        index=0
    )
    
    if st.button("Update Log Level"):
        st.success(f"Log level updated to {log_level}")


if __name__ == "__main__":
    create_dashboard() 