"""
Cohort Pulse
A beautifully designed cohort analysis tool.
"""

import streamlit as st
import pandas as pd
import altair as alt
from cohort_analysis import (
    load_and_validate_data,
    calculate_cohorts,
    build_retention_table,
    build_revenue_table,
    build_customer_count_table,
    get_cohort_summary,
    style_retention_table,
    style_revenue_table,
    style_customer_table,
    export_to_excel,
    get_advanced_metrics,
    get_cohort_sizes,
    get_retention_curve,
    generate_insights,
    get_frequency_segments,
    get_revenue_segments,
    get_retention_by_frequency,
    get_retention_by_revenue_segment
)

# Page configuration
st.set_page_config(
    page_title="Cohort Pulse",
    page_icon="🟣",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Cohort Pulse Logo SVG - modern gradient style
LOGO_SVG = """
<svg width="44" height="44" viewBox="0 0 44 44" fill="none" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="logoGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#7c3aed"/>
      <stop offset="100%" style="stop-color:#5b21b6"/>
    </linearGradient>
  </defs>
  <rect width="44" height="44" rx="12" fill="url(#logoGrad)"/>
  <circle cx="22" cy="22" r="12" stroke="white" stroke-width="2" fill="none" opacity="0.25"/>
  <circle cx="22" cy="22" r="7" stroke="white" stroke-width="2" fill="none" opacity="0.5"/>
  <circle cx="22" cy="22" r="3" fill="white"/>
</svg>
"""

# Premium modern CSS with Plus Jakarta Sans
st.markdown("""
<style>
    /* Import Plus Jakarta Sans - modern geometric font */
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');

    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Root variables - refined dark accents */
    :root {
        --text-primary: #0f172a;
        --text-secondary: #475569;
        --text-tertiary: #94a3b8;
        --bg-primary: #ffffff;
        --bg-secondary: #f8fafc;
        --bg-tertiary: #f1f5f9;
        --border-color: #e2e8f0;
        --accent: #7c3aed;
        --accent-light: #a78bfa;
        --accent-bg: #f5f3ff;
        --success: #059669;
        --success-bg: #ecfdf5;
        --warning: #d97706;
        --warning-bg: #fffbeb;
        --radius-sm: 10px;
        --radius-md: 14px;
        --radius-lg: 20px;
        --shadow-sm: 0 1px 3px rgba(15, 23, 42, 0.04), 0 1px 2px rgba(15, 23, 42, 0.02);
        --shadow-md: 0 4px 16px rgba(15, 23, 42, 0.08), 0 2px 4px rgba(15, 23, 42, 0.04);
        --shadow-lg: 0 12px 40px rgba(15, 23, 42, 0.12), 0 4px 12px rgba(15, 23, 42, 0.06);
        --transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
    }

    /* Global styles */
    .stApp {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
        background: linear-gradient(180deg, var(--bg-secondary) 0%, #ffffff 100%);
        color: var(--text-primary);
    }

    /* Main container */
    .block-container {
        padding: 3rem 2.5rem 4rem !important;
        max-width: 1140px !important;
    }

    /* Typography */
    h1, h2, h3, h4, h5, h6 {
        font-weight: 700 !important;
        letter-spacing: -0.03em !important;
        color: var(--text-primary) !important;
    }

    p, span, label {
        color: var(--text-secondary);
        line-height: 1.6;
    }

    /* Logo and header area */
    .logo-container {
        display: flex;
        align-items: center;
        gap: 16px;
        margin-bottom: 12px;
    }

    .logo-text {
        font-size: 1.875rem;
        font-weight: 800;
        letter-spacing: -0.04em;
        color: var(--text-primary);
        background: linear-gradient(135deg, var(--accent) 0%, #5b21b6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }

    .tagline {
        font-size: 1.1875rem;
        color: var(--text-secondary);
        font-weight: 400;
        margin-bottom: 2.5rem;
        line-height: 1.6;
        max-width: 520px;
    }

    /* File uploader - modern glass style */
    [data-testid="stFileUploader"] {
        background: var(--bg-primary);
        border: 2px dashed var(--border-color);
        border-radius: var(--radius-lg);
        padding: 3rem 2rem;
        transition: var(--transition);
        position: relative;
    }

    [data-testid="stFileUploader"]:hover {
        border-color: var(--accent);
        background: var(--accent-bg);
        border-style: solid;
    }

    [data-testid="stFileUploader"] label {
        font-size: 1rem !important;
        font-weight: 600 !important;
        color: var(--text-primary) !important;
    }

    [data-testid="stFileUploader"] small {
        color: var(--text-tertiary) !important;
    }

    /* Metric cards - elevated glass style */
    [data-testid="stMetric"] {
        background: var(--bg-primary);
        border: 1px solid var(--border-color);
        border-radius: var(--radius-md);
        padding: 1.75rem 1.5rem;
        box-shadow: var(--shadow-sm);
        transition: var(--transition);
        position: relative;
        overflow: hidden;
    }

    [data-testid="stMetric"]::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(90deg, var(--accent) 0%, var(--accent-light) 100%);
        opacity: 0;
        transition: var(--transition);
    }

    [data-testid="stMetric"]:hover {
        box-shadow: var(--shadow-md);
        transform: translateY(-3px);
        border-color: var(--accent-light);
    }

    [data-testid="stMetric"]:hover::before {
        opacity: 1;
    }

    [data-testid="stMetricLabel"] {
        font-size: 0.75rem !important;
        font-weight: 600 !important;
        color: var(--text-tertiary) !important;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-bottom: 0.5rem;
    }

    [data-testid="stMetricValue"] {
        font-size: 2rem !important;
        font-weight: 800 !important;
        color: var(--text-primary) !important;
        letter-spacing: -0.03em;
    }

    /* Tabs - modern segmented control */
    .stTabs [data-baseweb="tab-list"] {
        gap: 6px;
        background: var(--bg-tertiary);
        padding: 6px;
        border-radius: var(--radius-md);
        border: 1px solid var(--border-color);
    }

    .stTabs [data-baseweb="tab"] {
        border-radius: var(--radius-sm);
        font-weight: 600;
        font-size: 0.875rem;
        padding: 0.75rem 1.5rem;
        color: var(--text-secondary);
        background: transparent;
        border: none;
        transition: var(--transition);
    }

    .stTabs [data-baseweb="tab"]:hover {
        color: var(--text-primary);
        background: rgba(255, 255, 255, 0.7);
    }

    .stTabs [aria-selected="true"] {
        background: var(--bg-primary) !important;
        color: var(--accent) !important;
        box-shadow: var(--shadow-md);
        font-weight: 700;
    }

    /* Dataframe container */
    [data-testid="stDataFrame"] {
        background: var(--bg-primary);
        border: 1px solid var(--border-color);
        border-radius: var(--radius-md);
        overflow: hidden;
        box-shadow: var(--shadow-sm);
    }

    /* Download buttons - gradient accent style */
    .stDownloadButton > button {
        background: linear-gradient(135deg, var(--accent) 0%, #5b21b6 100%) !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: var(--radius-sm) !important;
        padding: 0.875rem 1.75rem !important;
        font-weight: 600 !important;
        font-size: 0.875rem !important;
        transition: var(--transition) !important;
        box-shadow: 0 4px 14px rgba(124, 58, 237, 0.35) !important;
    }

    .stDownloadButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(124, 58, 237, 0.45) !important;
    }

    .stDownloadButton > button p, .stDownloadButton > button span {
        color: #ffffff !important;
    }

    /* Expander - modern style */
    .streamlit-expanderHeader {
        font-weight: 600 !important;
        font-size: 0.9375rem !important;
        color: var(--text-primary) !important;
        background: var(--bg-tertiary) !important;
        border-radius: var(--radius-sm) !important;
        padding: 1rem 1.25rem !important;
        border: none !important;
    }

    [data-testid="stExpander"] {
        border: 1px solid var(--border-color) !important;
        border-radius: var(--radius-md) !important;
        overflow: hidden;
        box-shadow: var(--shadow-sm);
    }

    /* Success message */
    .stSuccess {
        background: var(--success-bg) !important;
        border: 1px solid #a7f3d0 !important;
        border-radius: var(--radius-sm) !important;
        color: var(--success) !important;
        font-weight: 500;
    }

    /* Error message */
    .stError {
        background: #fef2f2 !important;
        border: 1px solid #fecaca !important;
        border-radius: var(--radius-sm) !important;
        color: #dc2626 !important;
        font-weight: 500;
    }

    /* Divider */
    hr {
        margin: 3rem 0 !important;
        border: none !important;
        border-top: 1px solid var(--border-color) !important;
    }

    /* Section headers */
    .section-header {
        font-size: 1.375rem;
        font-weight: 700;
        color: var(--text-primary);
        margin-bottom: 1.5rem;
        letter-spacing: -0.03em;
    }

    .section-subtext {
        font-size: 0.9375rem;
        color: var(--text-secondary);
        margin-bottom: 1.5rem;
        line-height: 1.6;
    }

    /* Column chips - modern pill style */
    .column-chip {
        display: inline-flex;
        align-items: center;
        background: var(--accent-bg);
        padding: 0.625rem 1rem;
        border-radius: 100px;
        font-family: 'JetBrains Mono', 'SF Mono', monospace;
        font-size: 0.8125rem;
        color: var(--accent);
        font-weight: 600;
        margin-right: 0.625rem;
        margin-bottom: 0.625rem;
        border: 1px solid rgba(124, 58, 237, 0.15);
    }

    /* Info card */
    .info-card {
        background: linear-gradient(135deg, var(--bg-primary) 0%, var(--bg-tertiary) 100%);
        border: 1px solid var(--border-color);
        border-radius: var(--radius-lg);
        padding: 2rem;
        margin-bottom: 1.5rem;
        box-shadow: var(--shadow-sm);
    }

    .info-card-title {
        font-size: 0.9375rem;
        font-weight: 700;
        color: var(--accent);
        margin-bottom: 0.5rem;
        letter-spacing: -0.01em;
    }

    .info-card-text {
        font-size: 1rem;
        color: var(--text-secondary);
        margin: 0;
        line-height: 1.65;
    }

    /* Date range badge */
    .date-badge {
        display: inline-flex;
        align-items: center;
        background: var(--bg-tertiary);
        padding: 0.5rem 1rem;
        border-radius: 100px;
        font-size: 0.8125rem;
        font-weight: 500;
        color: var(--text-secondary);
        margin-top: 1.25rem;
        border: 1px solid var(--border-color);
    }

    /* Insight cards - modern elevated style */
    .insight-card {
        background: var(--bg-primary);
        border: 1px solid var(--border-color);
        border-radius: var(--radius-md);
        padding: 1.5rem;
        margin-bottom: 1rem;
        border-left: 4px solid var(--accent);
        box-shadow: var(--shadow-sm);
        transition: var(--transition);
    }

    .insight-card:hover {
        box-shadow: var(--shadow-md);
        transform: translateX(4px);
    }

    .insight-card.positive {
        border-left-color: var(--success);
        background: linear-gradient(90deg, var(--success-bg) 0%, var(--bg-primary) 30%);
    }

    .insight-card.warning {
        border-left-color: var(--warning);
        background: linear-gradient(90deg, var(--warning-bg) 0%, var(--bg-primary) 30%);
    }

    .insight-card.info {
        border-left-color: var(--accent);
        background: linear-gradient(90deg, var(--accent-bg) 0%, var(--bg-primary) 30%);
    }

    .insight-title {
        font-size: 0.9375rem;
        font-weight: 700;
        color: var(--text-primary);
        margin-bottom: 0.375rem;
        letter-spacing: -0.01em;
    }

    .insight-text {
        font-size: 0.9375rem;
        color: var(--text-secondary);
        margin: 0;
        line-height: 1.6;
    }

    /* Chart container */
    .chart-container {
        background: var(--bg-primary);
        border: 1px solid var(--border-color);
        border-radius: var(--radius-lg);
        padding: 1.75rem;
        margin-bottom: 1.5rem;
        box-shadow: var(--shadow-sm);
    }

    /* Footer */
    .footer {
        text-align: center;
        padding: 2rem 0 1rem;
        color: var(--text-tertiary);
        font-size: 0.8125rem;
        font-weight: 500;
    }

    /* Spinner */
    .stSpinner > div {
        border-color: var(--accent) transparent transparent transparent !important;
    }

    /* Hide file uploader instructions */
    [data-testid="stFileUploader"] section > div:first-child {
        display: none;
    }

    /* Altair chart styling */
    .vega-embed {
        width: 100% !important;
    }

    /* Selection and focus states */
    ::selection {
        background: var(--accent-bg);
        color: var(--accent);
    }

    /* Scrollbar styling */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }

    ::-webkit-scrollbar-track {
        background: var(--bg-tertiary);
        border-radius: 4px;
    }

    ::-webkit-scrollbar-thumb {
        background: var(--text-tertiary);
        border-radius: 4px;
    }

    ::-webkit-scrollbar-thumb:hover {
        background: var(--text-secondary);
    }
</style>
""", unsafe_allow_html=True)

# Header with logo
st.markdown(f"""
<div class="logo-container">
    <div style="width: 40px; height: 40px; flex-shrink: 0;">{LOGO_SVG}</div>
    <span class="logo-text">Cohort Pulse</span>
</div>
""", unsafe_allow_html=True)
st.markdown('<p class="tagline">Understand your customer retention at a glance. Upload your order data to get started.</p>', unsafe_allow_html=True)

# Required columns display
st.markdown("""
<div style="margin-bottom: 1.5rem;">
    <span class="column-chip">order_date</span>
    <span class="column-chip">customer_ID</span>
    <span class="column-chip">order_amount</span>
</div>
""", unsafe_allow_html=True)

# File uploader
uploaded_file = st.file_uploader("Drop your CSV file here", type=['csv'], label_visibility="collapsed")

if uploaded_file is not None:
    # Load and validate data
    with st.spinner("Analyzing your data..."):
        df, error = load_and_validate_data(uploaded_file)

    if error:
        st.error(f"{error}")
    else:
        st.success("Data loaded successfully")

        # Show data preview
        with st.expander("Preview uploaded data", expanded=False):
            st.dataframe(df.head(20), use_container_width=True, hide_index=True)

        # Calculate cohorts and metrics
        with st.spinner("Building cohort analysis..."):
            df_cohorts = calculate_cohorts(df)
            retention_table = build_retention_table(df_cohorts)
            revenue_table = build_revenue_table(df_cohorts)
            customer_table = build_customer_count_table(df_cohorts)
            advanced_metrics = get_advanced_metrics(df_cohorts)
            cohort_sizes = get_cohort_sizes(df_cohorts)
            retention_curve = get_retention_curve(df_cohorts)
            insights = generate_insights(df_cohorts, retention_table)
            frequency_segments = get_frequency_segments(df_cohorts)
            revenue_segments = get_revenue_segments(df_cohorts)
            retention_by_freq = get_retention_by_frequency(df_cohorts)
            retention_by_rev = get_retention_by_revenue_segment(df_cohorts)

        # Summary metrics
        summary = get_cohort_summary(df_cohorts)

        st.markdown("---")
        st.markdown('<p class="section-header">Overview</p>', unsafe_allow_html=True)

        # Metrics in 2 columns x 3 rows layout
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Orders", f"{summary['total_orders']:,}")
        with col2:
            st.metric("Unique Customers", f"{summary['unique_customers']:,}")

        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Revenue", f"${summary['total_revenue']:,.0f}")
        with col2:
            st.metric("Avg Order Value", f"${advanced_metrics['aov']:,.2f}")

        col1, col2 = st.columns(2)
        with col1:
            st.metric("Customer LTV", f"${advanced_metrics['ltv']:,.2f}")
        with col2:
            st.metric("Repeat Rate", f"{advanced_metrics['repeat_rate']:.1f}%")

        st.markdown(f'<div class="date-badge">{summary["date_range"]}</div>', unsafe_allow_html=True)

        # Key Insights Section
        if insights:
            st.markdown("---")
            st.markdown('<p class="section-header">Key Insights</p>', unsafe_allow_html=True)

            for insight in insights:
                insight_type = insight.get('type', 'info')
                st.markdown(f"""
                <div class="insight-card {insight_type}">
                    <p class="insight-title">{insight['title']}</p>
                    <p class="insight-text">{insight['text']}</p>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("---")

        # Charts Section
        st.markdown('<p class="section-header">Trends</p>', unsafe_allow_html=True)

        chart_col1, chart_col2 = st.columns(2)

        with chart_col1:
            st.markdown('<p class="section-subtext" style="margin-bottom: 0.75rem;">Retention Curve</p>', unsafe_allow_html=True)
            # Retention curve line chart
            retention_chart = alt.Chart(retention_curve).mark_line(
                point=alt.OverlayMarkDef(filled=True, size=70),
                strokeWidth=3,
                color='#7c3aed'
            ).encode(
                x=alt.X('month:Q', title='Month', axis=alt.Axis(tickMinStep=1, labelAngle=0)),
                y=alt.Y('retention:Q', title='Retention %', scale=alt.Scale(domain=[0, 100])),
                tooltip=[
                    alt.Tooltip('month:Q', title='Month'),
                    alt.Tooltip('retention:Q', title='Retention %', format='.1f')
                ]
            ).properties(
                height=300
            ).configure_axis(
                labelFontSize=11,
                titleFontSize=12,
                titleFontWeight=600,
                labelColor='#475569',
                titleColor='#0f172a',
                gridColor='#f1f5f9'
            ).configure_view(
                strokeWidth=0
            )
            st.altair_chart(retention_chart, use_container_width=True)

        with chart_col2:
            st.markdown('<p class="section-subtext" style="margin-bottom: 0.75rem;">New Customers by Cohort</p>', unsafe_allow_html=True)
            # Cohort size bar chart
            cohort_chart = alt.Chart(cohort_sizes).mark_bar(
                color='#7c3aed',
                cornerRadiusTopLeft=6,
                cornerRadiusTopRight=6
            ).encode(
                x=alt.X('cohort_month:N', title='Cohort', axis=alt.Axis(labelAngle=-45)),
                y=alt.Y('new_customers:Q', title='New Customers'),
                tooltip=[
                    alt.Tooltip('cohort_month:N', title='Cohort'),
                    alt.Tooltip('new_customers:Q', title='New Customers')
                ]
            ).properties(
                height=300
            ).configure_axis(
                labelFontSize=11,
                titleFontSize=12,
                titleFontWeight=600,
                labelColor='#475569',
                titleColor='#0f172a',
                gridColor='#f1f5f9'
            ).configure_view(
                strokeWidth=0
            )
            st.altair_chart(cohort_chart, use_container_width=True)

        # Retention by Segment Section
        st.markdown('<p class="section-header">Retention by Segment</p>', unsafe_allow_html=True)

        seg_col1, seg_col2 = st.columns(2)

        with seg_col1:
            st.markdown('<p class="section-subtext" style="margin-bottom: 0.75rem;">Retention by Purchase Frequency</p>', unsafe_allow_html=True)
            if not retention_by_freq.empty:
                freq_chart = alt.Chart(retention_by_freq).mark_bar(
                    cornerRadiusTopLeft=6,
                    cornerRadiusTopRight=6
                ).encode(
                    x=alt.X('frequency_segment:N', title='Frequency Segment',
                            sort=['1 order', '2 orders', '3-4 orders', '5+ orders'],
                            axis=alt.Axis(labelAngle=0)),
                    y=alt.Y('retention_rate:Q', title='Retention Rate %', scale=alt.Scale(domain=[0, 100])),
                    color=alt.Color('frequency_segment:N',
                                   scale=alt.Scale(range=['#c4b5fd', '#a78bfa', '#8b5cf6', '#7c3aed']),
                                   legend=None),
                    tooltip=[
                        alt.Tooltip('frequency_segment:N', title='Segment'),
                        alt.Tooltip('retention_rate:Q', title='Retention %', format='.1f'),
                        alt.Tooltip('customer_count:Q', title='Customers')
                    ]
                ).properties(
                    height=300
                ).configure_axis(
                    labelFontSize=11,
                    titleFontSize=12,
                    titleFontWeight=600,
                    labelColor='#475569',
                    titleColor='#0f172a',
                    gridColor='#f1f5f9'
                ).configure_view(
                    strokeWidth=0
                )
                st.altair_chart(freq_chart, use_container_width=True)
            else:
                st.info("Not enough data to calculate frequency-based retention.")

        with seg_col2:
            st.markdown('<p class="section-subtext" style="margin-bottom: 0.75rem;">Retention by Revenue Tier</p>', unsafe_allow_html=True)
            if not retention_by_rev.empty:
                rev_chart = alt.Chart(retention_by_rev).mark_bar(
                    cornerRadiusTopLeft=6,
                    cornerRadiusTopRight=6
                ).encode(
                    x=alt.X('revenue_segment:N', title='Revenue Tier',
                            sort=['Low', 'Medium', 'High', 'Premium'],
                            axis=alt.Axis(labelAngle=0)),
                    y=alt.Y('retention_rate:Q', title='Retention Rate %', scale=alt.Scale(domain=[0, 100])),
                    color=alt.Color('revenue_segment:N',
                                   scale=alt.Scale(range=['#fde68a', '#fbbf24', '#f59e0b', '#d97706']),
                                   legend=None),
                    tooltip=[
                        alt.Tooltip('revenue_segment:N', title='Tier'),
                        alt.Tooltip('retention_rate:Q', title='Retention %', format='.1f'),
                        alt.Tooltip('customer_count:Q', title='Customers')
                    ]
                ).properties(
                    height=300
                ).configure_axis(
                    labelFontSize=11,
                    titleFontSize=12,
                    titleFontWeight=600,
                    labelColor='#475569',
                    titleColor='#0f172a',
                    gridColor='#f1f5f9'
                ).configure_view(
                    strokeWidth=0
                )
                st.altair_chart(rev_chart, use_container_width=True)
            else:
                st.info("Not enough data to calculate revenue-based retention.")

        st.markdown("---")

        # Cohort tables in tabs
        st.markdown('<p class="section-header">Cohort Tables</p>', unsafe_allow_html=True)

        tab1, tab2, tab3 = st.tabs(["Retention", "Revenue", "Customers"])

        with tab1:
            st.markdown("""
            <p class="section-subtext">Percentage of customers returning each month after their first purchase.</p>
            """, unsafe_allow_html=True)
            st.dataframe(
                style_retention_table(retention_table),
                use_container_width=True,
                height=420
            )

        with tab2:
            st.markdown("""
            <p class="section-subtext">Total revenue generated by each cohort in subsequent months.</p>
            """, unsafe_allow_html=True)
            st.dataframe(
                style_revenue_table(revenue_table),
                use_container_width=True,
                height=420
            )

        with tab3:
            st.markdown("""
            <p class="section-subtext">Number of unique active customers from each cohort per month.</p>
            """, unsafe_allow_html=True)
            st.dataframe(
                style_customer_table(customer_table),
                use_container_width=True,
                height=420
            )

        st.markdown("---")

        # Export options
        st.markdown('<p class="section-header">Export</p>', unsafe_allow_html=True)

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            excel_data = export_to_excel(retention_table, revenue_table, customer_table)
            st.download_button(
                label="All Data (.xlsx)",
                data=excel_data,
                file_name="cohort_pulse_export.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

        with col2:
            st.download_button(
                label="Retention (.csv)",
                data=retention_table.to_csv(),
                file_name="retention.csv",
                mime="text/csv"
            )

        with col3:
            st.download_button(
                label="Revenue (.csv)",
                data=revenue_table.to_csv(),
                file_name="revenue.csv",
                mime="text/csv"
            )

        with col4:
            st.download_button(
                label="Customers (.csv)",
                data=customer_table.to_csv(),
                file_name="customers.csv",
                mime="text/csv"
            )

else:
    # Empty state
    st.markdown("""
    <div class="info-card">
        <p class="info-card-title">Getting started</p>
        <p class="info-card-text">
            Upload a CSV file with your order history. The analysis will automatically group
            customers by their first purchase month and track their behavior over time.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<p class="section-header">Example format</p>', unsafe_allow_html=True)
    sample_data = pd.DataFrame({
        'order_date': ['2024-01-15', '2024-01-20', '2024-02-10', '2024-02-15'],
        'customer_ID': ['C001', 'C002', 'C001', 'C003'],
        'order_amount': [99.99, 149.50, 79.99, 199.00]
    })
    st.dataframe(sample_data, use_container_width=True, hide_index=True)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 1rem 0;">
    <p style="color: #9ca3af; font-size: 0.75rem; margin: 0 0 0.5rem 0;">
        For demonstration purposes only. Your data is processed locally and is not stored on our servers.
    </p>
    <p class="footer" style="margin: 0;">Cohort Pulse</p>
</div>
""", unsafe_allow_html=True)
