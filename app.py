import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import numpy as np
import io
from functools import lru_cache

# This must be the first Streamlit command
st.set_page_config(
    page_title="Sales Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Format helper functions
def format_amount(x):
    try:
        if pd.isna(x) or x == 0:
            return "₹0L"
        # Convert to float first to handle string inputs, then to int
        value = float(str(x).replace('₹', '').replace('L', '').replace(',', ''))
        return f"₹{int(value)}L"
    except:
        return "₹0L"

def format_percentage(x):
    try:
        if pd.isna(x) or x == 0:
            return "0%"
        # Handle string percentage inputs
        if isinstance(x, str):
            value = float(x.rstrip('%'))
        else:
            value = float(x)
        return f"{int(value)}%"
    except:
        return "0%"

def format_number(x):
    try:
        if pd.isna(x) or x == 0:
            return "0"
        # Convert to float first to handle string inputs, then to int
        value = float(str(x).replace(',', ''))
        return f"{int(value):,}"
    except:
        return "0"

# Initialize session state
if 'df' not in st.session_state:
    st.session_state.df = None
if 'current_view' not in st.session_state:
    st.session_state.current_view = 'data_input'
if 'date_filter' not in st.session_state:
    st.session_state.date_filter = None
if 'selected_practice' not in st.session_state:
    st.session_state.selected_practice = 'All'
if 'selected_stage' not in st.session_state:
    st.session_state.selected_stage = 'All'
if 'reset_triggered' not in st.session_state:
    st.session_state.reset_triggered = False
if 'selected_team_member' not in st.session_state:
    st.session_state.selected_team_member = None

# Keep a single "sales_target" in session state
if 'sales_target' not in st.session_state:
    st.session_state.sales_target = 0.0  # Default target in Lakhs

# Custom CSS for modern styling
st.markdown("""
<style>
    /* Modern theme colors */
    :root {
        --primary-color: #4A90E2;
        --background-color: #1E1E1E;
        --secondary-background-color: #252526;
        --text-color: #FFFFFF;
        --font-family: 'Segoe UI', sans-serif;
    }

    /* Main container styling */
    .main {
        background-color: var(--background-color);
        color: var(--text-color);
        font-family: var(--font-family);
    }

    /* Card styling */
    .stCard {
        background-color: var(--secondary-background-color);
        border-radius: 10px;
        padding: 15px;
        margin: 30px 0;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }

    /* Number formatting */
    .big-number {
        font-size: 2.8em;
        font-weight: 700;
        color: #2ecc71;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.2);
        letter-spacing: -1px;
    }

    .metric-value {
        font-size: 2em;
        font-weight: 600;
        color: #4A90E2;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
    }

    .metric-label {
        font-size: 1.2em;
        color: #333;
        margin-bottom: 5px;
        font-weight: 500;
    }

    /* Section headers */
    .section-header {
        font-size: 1.8em;
        font-weight: 700;
        color: #2c3e50;
        margin: 30px 0;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
    }

    /* Chart text styling */
    .js-plotly-plot .plotly .main-svg {
        font-size: 14px;
        font-weight: 500;
    }

    /* Table styling */
    .dataframe {
        font-size: 1.2em;
        background-color: white;
        border-radius: 8px;
        padding: 15px;
    }

    .dataframe th {
        background-color: #4A90E2;
        color: white;
        font-weight: 700;
        padding: 15px;
        font-size: 1.1em;
    }

    .dataframe td {
        padding: 12px;
        border-bottom: 1px solid #eee;
        font-weight: 500;
    }

    /* Upload container styling */
    .upload-container {
        background-color: rgba(74, 144, 226, 0.1);
        border-radius: 10px;
        padding: 30px;
        margin: 20px 0;
        border: 2px dashed rgba(74, 144, 226, 0.3);
        text-align: center;
    }

    /* Button styling */
    .stButton>button {
        background-color: var(--primary-color);
        color: white;
        border-radius: 5px;
        padding: 10px 20px;
        border: none;
        transition: all 0.3s ease;
    }

    .stButton>button:hover {
        background-color: #357ABD;
        transform: translateY(-2px);
    }

    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    /* Custom header */
    .custom-header {
        background: linear-gradient(90deg, #4A90E2 0%, #357ABD 100%);
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
        color: white;
        text-align: center;
    }

    /* Info box */
    .info-box {
        background-color: rgba(74, 144, 226, 0.1);
        border-left: 4px solid #4A90E2;
        padding: 15px;
        border-radius: 4px;
        margin: 10px 0;
    }

    /* Container styling */
    .container {
        margin: 30px 0;
        padding: 15px;
    }

    /* Graph container */
    .graph-container {
        margin: 30px 0;
        padding: 15px;
        background: white;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }

    /* Metric container */
    .metric-container {
        display: flex;
        justify-content: space-between;
        margin: 20px 0;
        gap: 20px;
    }
    
    .card {
        background: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        flex: 1;
        text-align: center;
    }
    
    .metric-label {
        color: #666;
        font-size: 14px;
        font-weight: 600;
        margin-bottom: 8px;
    }
    
    .metric-value {
        font-size: 24px;
        font-weight: 700;
        color: #2a5298;
    }
    
    .delta-positive {
        color: #2ecc71;
    }
    
    .delta-negative {
        color: #e74c3c;
    }

    /* Section divider */
    .section-divider {
        margin: 30px 0;
        border-top: 1px solid #eee;
    }

    /* Custom styling for number input */
    [data-testid="stNumberInput"] {
        position: relative;
        background: transparent !important;
    }
    [data-testid="stNumberInput"] > div > div > input {
        color: white !important;
        font-size: 1.8em !important;
        font-weight: 800 !important;
        text-align: center !important;
        background: transparent !important;
        border: none !important;
        padding: 0 !important;
    }
    /* Hide the increment/decrement buttons */
    [data-testid="stNumberInput"] > div > div > div {
        display: none !important;
    }
    /* Container styling */
    div[data-testid="column"] > div > div > div > div > div {
        background: linear-gradient(135deg, #FF6B6B 0%, #FF8E8E 100%);
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        text-align: center;
    }

    /* Hide increment buttons */
    [data-testid="stNumberInput"] input[type="number"] {
        -moz-appearance: textfield;
    }
    [data-testid="stNumberInput"] input[type="number"]::-webkit-outer-spin-button,
    [data-testid="stNumberInput"] input[type="number"]::-webkit-inner-spin-button {
        -webkit-appearance: none;
        margin: 0;
    }
    
    /* Style the input field */
    [data-testid="stNumberInput"] {
        background: transparent;
    }
    
    /* Style the display value */
    .target-value {
        font-family: 'Segoe UI', sans-serif;
        font-size: 2.5em;
        font-weight: 800;
        color: #FF6B6B;
        text-align: center;
        padding: 20px;
        margin: 10px 0;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
    }

    /* Modern Quarterly Dashboard Styles */
    .quarterly-dashboard {
        background: linear-gradient(135deg, #f0f4ff 0%, #ffffff 100%);
        padding: 2rem;
        border-radius: 20px;
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.15);
        margin: 2rem 0;
    }

    .metric-card {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(8px);
        -webkit-backdrop-filter: blur(8px);
        border: 1px solid rgba(255, 255, 255, 0.18);
        border-radius: 16px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.1);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }

    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 36px 0 rgba(31, 38, 135, 0.15);
    }

    .metric-header {
        display: flex;
        align-items: center;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid rgba(74, 144, 226, 0.1);
    }

    .metric-icon {
        font-size: 1.5rem;
        margin-right: 0.75rem;
        color: #4a90e2;
    }

    .metric-title {
        font-family: 'Inter', sans-serif;
        font-size: 1.2rem;
        font-weight: 600;
        color: #1e1e2f;
        margin: 0;
    }

    .metric-content {
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    .metric-values {
        flex: 1;
    }

    .metric-current {
        font-size: 2rem;
        font-weight: 700;
        color: #1e1e2f;
        margin: 0.5rem 0;
    }

    .metric-previous {
        font-size: 1.1rem;
        color: #6b7280;
        margin: 0.25rem 0;
    }

    .metric-delta {
        background: rgba(255, 255, 255, 0.9);
        padding: 0.75rem 1rem;
        border-radius: 12px;
        text-align: center;
        min-width: 120px;
    }

    .delta-positive {
        color: #00c896;
    }

    .delta-negative {
        color: #ff5b5b;
    }

    .delta-value {
        font-size: 1.5rem;
        font-weight: 600;
        margin: 0;
    }

    .delta-label {
        font-size: 0.9rem;
        color: #6b7280;
        margin: 0;
    }

    /* Filter section styling */
    .filter-section {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
        padding: 1.5rem;
        border-radius: 16px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        margin-bottom: 2rem;
    }

    .filter-title {
        color: #1e1e2f;
        font-size: 1.2rem;
        font-weight: 600;
        margin-bottom: 1rem;
    }

    /* Selectbox styling */
    .stSelectbox {
        background: white;
        border-radius: 12px;
        border: 1px solid rgba(0,0,0,0.1);
    }

    .stSelectbox > div {
        background: white !important;
    }
</style>
""", unsafe_allow_html=True)

# Cache data processing functions
@st.cache_data
def process_data(df):
    """Process and prepare data for the dashboard"""
    df = df.copy()
    
    # Convert dates and calculate time-based columns at once
    df['Expected Close Date'] = pd.to_datetime(df['Expected Close Date'], format='%d-%m-%Y', errors='coerce')
    df['Month'] = df['Expected Close Date'].dt.strftime('%B')
    df['Year'] = df['Expected Close Date'].dt.year
    df['Quarter'] = df['Expected Close Date'].dt.quarter.map({1: 'Q1', 2: 'Q2', 3: 'Q3', 4: 'Q4'})
    
    # Convert probability and calculate numeric values at once with safe null handling
    def convert_probability(x):
        try:
            if pd.isna(x):
                return 0
            if isinstance(x, str):
                x = x.rstrip('%')
            return float(x)
        except:
            return 0
    
    df['Probability_Num'] = df['Probability'].apply(convert_probability)
    
    # Pre-calculate common flags and metrics with safe null handling
    df['Is_Won'] = df['Sales Stage'].str.contains('Won', case=False, na=False)
    df['Amount_Lacs'] = df['Amount'].fillna(0).div(100000).round(0).astype(int)
    df['Weighted_Amount'] = (df['Amount_Lacs'] * df['Probability_Num'] / 100).round(0).astype(int)
    
    return df

@st.cache_data
def calculate_team_metrics(df):
    """Calculate all team-related metrics at once"""
    team_metrics = df.groupby('Sales Owner').agg({
        'Amount': lambda x: int(x[df['Is_Won'] & x.notna()].sum() / 100000) if len(x[df['Is_Won'] & x.notna()]) > 0 else 0,
        'Is_Won': 'sum',
        'Amount_Lacs': lambda x: int(x[~df['Is_Won'] & x.notna()].sum()) if len(x[~df['Is_Won'] & x.notna()]) > 0 else 0,
        'Weighted_Amount': lambda x: int(x[~df['Is_Won'] & x.notna()].sum()) if len(x[~df['Is_Won'] & x.notna()]) > 0 else 0
    }).reset_index()
    
    team_metrics.columns = ['Sales Owner', 'Closed Won', 'Closed Deals', 'Current Pipeline', 'Weighted Projections']
    
    team_metrics = team_metrics.fillna(0)
    
    # Calculate Pipeline Deals
    pipeline_deals = df[~df['Is_Won']].groupby('Sales Owner').size()
    team_metrics['Pipeline Deals'] = team_metrics['Sales Owner'].map(pipeline_deals).fillna(0).astype(int)
    
    # Win Rate
    total_deals = team_metrics['Closed Deals'] + team_metrics['Pipeline Deals']
    team_metrics['Win Rate'] = np.where(
        total_deals > 0,
        (team_metrics['Closed Deals'] / total_deals * 100).round(0),
        0
    ).astype(int)
    
    return team_metrics

@st.cache_data
def filter_dataframe(df, filters):
    """Apply filters to dataframe efficiently"""
    mask = pd.Series(True, index=df.index)
    
    if filters.get('selected_member') != "All Team Members":
        mask &= df['Sales Owner'] == filters['selected_member']
    
    if filters.get('search'):
        search_mask = pd.Series(False, index=df.index)
        search = filters['search'].lower()
        for col in ['Organization Name', 'Opportunity Name', 'Sales Owner', 'Sales Stage']:
            search_mask |= df[col].astype(str).str.lower().str.contains(search, na=False)
        mask &= search_mask
    
    # Practice filter
    if filters.get('practices'):
        mask &= df['Practice'].isin(filters['practices'])
            
    if filters.get('month_filter') != "All Months":
        mask &= df['Month'] == filters['month_filter']
    
    if filters.get('quarter_filter') != "All Quarters":
        mask &= df['Quarter'] == filters['quarter_filter']
    
    if filters.get('year_filter') != "All Years":
        mask &= df['Year'] == filters['year_filter']
    
    if filters.get('probability_filter') != "All Probability":
        if filters['probability_filter'] == "Custom Range":
            prob_range = filters['custom_prob_range'].split("-")
            min_prob = float(prob_range[0])
            max_prob = float(prob_range[1].rstrip("%"))
        else:
            prob_range = filters['probability_filter'].split("-")
            min_prob = float(prob_range[0])
            max_prob = float(prob_range[1].rstrip("%"))
        mask &= (df['Probability_Num'] >= min_prob) & (df['Probability_Num'] <= max_prob)
    
    if filters.get('status_filter') != "All Status":
        if filters['status_filter'] == "Committed for the Month":
            current_month = pd.Timestamp.now().strftime('%B')
            mask &= (df['Month'] == current_month) & (df['Probability_Num'] > 75)
        elif filters['status_filter'] == "Upsides for the Month":
            current_month = pd.Timestamp.now().strftime('%B')
            mask &= (df['Month'] == current_month) & (df['Probability_Num'].between(25, 75))
        else:
            mask &= df['Sales Stage'] == filters['status_filter']
    
    if filters.get('focus_filter') != "All Focus":
        mask &= df['KritiKal Focus Areas'] == filters['focus_filter']
    
    return df[mask]

def show_data_input():
    # Custom header
    st.markdown("""
        <div class="custom-header">
            <h1>Sales Performance Dashboard</h1>
            <p style="font-size: 1.2em; margin: 0;">Upload your sales data to begin analysis</p>
        </div>
    """, unsafe_allow_html=True)

    # Main upload section
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown('<div class="upload-container">', unsafe_allow_html=True)
        uploaded_file = st.file_uploader(
            "Upload Sales Data",
            type=['xlsx', 'csv'],
            help="Upload your sales data file in Excel or CSV format"
        )
        st.markdown("</div>", unsafe_allow_html=True)
        
        if uploaded_file:
            try:
                if uploaded_file.name.endswith('.xlsx'):
                    excel_file = pd.ExcelFile(uploaded_file)
                    sheet_name = st.selectbox("Select Worksheet", excel_file.sheet_names)
                    df = pd.read_excel(uploaded_file, sheet_name=sheet_name)
                else:
                    df = pd.read_csv(uploaded_file)
                
                st.session_state.df = df
                st.success(f"Successfully loaded {len(df):,} records")
                
                # Preview the data
                st.subheader("Data Preview")
                st.dataframe(df.head(), use_container_width=True)
                
            except Exception as e:
                st.error(f"Error: {str(e)}")
    
    with col2:
        st.markdown("""
        <div class="info-box">
            <h4>Required Data Fields</h4>
            <ul>
                <li>Amount</li>
                <li>Sales Stage</li>
                <li>Expected Close Date</li>
                <li>Practice/Region</li>
            </ul>
            <h4>File Formats</h4>
            <ul>
                <li>Excel (.xlsx)</li>
                <li>CSV (.csv)</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

def show_overview():
    if 'df_current' not in st.session_state or 'df_previous' not in st.session_state:
        st.warning("Please upload data first.")
        return
    
    # Use current week data by default
    df = st.session_state.df_current
    st.session_state.df = df  # Set the current df in session state for compatibility
    
    st.title("Sales Performance Overview")

    # --------------------------------------------------------
    # (1) Let user edit the target as an integer
    # --------------------------------------------------------
    st.markdown("### Enter Your Sales Target (Optional)")

    # Get existing value from session state or default to "0"
    default_target = str(int(st.session_state.get("sales_target", 0)))

    # Input as string (no steppers)
    user_target_input = st.text_input("Sales Target (in Lakhs)", value=default_target)

    # Try to convert it to int
    try:
        user_target = int(user_target_input)
    except ValueError:
        user_target = 0  # fallback value if user input is invalid

    st.write("You entered:", user_target)

    # Store as float if you like, or keep it integer
    st.session_state.sales_target = float(user_target)

    # Calculate total "Closed Won"
    won_deals = df[df['Sales Stage'].str.contains('Won', case=False, na=False)]
    won_amount_lacs = won_deals['Amount'].sum() / 100000  # convert to Lakhs

    # Show "Target vs Closed Won" progress
    if st.session_state.sales_target > 0:
        achievement_pct = (won_amount_lacs / st.session_state.sales_target) * 100
    else:
        achievement_pct = 0

    st.markdown(
        f"""
        <div style='margin-top: 30px; padding: 20px; background: #f0f2f6; border-radius: 12px;'>
            <h3 style='margin: 0; color: #2ecc71; font-size: 1.2em; font-weight: 500;'>Closed Won</h3>
            <h2 style='margin: 5px 0; color: #2ecc71; font-size: 2.8em; font-weight: 700; text-shadow: 1px 1px 2px rgba(0,0,0,0.2);'>
                ₹{won_amount_lacs:,.2f}L
            </h2>
            <div style='text-align: right; margin-bottom: 10px;'>
                <span style='color: #e74c3c; font-size: 1em; font-weight: 500;'>Target: ₹{st.session_state.sales_target:,.0f}L</span>
            </div>
            <div style='background: #e74c3c; height: 40px; border-radius: 20px; overflow: hidden; position: relative; box-shadow: inset 0 1px 3px rgba(0,0,0,0.2);'>
                <div style='background: #2ecc71; height: 100%; width: {min(achievement_pct, 100)}%; transition: width 0.5s ease-in-out;'></div>
                <div style='position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); color: white; font-weight: 600; font-size: 1.2em; text-shadow: 1px 1px 2px rgba(0,0,0,0.5);'>
                    {int(achievement_pct)}% Complete
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # ---- The rest of your existing Overview code remains below ----

    # II. Practice
    st.markdown("""
        <div style='background: linear-gradient(90deg, #4A90E2 0%, #357ABD 100%); padding: 15px; border-radius: 10px; margin-bottom: 30px;'>
            <h3 style='color: white; margin: 0; text-align: center; font-size: 1.8em; font-weight: 600;'>Practice</h3>
        </div>
    """, unsafe_allow_html=True)
    
    if 'Practice' in df.columns:
        # Add practice filter
        practices = ['All'] + sorted(df['Practice'].dropna().unique().tolist())
        selected_practice = st.selectbox(
            "Select Practice",
            options=practices,
            key="practice_filter"
        )
        
        # Filter data based on selected practice
        df_practice = df.copy()
        if selected_practice != 'All':
            df_practice = df_practice[df_practice['Practice'] == selected_practice]
        
        # Calculate practice metrics
        practice_metrics = df_practice.groupby('Practice').agg({
            'Amount': lambda x: x[df_practice['Sales Stage'].str.contains('Won', case=False, na=False)].sum() / 100000,
            'Sales Stage': lambda x: x[df_practice['Sales Stage'].str.contains('Won', case=False, na=False)].count()
        }).reset_index()
        
        practice_metrics.columns = ['Practice', 'Closed Amount', 'Closed Deals']
        
        # Pipeline by practice
        pipeline_df = df_practice[~df_practice['Sales Stage'].str.contains('Won', case=False, na=False)]
        total_pipeline = pipeline_df.groupby('Practice')['Amount'].sum() / 100000
        practice_metrics['Total Pipeline'] = practice_metrics['Practice'].map(total_pipeline)
        
        # Pipeline deal counts
        total_deals = pipeline_df.groupby('Practice').size()
        practice_metrics['Pipeline Deals'] = practice_metrics['Practice'].map(total_deals)
        
        # Sort by pipeline
        practice_metrics = practice_metrics.sort_values('Total Pipeline', ascending=False)
        
        # Charts
        col1, col2 = st.columns(2)
        
        with col1:
            fig_pipeline = go.Figure()
            fig_pipeline.add_trace(go.Bar(
                x=practice_metrics['Practice'],
                y=practice_metrics['Total Pipeline'],
                name='Pipeline',
                text=practice_metrics['Total Pipeline'].apply(lambda x: f"₹{int(x)}L"),
                textposition='outside',
                textfont=dict(size=16, color='#4A90E2', family='Segoe UI', weight='bold'),
                marker_color='#4A90E2',
                marker_line=dict(color='#357ABD', width=2),
                opacity=0.9
            ))
            fig_pipeline.add_trace(go.Bar(
                x=practice_metrics['Practice'],
                y=practice_metrics['Closed Amount'],
                name='Closed Won',
                text=practice_metrics['Closed Amount'].apply(lambda x: f"₹{int(x)}L"),
                textposition='outside',
                textfont=dict(size=16, color='#2ecc71', family='Segoe UI', weight='bold'),
                marker_color='#2ecc71',
                marker_line=dict(color='#27ae60', width=2),
                opacity=0.9
            ))
            fig_pipeline.update_layout(
                title=dict(
                    text="Practice-wise Pipeline vs Closed Won",
                    font=dict(size=22, family='Segoe UI', color='#2c3e50', weight='bold'),
                    x=0.5,
                    y=0.95,
                    xanchor='center',
                    yanchor='top'
                ),
                height=500,
                barmode='group',
                bargap=0.15,
                bargroupgap=0.1,
                xaxis_title=dict(
                    text="Practice",
                    font=dict(size=16, family='Segoe UI', color='#2c3e50', weight='bold'),
                    standoff=15
                ),
                yaxis_title=dict(
                    text="Amount (Lakhs)",
                    font=dict(size=16, family='Segoe UI', color='#2c3e50', weight='bold'),
                    standoff=15
                ),
                showlegend=True,
                legend=dict(
                    font=dict(size=14, family='Segoe UI', color='#2c3e50'),
                    yanchor="top",
                    y=0.99,
                    xanchor="right",
                    x=0.99,
                    bgcolor='rgba(255, 255, 255, 0.8)',
                    bordercolor='rgba(0, 0, 0, 0.2)',
                    borderwidth=1
                ),
                font=dict(size=14, family='Segoe UI'),
                xaxis=dict(
                    tickfont=dict(size=12, family='Segoe UI', color='#2c3e50'),
                    gridcolor='rgba(0, 0, 0, 0.1)'
                ),
                yaxis=dict(
                    tickfont=dict(size=12, family='Segoe UI', color='#2c3e50'),
                    gridcolor='rgba(0, 0, 0, 0.1)'
                ),
                plot_bgcolor='white',
                paper_bgcolor='white',
                margin=dict(t=80, b=40, l=40, r=40)
            )
            st.plotly_chart(fig_pipeline, use_container_width=True)
        
        with col2:
            fig_deals = go.Figure()
            fig_deals.add_trace(go.Bar(
                x=practice_metrics['Practice'],
                y=practice_metrics['Pipeline Deals'],
                name='Pipeline Deals',
                text=practice_metrics['Pipeline Deals'],
                textposition='outside',
                textfont=dict(size=16, color='#4A90E2', family='Segoe UI', weight='bold'),
                marker_color='#4A90E2',
                marker_line=dict(color='#357ABD', width=2),
                opacity=0.9
            ))
            fig_deals.add_trace(go.Bar(
                x=practice_metrics['Practice'],
                y=practice_metrics['Closed Deals'],
                name='Closed Deals',
                text=practice_metrics['Closed Deals'],
                textposition='outside',
                textfont=dict(size=16, color='#2ecc71', family='Segoe UI', weight='bold'),
                marker_color='#2ecc71',
                marker_line=dict(color='#27ae60', width=2),
                opacity=0.9
            ))
            fig_deals.update_layout(
                title=dict(
                    text="Practice-wise Pipeline vs Closed Deals",
                    font=dict(size=22, family='Segoe UI', color='#2c3e50', weight='bold'),
                    x=0.5,
                    y=0.95,
                    xanchor='center',
                    yanchor='top'
                ),
                height=500,
                barmode='group',
                bargap=0.15,
                bargroupgap=0.1,
                xaxis_title=dict(
                    text="Practice",
                    font=dict(size=16, family='Segoe UI', color='#2c3e50', weight='bold'),
                    standoff=15
                ),
                yaxis_title=dict(
                    text="Number of Deals",
                    font=dict(size=16, family='Segoe UI', color='#2c3e50', weight='bold'),
                    standoff=15
                ),
                showlegend=True,
                legend=dict(
                    font=dict(size=14, family='Segoe UI', color='#2c3e50'),
                    yanchor="top",
                    y=0.99,
                    xanchor="right",
                    x=0.99,
                    bgcolor='rgba(255, 255, 255, 0.8)',
                    bordercolor='rgba(0, 0, 0, 0.2)',
                    borderwidth=1
                ),
                font=dict(size=14, family='Segoe UI'),
                xaxis=dict(
                    tickfont=dict(size=12, family='Segoe UI', color='#2c3e50'),
                    gridcolor='rgba(0, 0, 0, 0.1)'
                ),
                yaxis=dict(
                    tickfont=dict(size=12, family='Segoe UI', color='#2c3e50'),
                    gridcolor='rgba(0, 0, 0, 0.1)'
                ),
                plot_bgcolor='white',
                paper_bgcolor='white',
                margin=dict(t=80, b=40, l=40, r=40)
            )
            st.plotly_chart(fig_deals, use_container_width=True)
        
        # Practice summary
        st.markdown("### Practice Summary")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_pipeline_val = practice_metrics['Total Pipeline'].sum()
            st.markdown(f"""
                <div style='text-align: center; padding: 15px; background: #f8f9fa; border-radius: 10px;'>
                    <div class='metric-label'>Total Pipeline</div>
                    <div class='metric-value'>₹{int(total_pipeline_val)}L</div>
                    <div style='color: #666; font-size: 0.9em;'>Active pipeline value</div>
                </div>
            """, unsafe_allow_html=True)
        
        with col2:
            total_deals_count = practice_metrics['Pipeline Deals'].sum()
            st.markdown(f"""
                <div style='text-align: center; padding: 15px; background: #f8f9fa; border-radius: 10px;'>
                    <div class='metric-label'>Pipeline Deals</div>
                    <div class='metric-value'>{int(total_deals_count)}</div>
                    <div style='color: #666; font-size: 0.9em;'>Active opportunities</div>
                </div>
            """, unsafe_allow_html=True)
        
        with col3:
            total_won = practice_metrics['Closed Deals'].sum()
            win_rate = (total_won / (total_won + total_deals_count) * 100) if (total_won + total_deals_count) > 0 else 0
            st.markdown(f"""
                <div style='text-align: center; padding: 15px; background: #f8f9fa; border-radius: 10px;'>
                    <div class='metric-label'>Win Rate</div>
                    <div class='metric-value'>{int(win_rate)}%</div>
                    <div style='color: #666; font-size: 0.9em;'>{int(total_won)} won</div>
                </div>
            """, unsafe_allow_html=True)
        
        with col4:
            avg_deal_size = practice_metrics['Closed Amount'].sum() / total_won if total_won > 0 else 0
            st.markdown(f"""
                <div style='text-align: center; padding: 15px; background: #f8f9fa; border-radius: 10px;'>
                    <div class='metric-label'>Avg Deal Size</div>
                    <div class='metric-value'>₹{int(avg_deal_size)}L</div>
                    <div style='color: #666; font-size: 0.9em;'>Per won deal</div>
                </div>
            """, unsafe_allow_html=True)
        
        # Practice-wise table
        st.markdown("### Practice-wise Details")
        summary_data = practice_metrics.copy()
        summary_data['Win Rate'] = (summary_data['Closed Deals'] / (summary_data['Closed Deals'] + summary_data['Pipeline Deals']) * 100).round(1)
        summary_data['Closed Amount'] = summary_data['Closed Amount'].apply(lambda x: f"₹{int(x)}L")
        summary_data['Total Pipeline'] = summary_data['Total Pipeline'].apply(lambda x: f"₹{int(x)}L")
        summary_data['Win Rate'] = summary_data['Win Rate'].apply(lambda x: f"{int(x)}%")
        
        st.dataframe(
            summary_data[['Practice', 'Closed Amount', 'Total Pipeline', 'Closed Deals', 'Pipeline Deals', 'Win Rate']],
            use_container_width=True
        )
    else:
        st.error("Practice column not found in the dataset")

    # KritiKal Focus Areas
    st.markdown("""
        <div style='background: linear-gradient(90deg, #9b59b6 0%, #8e44ad 100%); padding: 15px; border-radius: 10px; margin-bottom: 30px;'>
            <h3 style='color: white; margin: 0; text-align: center; font-size: 1.8em; font-weight: 600;'>KritiKal Focus Areas</h3>
        </div>
    """, unsafe_allow_html=True)
    
    if 'KritiKal Focus Areas' in df.columns:
        focus_metrics = df.groupby('KritiKal Focus Areas').agg({
            'Amount': 'sum',
            'Sales Stage': lambda x: x[df['Sales Stage'].str.contains('Won', case=False, na=False)].count()
        }).reset_index()
        
        focus_metrics['KritiKal Focus Areas'] = focus_metrics['KritiKal Focus Areas'].fillna('Uncategorized')
        
        focus_metrics.columns = ['Focus Area', 'Total Amount', 'Closed Deals']
        focus_metrics['Total Amount'] = focus_metrics['Total Amount'] / 100000
        
        total_deals_focus = df.groupby('KritiKal Focus Areas').size().reset_index()
        total_deals_focus.columns = ['Focus Area', 'Total Deals']
        focus_metrics = focus_metrics.merge(total_deals_focus, on='Focus Area', how='left')
        
        total_amount_focus = focus_metrics['Total Amount'].sum()
        focus_metrics['Share %'] = (focus_metrics['Total Amount'] / total_amount_focus * 100).round(1)
        
        focus_metrics = focus_metrics.sort_values('Total Amount', ascending=False)
        
        st.markdown("### Focus Areas Summary")
        summary_data = focus_metrics.copy()
        summary_data['Total Amount'] = summary_data['Total Amount'].apply(lambda x: f"₹{int(x)}L")
        summary_data['Share %'] = summary_data['Share %'].apply(lambda x: f"{int(x)}%")
        
        summary_data = summary_data.reset_index(drop=True)
        summary_data.index = summary_data.index + 1
        
        st.dataframe(
            summary_data[['Focus Area', 'Total Amount', 'Share %', 'Total Deals', 'Closed Deals']],
            use_container_width=True
        )
        
        st.markdown("### Focus Areas Distribution")
        fig_focus = go.Figure(data=[go.Pie(
            labels=focus_metrics['Focus Area'],
            values=focus_metrics['Total Amount'],
            hole=.4,
            textinfo='label+percent+value',
            texttemplate='%{label}<br>%{percent}<br>' + format_amount('%{value}'),
            textfont=dict(size=14, family='Segoe UI', weight='bold')
        )])
        
        fig_focus.update_layout(
            title=dict(
                text="Focus Areas Distribution",
                font=dict(size=22, family='Segoe UI', color='#2c3e50', weight='bold'),
                x=0.5,
                y=0.95,
                xanchor='center',
                yanchor='top'
            ),
            height=500,
            showlegend=True,
            legend=dict(
                font=dict(size=14, family='Segoe UI', color='#2c3e50'),
                yanchor="top",
                y=0.99,
                xanchor="right",
                x=0.99,
                bgcolor='rgba(255, 255, 255, 0.8)',
                bordercolor='rgba(0, 0, 0, 0.2)',
                borderwidth=1
            ),
            annotations=[dict(
                text=f"Total: ₹{int(total_amount_focus)}L",
                font=dict(size=16, family='Segoe UI', weight='bold'),
                showarrow=False,
                x=0.5,
                y=0.5
            )]
        )
        
        st.plotly_chart(fig_focus, use_container_width=True)
    else:
        st.info("KritiKal Focus Areas column not found in the dataset")

    # Monthly Pipeline Trend
    st.markdown("""
        <div style='background: linear-gradient(90deg, #00b4db 0%, #0083b0 100%); padding: 15px; border-radius: 10px; margin-bottom: 30px;'>
            <h3 style='color: white; margin: 0; text-align: center; font-size: 1.8em; font-weight: 600;'>Monthly Pipeline Trend</h3>
        </div>
    """, unsafe_allow_html=True)
    
    if 'Expected Close Date' in df.columns and 'Amount' in df.columns and 'Sales Stage' in df.columns:
        df['Expected Close Date'] = pd.to_datetime(df['Expected Close Date'], errors='coerce')
        
        deal_type = st.selectbox(
            "Select Deal Type",
            ["🌊 Pipeline", "🟢 Closed Won", "📦 All Deals"],
            index=0
        )
        
        if deal_type == "🌊 Pipeline":
            filtered_df = df[~df['Sales Stage'].str.contains('Won', case=False, na=False)]
            color = '#00b4db'
        elif deal_type == "🟢 Closed Won":
            filtered_df = df[df['Sales Stage'].str.contains('Won', case=False, na=False)]
            color = '#2ecc71'
        else:
            filtered_df = df
            color = '#9b59b6'
        
        monthly_data = filtered_df.groupby(filtered_df['Expected Close Date'].dt.to_period('M')).agg({
            'Amount': 'sum',
            'Sales Stage': 'count'
        }).reset_index()
        
        monthly_data['Expected Close Date'] = monthly_data['Expected Close Date'].astype(str)
        monthly_data['Amount'] = monthly_data['Amount'] / 100000
        
        fig_trend = go.Figure()
        fig_trend.add_trace(go.Scatter(
            x=monthly_data['Expected Close Date'],
            y=monthly_data['Amount'],
            mode='lines+markers',
            name=deal_type,
            line=dict(width=3, color=color),
            marker=dict(size=8, color=color),
            text=monthly_data['Amount'].apply(lambda x: f"₹{int(x)}L"),
            textposition='top center',
            textfont=dict(size=12, family='Segoe UI', weight='bold')
        ))
        
        fig_trend.update_layout(
            title=dict(
                text=f"{deal_type} Trend",
                font=dict(size=22, family='Segoe UI', color='#2c3e50', weight='bold'),
                x=0.5,
                y=0.95,
                xanchor='center',
                yanchor='top'
            ),
            height=500,
            showlegend=False,
            xaxis_title=dict(
                text="Month",
                font=dict(size=16, family='Segoe UI', color='#2c3e50', weight='bold'),
                standoff=15
            ),
            yaxis_title=dict(
                text="Amount (Lakhs)",
                font=dict(size=16, family='Segoe UI', color='#2c3e50', weight='bold'),
                standoff=15
            ),
            font=dict(size=14, family='Segoe UI'),
            xaxis=dict(
                tickfont=dict(size=12, family='Segoe UI', color='#2c3e50'),
                gridcolor='rgba(0, 0, 0, 0.1)'
            ),
            yaxis=dict(
                tickfont=dict(size=12, family='Segoe UI', color='#2c3e50'),
                gridcolor='rgba(0, 0, 0, 0.1)'
            ),
            plot_bgcolor='white',
            paper_bgcolor='white',
            margin=dict(t=80, b=40, l=40, r=40)
        )
        
        st.plotly_chart(fig_trend, use_container_width=True)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            total_value = monthly_data['Amount'].sum()
            st.markdown(f"""
                <div style='text-align: center; padding: 15px; background: #f8f9fa; border-radius: 10px;'>
                    <div class='metric-label'>Total Value</div>
                    <div class='metric-value'>₹{int(total_value)}L</div>
                    <div style='color: #666; font-size: 0.9em;'>Overall</div>
                </div>
            """, unsafe_allow_html=True)
        with col2:
            avg_monthly = monthly_data['Amount'].mean()
            st.markdown(f"""
                <div style='text-align: center; padding: 15px; background: #f8f9fa; border-radius: 10px;'>
                    <div class='metric-label'>Monthly Average</div>
                    <div class='metric-value'>₹{int(avg_monthly)}L</div>
                    <div style='color: #666; font-size: 0.9em;'>Per month</div>
                </div>
            """, unsafe_allow_html=True)
        with col3:
            total_deals = monthly_data['Sales Stage'].sum()
            st.markdown(f"""
                <div style='text-align: center; padding: 15px; background: #f8f9fa; border-radius: 10px;'>
                    <div class='metric-label'>Total Deals</div>
                    <div class='metric-value'>{int(total_deals)}</div>
                    <div style='color: #666; font-size: 0.9em;'>Number of deals</div>
                </div>
            """, unsafe_allow_html=True)
    else:
        st.info("Required columns (Expected Close Date, Amount, Sales Stage) not found in the dataset")

def show_sales_team():
    if st.session_state.df is None:
        st.warning("Please upload your sales data to view team information")
        return
    
    # Process data once with caching
    df = process_data(st.session_state.df)
    
    # Team members
    team_members = sorted(df['Sales Owner'].dropna().unique().tolist())
    
    st.markdown("""
        <div style='
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            padding: 25px;
            border-radius: 15px;
            margin-bottom: 25px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        '>
            <h2 style='
                color: white;
                margin: 0;
                text-align: center;
                font-size: 2em;
                font-weight: 600;
                letter-spacing: 0.5px;
                text-shadow: 1px 1px 2px rgba(0,0,0,0.2);
            '>Sales Team Data</h2>
        </div>
    """, unsafe_allow_html=True)

    metrics = calculate_team_metrics(df)
    
    col1, col2, col3, col4 = st.columns(4)
    metric_style = """
        text-align: center;
        padding: 20px;
        background: linear-gradient(135deg, {gradient});
        border-radius: 15px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        margin: 10px 5px;
    """
    metric_text_style = """
        color: #FFFFFF;
        font-family: 'Segoe UI', sans-serif;
        font-size: 2.6em;
        font-weight: 800;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.4);
        margin: 15px 0;
        letter-spacing: 0.5px;
        -webkit-font-smoothing: antialiased;
    """
    label_style = """
        color: #FFFFFF;
        font-family: 'Segoe UI', sans-serif;
        font-size: 1.5em;
        font-weight: 800;
        margin-bottom: 12px;
        text-transform: uppercase;
        letter-spacing: 1px;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        -webkit-font-smoothing: antialiased;
    """
    sublabel_style = """
        color: #FFFFFF;
        font-family: 'Segoe UI', sans-serif;
        font-size: 1.2em;
        font-weight: 700;
        margin-top: 8px;
        letter-spacing: 0.5px;
        text-shadow: 1px 1px 3px rgba(0,0,0,0.3);
        -webkit-font-smoothing: antialiased;
    """
    
    total_pipeline = metrics['Current Pipeline'].sum()
    total_closed = metrics['Closed Won'].sum()
    total_closed_deals = metrics['Closed Deals'].sum()
    total_pipeline_deals = metrics['Pipeline Deals'].sum()
    
    with col1:
        st.markdown(f"""
            <div style='{metric_style.format(gradient="#2193b0 0%, #6dd5ed 100%")}'>
                <div style='{label_style}'>Pipeline Value</div>
                <div style='{metric_text_style}'>₹{int(total_pipeline)}L</div>
                <div style='{sublabel_style}'>Active opportunities</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
            <div style='{metric_style.format(gradient="#11998e 0%, #38ef7d 100%")}'>
                <div style='{label_style}'>Closed Won</div>
                <div style='{metric_text_style}'>₹{int(total_closed)}L</div>
                <div style='{sublabel_style}'>Won opportunities</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        win_rate = round((total_closed_deals / (total_closed_deals + total_pipeline_deals) * 100), 1) if (total_closed_deals + total_pipeline_deals) > 0 else 0
        st.markdown(f"""
            <div style='{metric_style.format(gradient="#4e54c8 0%, #8f94fb 100%")}'>
                <div style='{label_style}'>Win Rate</div>
                <div style='{metric_text_style}'>{int(win_rate)}%</div>
                <div style='{sublabel_style}'>{int(total_closed_deals)} won</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col4:
        avg_deal_size = round(total_closed / total_closed_deals, 1) if total_closed_deals > 0 else 0
        st.markdown(f"""
            <div style='{metric_style.format(gradient="#f12711 0%, #f5af19 100%")}'>
                <div style='{label_style}'>Avg Deal Size</div>
                <div style='{metric_text_style}'>₹{int(avg_deal_size)}L</div>
                <div style='{sublabel_style}'>Per won deal</div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("""
        <div style='padding: 15px; background: linear-gradient(to right, #f8f9fa, #e9ecef); border-radius: 10px; margin: 15px 0;'>
            <h4 style='color: #2a5298; margin: 0; font-size: 1.1em; font-weight: 600;'>🔍 Filters</h4>
        </div>
    """, unsafe_allow_html=True)

    # Create a single row with all filters using adjusted column sizes
    col1, col2, col3, col4, col5, col6, col7, col8 = st.columns([1.2, 1.2, 1.2, 1, 1, 1, 1.2, 1.2])
    
    with col1:
        filters = {
            'selected_member': st.selectbox(
                "👤 Sales Owner",
                options=["All Team Members"] + team_members,
                key="team_member_filter"
            )
        }
    
    with col2:
        filters['search'] = st.text_input("🔍 Search", placeholder="Search...")
    
    with col3:
        if 'Practice' in df.columns:
            practices = sorted(df['Practice'].dropna().unique())
            selected_practices = st.multiselect(
                "🏢 Practice",
                options=practices,
                default=[],
                key="practice_filter"
            )
            filters['practices'] = selected_practices
        else:
            st.error("Practice column not found in the data")
            filters['practices'] = []
    
    with col4:
        fiscal_order = ['April', 'May', 'June', 'July', 'August', 'September', 
                       'October', 'November', 'December', 'January', 'February', 'March']
        available_months = df['Month'].dropna().unique().tolist()
        available_months.sort(key=lambda x: fiscal_order.index(x) if x in fiscal_order else len(fiscal_order))
        filters['month_filter'] = st.selectbox("📅 Month", options=["All Months"] + available_months)
    
    with col5:
        filters['quarter_filter'] = st.selectbox("📊 Quarter", options=["All Quarters", "Q1", "Q2", "Q3", "Q4"])
    
    with col6:
        filters['year_filter'] = st.selectbox("📅 Year", options=["All Years"] + sorted(df['Expected Close Date'].dt.year.unique().tolist()))
    
    with col7:
        probability_options = ["All Probability", "0-25%", "26-50%", "51-75%", "76-100%", "Custom Range"]
        filters['probability_filter'] = st.selectbox("📈 Probability", options=probability_options)
        if filters['probability_filter'] == "Custom Range":
            col7a, col7b = st.columns(2)
            with col7a:
                min_prob_input = st.text_input("Min %", value="0", key="custom_min_prob_input")
            with col7b:
                max_prob_input = st.text_input("Max %", value="100", key="custom_max_prob_input")
            try:
                min_prob = int(min_prob_input)
                max_prob = int(max_prob_input)
                filters['min_prob'] = min_prob
                filters['max_prob'] = max_prob
                filters['custom_prob_range'] = f"{min_prob}-{max_prob}%"
            except ValueError:
                filters['min_prob'] = 0
                filters['max_prob'] = 100
                filters['custom_prob_range'] = "0-100%"
    
    with col8:
        status_options = ["All Status", "Committed for the Month", "Upsides for the Month"]
        filters['status_filter'] = st.selectbox("🎯 Status", options=status_options)
        if filters['status_filter'] == "Committed for the Month":
            current_month = pd.Timestamp.now().strftime('%B')
            mask = (df['Month'] == current_month) & (df['Probability_Num'] > 75)
            filtered_df = df[mask]
        elif filters['status_filter'] == "Upsides for the Month":
            current_month = pd.Timestamp.now().strftime('%B')
            mask = (df['Month'] == current_month) & (df['Probability_Num'].between(25, 75))
            filtered_df = df[mask]
    
    with col8:
        filters['focus_filter'] = st.selectbox("🎯 Focus", options=["All Focus"] + sorted(df['KritiKal Focus Areas'].dropna().unique().tolist()))

    filtered_df = filter_dataframe(df, filters)
    
    st.markdown("""
        <div style='margin-bottom: 20px;'>
            <h3 style='color: #2a5298; margin: 0; font-size: 1.4em; font-weight: 600;'>Performance Metrics</h3>
        </div>
    """, unsafe_allow_html=True)

    m1, m2, m3 = st.columns(3)
    current_pipeline = filtered_df[~filtered_df['Is_Won']]['Amount_Lacs'].sum()
    weighted_projections = filtered_df[~filtered_df['Is_Won']]['Weighted_Amount'].sum()
    closed_won = filtered_df[filtered_df['Is_Won']]['Amount_Lacs'].sum()

    with m1:
        st.markdown(f"""
            <div style='
                background: linear-gradient(135deg, #4A90E2 0%, #357ABD 100%);
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                text-align: center;
                height: 100%;
            '>
                <div style='color: white; font-size: 1.1em; font-weight: 600; margin-bottom: 8px;'>
                    🌊 Current Pipeline
                </div>
                <div style='color: white; font-size: 1.8em; font-weight: 800;'>
                    ₹{int(current_pipeline)}L
                </div>
            </div>
        """, unsafe_allow_html=True)

    with m2:
        st.markdown(f"""
            <div style='
                background: linear-gradient(135deg, #6B5B95 0%, #846EA9 100%);
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                text-align: center;
            '>
                <div style='color: white; font-size: 1.1em; font-weight: 600; margin-bottom: 8px;'>
                    ⚖️ Weighted Projections
                </div>
                <div style='color: white; font-size: 1.8em; font-weight: 800;'>
                    ₹{int(weighted_projections)}L
                </div>
            </div>
        """, unsafe_allow_html=True)

    with m3:
        st.markdown(f"""
            <div style='
                background: linear-gradient(135deg, #2ECC71 0%, #27AE60 100%);
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                text-align: center;
            '>
                <div style='color: white; font-size: 1.1em; font-weight: 600; margin-bottom: 8px;'>
                    💰 Closed Won
                </div>
                <div style='color: white; font-size: 1.8em; font-weight: 800;'>
                    ₹{int(closed_won)}L
                </div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='margin: 25px 0;'></div>", unsafe_allow_html=True)

    # First show Detailed Opportunities
    st.markdown("""### Detailed Opportunities""", unsafe_allow_html=True)
    
    display_df = filtered_df[['Organization Name', 'Opportunity Name', 'Geography', 
                            'Expected Close Date', 'Probability', 'Amount', 
                            'Sales Owner', 'Pre-sales Technical Lead', 'Business Owner', 
                            'Type', 'KritiKal Focus Areas']].copy()
    
    display_df = display_df.rename(columns={
        'Amount': 'Amount (In Lacs)',
        'Pre-sales Technical Lead': 'Tech Owner',
        'Type': 'Hunting /farming'
    })
    
    display_df['Amount (In Lacs)'] = display_df['Amount (In Lacs)'].apply(lambda x: int(x/100000) if pd.notnull(x) else 0)
    display_df['Probability'] = display_df['Probability'].apply(format_percentage)
    display_df['Weighted Revenue (In Lacs)'] = display_df.apply(
        lambda row: int((row['Amount (In Lacs)']) * float(str(row['Probability']).rstrip('%'))/100) if pd.notnull(row['Amount (In Lacs)']) else 0, 
        axis=1
    )
    
    display_df['Expected Close Date'] = pd.to_datetime(display_df['Expected Close Date']).dt.strftime('%d-%b-%Y')
    display_df = display_df.sort_values('Amount (In Lacs)', ascending=False)
    
    display_df.index = range(1, len(display_df) + 1)
    display_df.index.name = 'S.No'
    
    st.dataframe(
        display_df,
        column_config={
            'Amount (In Lacs)': st.column_config.NumberColumn(
                'Amount (In Lacs)',
                format="₹%d L",
                help="Amount in Lakhs"
            ),
            'Weighted Revenue (In Lacs)': st.column_config.NumberColumn(
                'Weighted Revenue (In Lacs)',
                format="₹%d L",
                help="Weighted Revenue in Lakhs"
            ),
            'Probability': st.column_config.TextColumn(
                'Probability',
                help="Probability of winning the deal"
            ),
            'Expected Close Date': st.column_config.TextColumn(
                'Expected Close Date',
                help="Expected closing date"
            )
        }
    )

    st.markdown("<div style='margin: 25px 0;'></div>", unsafe_allow_html=True)

    # Then show Team Member Performance
    st.markdown(f"""
        <div style='
            background: linear-gradient(to right, #f8f9fa, #e9ecef);
            padding: 20px;
            border-radius: 15px;
            margin: 25px 0;
            box-shadow: 0 4px 8px rgba(0,0,0,0.05);
        '>
            <h3 style='
                color: #2a5298;
                margin: 0;
                font-size: 1.4em;
                font-weight: 600;
                font-family: "Segoe UI", sans-serif;
            '>Team Member Performance</h3>
        </div>
    """, unsafe_allow_html=True)
    
    # Calculate team metrics
    team_metrics = df.groupby('Sales Owner').agg({
        'Amount': lambda x: round(x[df['Sales Stage'].str.contains('Won', case=False, na=False)].sum() / 100000, 1),
        'Sales Stage': lambda x: x[df['Sales Stage'].str.contains('Won', case=False, na=False)].count()
    }).reset_index()
    team_metrics.columns = ['Sales Owner', 'Closed Won', 'Closed Deals']
    
    pipeline_df = df[~df['Sales Stage'].str.contains('Won', case=False, na=False)]
    total_pipeline = round(pipeline_df.groupby('Sales Owner')['Amount'].sum() / 100000, 1)
    team_metrics['Current Pipeline'] = team_metrics['Sales Owner'].map(total_pipeline)
    
    def calculate_weighted_projection(owner):
        owner_pipeline = pipeline_df[pipeline_df['Sales Owner'] == owner]
        weighted_sum = sum((amt * pr / 100) 
                           for amt, pr in zip(owner_pipeline['Amount'], owner_pipeline['Probability_Num']))
        return round(weighted_sum / 100000, 1)
    
    team_metrics['Weighted Projections'] = team_metrics['Sales Owner'].apply(calculate_weighted_projection)
    
    total_deals_owner = pipeline_df.groupby('Sales Owner').size()
    team_metrics['Pipeline Deals'] = team_metrics['Sales Owner'].map(total_deals_owner)
    team_metrics['Win Rate'] = round((team_metrics['Closed Deals'] / (team_metrics['Closed Deals'] + team_metrics['Pipeline Deals']) * 100), 1)
    team_metrics = team_metrics.sort_values('Current Pipeline', ascending=False)
    
    summary_data = team_metrics.copy()
    summary_data['Current Pipeline'] = summary_data['Current Pipeline'].apply(lambda x: f"₹{x:,}L")
    summary_data['Weighted Projections'] = summary_data['Weighted Projections'].apply(lambda x: f"₹{x:,}L")
    summary_data['Closed Won'] = summary_data['Closed Won'].apply(lambda x: f"₹{x:,}L")
    summary_data['Win Rate'] = summary_data['Win Rate'].apply(lambda x: f"{x}%")
    
    st.dataframe(
        summary_data[[
            'Sales Owner',
            'Current Pipeline',
            'Weighted Projections',
            'Closed Won',
            'Pipeline Deals',
            'Closed Deals',
            'Win Rate'
        ]],
        use_container_width=True
    )

def show_detailed():
    if st.session_state.df is None:
        st.warning("Please upload your sales data to view detailed information")
        return
    
    st.title("Detailed Sales Data")
    df = st.session_state.df
    search = st.text_input("Search", placeholder="Search in any field...")
    
    if search:
        mask = np.column_stack([df[col].astype(str).str.contains(search, case=False, na=False) 
                                for col in df.columns])
        df = df[mask.any(axis=1)]
    
    st.dataframe(df, use_container_width=True)

def show_ytd_dashboard():
    if 'df_current' not in st.session_state or 'df_previous' not in st.session_state:
        st.warning("Please upload data first.")
        return
    
    df_current = st.session_state.df_current
    df_previous = st.session_state.df_previous
    
    # Modern header with glassmorphism effect
    st.markdown("""
        <div style='
            background: linear-gradient(135deg, rgba(30, 60, 114, 0.95) 0%, rgba(42, 82, 152, 0.95) 100%);
            backdrop-filter: blur(8px);
            -webkit-backdrop-filter: blur(8px);
            padding: 2rem;
            border-radius: 20px;
            box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.15);
            border: 1px solid rgba(255, 255, 255, 0.18);
            margin-bottom: 2rem;
        '>
            <h1 style='
                color: white;
                margin: 0;
                text-align: center;
                font-size: 2.5rem;
                font-weight: 700;
                letter-spacing: 1px;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
            '>YTD Performance Dashboard</h1>
        </div>
    """, unsafe_allow_html=True)
    
    # Enhanced filters section with 6 columns
    st.markdown("### 🎯 Filters")
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    
    with col1:
        sales_owners = ["All"] + sorted(df_current['Sales Owner'].dropna().unique().tolist()) if 'Sales Owner' in df_current.columns else ["All"]
        selected_owner = st.selectbox("Sales Owner", sales_owners)
    
    with col2:
        practice_column = next((col for col in ['P&L Centre', 'Practice', 'Business Unit', 'Department'] 
                              if col in df_current.columns), None)
        if practice_column:
            practices = ["All"] + sorted(df_current[practice_column].dropna().unique().tolist())
            selected_practice = st.selectbox(practice_column, practices)
        else:
            selected_practice = "All"
            st.warning("Practice/P&L Centre column not found")
    
    with col3:
        types = ["All"] + sorted(df_current['Type'].dropna().unique().tolist()) if 'Type' in df_current.columns else ["All"]
        selected_type = st.selectbox("Type", types)
    
    with col4:
        status_column = next((col for col in ['Status', 'Sales Stage', 'Stage'] 
                            if col in df_current.columns), None)
        if status_column:
            statuses = ["All"] + sorted(df_current[status_column].dropna().unique().tolist())
            selected_status = st.selectbox(status_column, statuses)
        else:
            selected_status = "All"
            st.warning("Status column not found")
    
    with col5:
        geographies = ["All"] + sorted(df_current['Geography'].dropna().unique().tolist()) if 'Geography' in df_current.columns else ["All"]
        selected_geography = st.selectbox("Geography", geographies)
    
    with col6:
        years = ["All"]
        if 'Year' in df_current.columns:
            years.extend(sorted(df_current['Year'].dropna().unique().tolist()))
        elif 'Expected Close Date' in df_current.columns:
            df_current['Year'] = pd.to_datetime(df_current['Expected Close Date'], dayfirst=True).dt.year
            years.extend(sorted(df_current['Year'].dropna().unique().tolist()))
        selected_year = st.selectbox("Fiscal Year", years)
    
    # Filter data based on selections
    def filter_data(df):
        filtered_df = df.copy()
        
        if 'Sales Owner' in df.columns and selected_owner != "All":
            filtered_df = filtered_df[filtered_df['Sales Owner'] == selected_owner]
        
        if practice_column and selected_practice != "All":
            filtered_df = filtered_df[filtered_df[practice_column] == selected_practice]
        
        if 'Type' in df.columns and selected_type != "All":
            filtered_df = filtered_df[filtered_df['Type'] == selected_type]
        
        if status_column and selected_status != "All":
            filtered_df = filtered_df[filtered_df[status_column] == selected_status]
        
        if 'Geography' in df.columns and selected_geography != "All":
            filtered_df = filtered_df[filtered_df['Geography'] == selected_geography]
        
        if selected_year != "All":
            if 'Year' in df.columns:
                filtered_df = filtered_df[filtered_df['Year'] == selected_year]
            elif 'Expected Close Date' in df.columns:
                filtered_df = filtered_df[pd.to_datetime(filtered_df['Expected Close Date'], dayfirst=True).dt.year == selected_year]
            
        return filtered_df
    
    df_current_filtered = filter_data(df_current)
    df_previous_filtered = filter_data(df_previous)
    
    # Define metrics dictionary with enhanced styling and animations
    metrics = {
        'Total Pipeline': {
            'icon': '📈',
            'current': df_current_filtered['Amount'].sum() / 100000,
            'previous': df_previous_filtered['Amount'].sum() / 100000,
            'description': 'Total pipeline value across all stages',
            'gradient': 'linear-gradient(135deg, #3B82F6 0%, #1D4ED8 100%)',
            'trend_icon': '↗️' if (df_current_filtered['Amount'].sum() / 100000) > (df_previous_filtered['Amount'].sum() / 100000) else '↘️'
        },
        'Closed Won': {
            'icon': '🎯',
            'current': df_current_filtered[df_current_filtered[status_column].str.contains('Won', case=False, na=False)]['Amount'].sum() / 100000 if status_column else 0,
            'previous': df_previous_filtered[df_previous_filtered[status_column].str.contains('Won', case=False, na=False)]['Amount'].sum() / 100000 if status_column else 0,
            'description': 'Successfully closed deals',
            'gradient': 'linear-gradient(135deg, #10B981 0%, #059669 100%)',
            'trend_icon': '↗️' if (df_current_filtered[df_current_filtered[status_column].str.contains('Won', case=False, na=False)]['Amount'].sum() / 100000) > (df_previous_filtered[df_previous_filtered[status_column].str.contains('Won', case=False, na=False)]['Amount'].sum() / 100000) else '↘️' if status_column else '➖'
        },
        'Win Rate': {
            'icon': '🏆',
            'current': (len(df_current_filtered[df_current_filtered[status_column].str.contains('Won', case=False, na=False)]) / len(df_current_filtered) * 100) if status_column and len(df_current_filtered) > 0 else 0,
            'previous': (len(df_previous_filtered[df_previous_filtered[status_column].str.contains('Won', case=False, na=False)]) / len(df_previous_filtered) * 100) if status_column and len(df_previous_filtered) > 0 else 0,
            'description': 'Deal success rate',
            'gradient': 'linear-gradient(135deg, #8B5CF6 0%, #6D28D9 100%)',
            'trend_icon': '↗️' if ((len(df_current_filtered[df_current_filtered[status_column].str.contains('Won', case=False, na=False)]) / len(df_current_filtered) * 100) if status_column and len(df_current_filtered) > 0 else 0) > ((len(df_previous_filtered[df_previous_filtered[status_column].str.contains('Won', case=False, na=False)]) / len(df_previous_filtered) * 100) if status_column and len(df_previous_filtered) > 0 else 0) else '↘️'
        },
        'Average Deal Size': {
            'icon': '💰',
            'current': (df_current_filtered[df_current_filtered[status_column].str.contains('Won', case=False, na=False)]['Amount'].sum() / len(df_current_filtered[df_current_filtered[status_column].str.contains('Won', case=False, na=False)])) / 100000 if status_column and len(df_current_filtered[df_current_filtered[status_column].str.contains('Won', case=False, na=False)]) > 0 else 0,
            'previous': (df_previous_filtered[df_previous_filtered[status_column].str.contains('Won', case=False, na=False)]['Amount'].sum() / len(df_previous_filtered[df_previous_filtered[status_column].str.contains('Won', case=False, na=False)])) / 100000 if status_column and len(df_previous_filtered[df_previous_filtered[status_column].str.contains('Won', case=False, na=False)]) > 0 else 0,
            'description': 'Average value per won deal',
            'gradient': 'linear-gradient(135deg, #F59E0B 0%, #D97706 100%)',
            'trend_icon': '↗️' if ((df_current_filtered[df_current_filtered[status_column].str.contains('Won', case=False, na=False)]['Amount'].sum() / len(df_current_filtered[df_current_filtered[status_column].str.contains('Won', case=False, na=False)])) / 100000 if status_column and len(df_current_filtered[df_current_filtered[status_column].str.contains('Won', case=False, na=False)]) > 0 else 0) > ((df_previous_filtered[df_previous_filtered[status_column].str.contains('Won', case=False, na=False)]['Amount'].sum() / len(df_previous_filtered[df_previous_filtered[status_column].str.contains('Won', case=False, na=False)])) / 100000 if status_column and len(df_previous_filtered[df_previous_filtered[status_column].str.contains('Won', case=False, na=False)]) > 0 else 0) else '↘️'
        }
    }

    # Display metrics with modern design
    metric_cols = st.columns(len(metrics))
    for col, (metric_name, data) in zip(metric_cols, metrics.items()):
        with col:
            delta = data['current'] - data['previous']
            delta_color = "normal" if delta >= 0 else "inverse"
            st.metric(
                label=f"{data['icon']} {metric_name}",
                value=format_metric(data['current'], metric_name),
                delta=format_metric(abs(delta), metric_name),
                delta_color=delta_color
            )

    # Pipeline Analysis Section
    st.markdown("""
        <div style='margin-top: 2rem;'>
            <h2 style='color: #1a237e; font-weight: 600;'>Pipeline Analysis</h2>
        </div>
    """, unsafe_allow_html=True)

    # Pipeline Funnel
    stages = df_current_filtered['Sales Stage'].value_counts()
    fig_funnel = go.Figure(go.Funnel(
        y=stages.index,
        x=stages.values,
        textinfo="value+percent initial",
        textposition="inside",
        textfont=dict(size=16, color="white"),
        marker=dict(
            color=["#4CAF50", "#2196F3", "#9C27B0", "#FF9800", "#F44336"]
        )
    ))
    fig_funnel.update_layout(
        title="Pipeline Funnel Analysis",
        height=500,
        showlegend=False
    )
    st.plotly_chart(fig_funnel, use_container_width=True)

    # Performance Insights Section
    st.markdown("""
        <div style='margin-top: 2rem;'>
            <h2 style='color: #006064; font-weight: 600;'>Performance Insights</h2>
        </div>
    """, unsafe_allow_html=True)

    # Performance Trends
    trend_metrics = df_current_filtered.groupby(pd.Grouper(key='Expected Close Date', freq='M')).agg({
        'Amount': ['sum', 'count'],
        'Sales Stage': lambda x: (x.str.contains('Won', case=False, na=False)).sum()
    }).reset_index()
    trend_metrics.columns = ['Date', 'Total Amount', 'Deal Count', 'Won Deals']
    trend_metrics['Win Rate'] = trend_metrics['Won Deals'] / trend_metrics['Deal Count'] * 100
    trend_metrics['Average Deal Size'] = trend_metrics['Total Amount'] / trend_metrics['Deal Count']

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=trend_metrics['Date'],
        y=trend_metrics['Win Rate'],
        name='Win Rate',
        line=dict(color='#4CAF50', width=3),
        yaxis='y'
    ))
    fig.add_trace(go.Bar(
        x=trend_metrics['Date'],
        y=trend_metrics['Average Deal Size']/100000,
        name='Avg Deal Size (Lakhs)',
        marker_color='#2196F3',
        yaxis='y2'
    ))
    fig.update_layout(
        title='Win Rate vs Average Deal Size Trend',
        yaxis=dict(title='Win Rate (%)', side='left', showgrid=False),
        yaxis2=dict(title='Avg Deal Size (Lakhs)', side='right', overlaying='y', showgrid=False),
        height=500,
        hovermode='x unified'
    )
    st.plotly_chart(fig, use_container_width=True)

    # Competitive Analysis Section
    if 'Competitor' in df_current_filtered.columns:
        st.markdown("""
            <div style='margin-top: 2rem;'>
                <h2 style='color: #4a148c; font-weight: 600;'>Competitive Analysis</h2>
            </div>
        """, unsafe_allow_html=True)

        # Competitor Win/Loss Analysis
        competitor_analysis = df_current_filtered.groupby('Competitor').agg({
            'Amount': 'sum',
            'Sales Stage': lambda x: (x.str.contains('Won', case=False, na=False)).sum(),
            'Opportunity Name': 'count'
        }).reset_index()
        
        competitor_analysis.columns = ['Competitor', 'Total Amount', 'Won Deals', 'Total Deals']
        competitor_analysis['Win Rate'] = competitor_analysis['Won Deals'] / competitor_analysis['Total Deals'] * 100
        competitor_analysis['Loss Rate'] = 100 - competitor_analysis['Win Rate']
        
        col1, col2 = st.columns(2)
        with col1:
            fig_win = px.bar(
                competitor_analysis,
                x='Competitor',
                y=['Win Rate', 'Loss Rate'],
                title='Win/Loss Rate by Competitor',
                barmode='stack'
            )
            st.plotly_chart(fig_win, use_container_width=True)
        
        with col2:
            fig_amount = px.pie(
                competitor_analysis,
                values='Total Amount',
                names='Competitor',
                title='Pipeline Share by Competitor'
            )
            st.plotly_chart(fig_amount, use_container_width=True)

def format_metric(value, metric_type):
    """Helper function to format metric values"""
    if metric_type in ['Total Pipeline', 'Closed Won', 'Avg Deal Size']:
        return f"₹{abs(value):.0f}L"
    elif metric_type == 'Win Rate':
        return f"{abs(value):.1f}%"
    return f"{abs(value):.0f}"

def display_dashboard():
    if 'df_current' not in st.session_state or 'df_previous' not in st.session_state:
        st.warning("Please upload the data first!")
        return

    df_current = st.session_state.df_current
    df_previous = st.session_state.df_previous

    st.title("Sales Dashboard")

    col1, col2, col3 = st.columns([1, 1, 1])

    with col1:
        sales_owners = sorted(df_current['Sales Owner'].dropna().unique().tolist())
        selected_sales_owner = st.selectbox("Select Sales Owner", ["All Sales Owners"] + sales_owners)

    with col2:
        quarters = ['Q1', 'Q2', 'Q3', 'Q4']
        selected_quarter = st.selectbox("Select Quarter", ["All Quarters"] + quarters)

    with col3:
        practices = sorted(df_current['Practice'].dropna().unique().tolist())
        selected_practice = st.selectbox("Select Practice", ["All Practices"] + practices)

    if selected_sales_owner != "All Sales Owners":
        df_current = df_current[df_current['Sales Owner'] == selected_sales_owner]
        df_previous = df_previous[df_previous['Sales Owner'] == selected_sales_owner]

    if selected_quarter != "All Quarters":
        df_current = df_current[df_current['Quarter'] == selected_quarter]
        df_previous = df_previous[df_previous['Quarter'] == selected_quarter]

    if selected_practice != "All Practices":
        df_current = df_current[df_current['Practice'] == selected_practice]
        df_previous = df_previous[df_previous['Practice'] == selected_practice]

    committed_current_week = df_current[df_current['Status'] == "Committed for the Month"]['Amount'].sum()
    upside_current_week = df_current[df_current['Status'] == "Upside for the Month"]['Amount'].sum()
    closed_won_current_week = df_current[df_current['Status'] == "Closed Won"]['Amount'].sum()

    committed_previous_week = df_previous[df_previous['Status'] == "Committed for the Month"]['Amount'].sum()
    upside_previous_week = df_previous[df_previous['Status'] == "Upside for the Month"]['Amount'].sum()
    closed_won_previous_week = df_previous[df_previous['Status'] == "Closed Won"]['Amount'].sum()

    committed_delta = committed_current_week - committed_previous_week
    upside_delta = upside_current_week - upside_previous_week
    closed_won_delta = closed_won_current_week - closed_won_previous_week

    overall_committed_current_week = committed_current_week + closed_won_current_week
    overall_committed_previous_week = committed_previous_week + closed_won_previous_week
    overall_committed_delta = overall_committed_current_week - overall_committed_previous_week

    with st.container():
        st.markdown(f"""
            <div class="metric-container">
                <div class="card">
                    <div class="metric-label">Committed Data (Current Week)</div>
                    <div class="metric-value">₹{committed_current_week / 100000:.0f}L</div>
                    <div class="metric-label">Current Week Total</div>
                </div>
                <div class="card">
                    <div class="metric-label">Committed Data (Previous Week)</div>
                    <div class="metric-value">₹{committed_previous_week / 100000:.0f}L</div>
                    <div class="metric-label">Previous Week Total</div>
                </div>
                <div class="card">
                    <div class="metric-label">Delta</div>
                    <div class="metric-value {'delta-positive' if committed_delta > 0 else 'delta-negative'}">₹{committed_delta / 100000:.0f}L</div>
                    <div class="metric-label">Change</div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
            <div class="metric-container">
                <div class="card">
                    <div class="metric-label">Upside Data (Current Week)</div>
                    <div class="metric-value">₹{upside_current_week / 100000:.0f}L</div>
                    <div class="metric-label">Current Week Total</div>
                </div>
                <div class="card">
                    <div class="metric-label">Upside Data (Previous Week)</div>
                    <div class="metric-value">₹{upside_previous_week / 100000:.0f}L</div>
                    <div class="metric-label">Previous Week Total</div>
                </div>
                <div class="card">
                    <div class="metric-label">Delta</div>
                    <div class="metric-value {'delta-positive' if upside_delta > 0 else 'delta-negative'}">₹{upside_delta / 100000:.0f}L</div>
                    <div class="metric-label">Change</div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
            <div class="metric-container">
                <div class="card">
                    <div class="metric-label">Closed Won (Current Week)</div>
                    <div class="metric-value">₹{closed_won_current_week / 100000:.0f}L</div>
                    <div class="metric-label">Current Week Total</div>
                </div>
                <div class="card">
                    <div class="metric-label">Closed Won (Previous Week)</div>
                    <div class="metric-value">₹{closed_won_previous_week / 100000:.0f}L</div>
                    <div class="metric-label">Previous Week Total</div>
                </div>
                <div class="card">
                    <div class="metric-label">Delta</div>
                    <div class="metric-value {'delta-positive' if closed_won_delta > 0 else 'delta-negative'}">₹{closed_won_delta / 100000:.0f}L</div>
                    <div class="metric-label">Change</div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
            <div class="metric-container">
                <div class="card">
                    <div class="metric-label">Overall Committed Data (Current Week)</div>
                    <div class="metric-value">₹{overall_committed_current_week / 100000:.0f}L</div>
                    <div class="metric-label">Current Week Total</div>
                </div>
                <div class="card">
                    <div class="metric-label">Overall Committed Data (Previous Week)</div>
                    <div class="metric-value">₹{overall_committed_previous_week / 100000:.0f}L</div>
                    <div class="metric-label">Previous Week Total</div>
                </div>
                <div class="card">
                    <div class="metric-label">Delta</div>
                    <div class="metric-value {'delta-positive' if overall_committed_delta > 0 else 'delta-negative'}">₹{overall_committed_delta / 100000:.0f}L</div>
                    <div class="metric-label">Change</div>
                </div>
            </div>
        """, unsafe_allow_html=True)

def display_data_input():
    st.title("Data Input")
    st.write("Please upload your Excel file containing both current and previous week data in different sheets.")

    # Single file upload for Excel
    uploaded_file = st.file_uploader("Upload Excel File", type=['xlsx'], key='excel_file')

    if uploaded_file is not None:
        try:
            # Read the Excel file and get sheet names
            excel_file = pd.ExcelFile(uploaded_file)
            sheet_names = excel_file.sheet_names

            # Sheet selection for current week
            current_week_sheet = st.selectbox(
                "Select Current Week Sheet",
                options=sheet_names,
                key="current_week_sheet"
            )

            # Sheet selection for previous week
            previous_week_sheet = st.selectbox(
                "Select Previous Week Sheet",
                options=sheet_names,
                key="previous_week_sheet"
            )

            if current_week_sheet == previous_week_sheet:
                st.warning("Please select different sheets for current and previous week data.")
                return

            # Read the selected sheets
            df_current = pd.read_excel(uploaded_file, sheet_name=current_week_sheet)
            df_previous = pd.read_excel(uploaded_file, sheet_name=previous_week_sheet)

            # Store the dataframes in session state
            st.session_state.df_current = df_current
            st.session_state.df_previous = df_previous

            # Show success message
            st.success("Data uploaded successfully!")

            # Preview the data
            st.subheader("Current Week Data Preview")
            st.dataframe(df_current.head(), use_container_width=True)

            st.subheader("Previous Week Data Preview")
            st.dataframe(df_previous.head(), use_container_width=True)

        except Exception as e:
            st.error(f"Error reading the files: {str(e)}")
    else:
        st.info("Please upload both current and previous week data files to proceed.")

def show_pipeline_analysis():
    """Advanced Pipeline Analysis View"""
    if 'df_current' not in st.session_state:
        st.warning("Please upload data first.")
        return

    df = st.session_state.df_current.copy()
    
    # Convert Expected Close Date to datetime
    df['Expected Close Date'] = pd.to_datetime(df['Expected Close Date'], format='%d-%m-%Y', dayfirst=True)

    st.markdown("""
        <div style='
            background: linear-gradient(135deg, #1a237e 0%, #0d47a1 100%);
            padding: 2rem;
            border-radius: 20px;
            margin-bottom: 2rem;
            box-shadow: 0 8px 32px rgba(0,0,0,0.15);
        '>
            <h2 style='
                color: white;
                text-align: center;
                font-size: 2.2rem;
                font-weight: 700;
                margin: 0;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
            '>Pipeline Analysis</h2>
        </div>
    """, unsafe_allow_html=True)

    # Advanced Filters
    col1, col2, col3 = st.columns(3)
    with col1:
        probability_range = st.slider("Probability Range", 0, 100, (0, 100), 5)
    with col2:
        amount_range = st.slider("Deal Size (Lakhs)", 
                               int(df['Amount'].min()/100000), 
                               int(df['Amount'].max()/100000), 
                               (int(df['Amount'].min()/100000), int(df['Amount'].max()/100000)))
    with col3:
        timeline = st.selectbox("Timeline", ["Next Quarter", "Next 6 Months", "Next Year", "All"])

    # Filter data
    filtered_df = df.copy()
    filtered_df = filtered_df[
        (filtered_df['Probability'].between(probability_range[0], probability_range[1])) &
        (filtered_df['Amount'].between(amount_range[0]*100000, amount_range[1]*100000))
    ]

    # Pipeline Funnel
    stages = filtered_df['Sales Stage'].value_counts()
    fig_funnel = go.Figure(go.Funnel(
        y=stages.index,
        x=stages.values,
        textinfo="value+percent initial",
        textposition="inside",
        textfont=dict(size=16, color="white"),
        marker=dict(
            color=["#4CAF50", "#2196F3", "#9C27B0", "#FF9800", "#F44336"]
        )
    ))
    fig_funnel.update_layout(
        title="Pipeline Funnel Analysis",
        height=500,
        showlegend=False
    )
    st.plotly_chart(fig_funnel, use_container_width=True)

    # Probability Distribution
    col1, col2 = st.columns(2)
    with col1:
        prob_dist = filtered_df.groupby(pd.cut(filtered_df['Probability'], 
                                             bins=[0, 25, 50, 75, 100]))['Amount'].sum()/100000
        fig_prob = px.bar(
            x=["0-25%", "26-50%", "51-75%", "76-100%"],
            y=prob_dist.values,
            title="Pipeline by Probability",
            labels={"x": "Probability Range", "y": "Amount (Lakhs)"}
        )
        fig_prob.update_traces(marker_color='#2196F3')
        st.plotly_chart(fig_prob, use_container_width=True)

    with col2:
        # Group by month using datetime index
        monthly_data = filtered_df.set_index('Expected Close Date')
        timeline_dist = monthly_data.resample('ME')['Amount'].sum()/100000
        
        fig_timeline = px.line(
            x=timeline_dist.index,
            y=timeline_dist.values,
            title="Pipeline Timeline",
            labels={"x": "Month", "y": "Amount (Lakhs)"}
        )
        fig_timeline.update_traces(line_color='#4CAF50')
        st.plotly_chart(fig_timeline, use_container_width=True)

def show_performance_insights():
    """Advanced Performance Insights View"""
    if 'df_current' not in st.session_state:
        st.warning("Please upload data first.")
        return

    df = st.session_state.df_current.copy()
    
    # Convert Expected Close Date to datetime
    df['Expected Close Date'] = pd.to_datetime(df['Expected Close Date'], format='%d-%m-%Y', dayfirst=True)

    st.markdown("""
        <div style='
            background: linear-gradient(135deg, #006064 0%, #00838f 100%);
            padding: 2rem;
            border-radius: 20px;
            margin-bottom: 2rem;
            box-shadow: 0 8px 32px rgba(0,0,0,0.15);
        '>
            <h2 style='
                color: white;
                text-align: center;
                font-size: 2.2rem;
                font-weight: 700;
                margin: 0;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
            '>Performance Insights</h2>
        </div>
    """, unsafe_allow_html=True)

    # Performance Metrics
    col1, col2, col3, col4 = st.columns(4)
    metrics = {
        'Average Deal Size': df[df['Sales Stage'].str.contains('Won', case=False, na=False)]['Amount'].mean()/100000,
        'Win Rate': len(df[df['Sales Stage'].str.contains('Won', case=False, na=False)])/len(df)*100 if len(df) > 0 else 0,
        'Pipeline Coverage': df['Amount'].sum()/(st.session_state.sales_target*100000) if st.session_state.sales_target > 0 else 0,
        'Avg Sales Cycle': (pd.to_datetime(df[df['Sales Stage'].str.contains('Won', case=False, na=False)]['Expected Close Date']) - 
                           pd.to_datetime(df[df['Sales Stage'].str.contains('Won', case=False, na=False)]['Created Date'])).mean().days
                           if 'Created Date' in df.columns and len(df[df['Sales Stage'].str.contains('Won', case=False, na=False)]) > 0 else 0
    }

    for (metric, value), col in zip(metrics.items(), [col1, col2, col3, col4]):
        with col:
            st.markdown(f"""
                <div style='
                    background: white;
                    padding: 1.5rem;
                    border-radius: 15px;
                    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                    text-align: center;
                '>
                    <h3 style='
                        color: #333;
                        font-size: 1.1rem;
                        margin-bottom: 0.5rem;
                    '>{metric}</h3>
                    <p style='
                        color: #2196F3;
                        font-size: 1.8rem;
                        font-weight: 700;
                        margin: 0;
                    '>{value:.1f}{'L' if metric == 'Average Deal Size' else '%' if metric in ['Win Rate', 'Pipeline Coverage'] else ' days'}</p>
                </div>
            """, unsafe_allow_html=True)

    # Performance Trends
    st.markdown("### Performance Trends")
    
    # Set Expected Close Date as index and sort
    df_trend = df.set_index('Expected Close Date').sort_index()
    
    # Group by month using resample
    trend_metrics = df_trend.resample('ME').agg({
        'Amount': ['sum', 'count'],
        'Sales Stage': lambda x: (x.str.contains('Won', case=False, na=False)).sum()
    }).reset_index()
    
    # Flatten column names
    trend_metrics.columns = ['Date', 'Total Amount', 'Deal Count', 'Won Deals']
    
    # Calculate metrics
    trend_metrics['Win Rate'] = (trend_metrics['Won Deals'] / trend_metrics['Deal Count'] * 100).fillna(0)
    trend_metrics['Average Deal Size'] = (trend_metrics['Total Amount'] / trend_metrics['Deal Count']).fillna(0)

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=trend_metrics['Date'],
        y=trend_metrics['Win Rate'],
        name='Win Rate',
        line=dict(color='#4CAF50', width=3),
        yaxis='y'
    ))
    fig.add_trace(go.Bar(
        x=trend_metrics['Date'],
        y=trend_metrics['Average Deal Size']/100000,
        name='Avg Deal Size (Lakhs)',
        marker_color='#2196F3',
        yaxis='y2'
    ))
    fig.update_layout(
        title='Win Rate vs Average Deal Size Trend',
        yaxis=dict(title='Win Rate (%)', side='left', showgrid=False),
        yaxis2=dict(title='Avg Deal Size (Lakhs)', side='right', overlaying='y', showgrid=False),
        height=500,
        hovermode='x unified'
    )
    st.plotly_chart(fig, use_container_width=True)

def show_competitive_analysis():
    """Competitive Analysis View"""
    if 'df_current' not in st.session_state:
        st.warning("Please upload data first.")
        return

    df = st.session_state.df_current

    st.markdown("""
        <div style='
            background: linear-gradient(135deg, #4a148c 0%, #7b1fa2 100%);
            padding: 2rem;
            border-radius: 20px;
            margin-bottom: 2rem;
            box-shadow: 0 8px 32px rgba(0,0,0,0.15);
        '>
            <h2 style='
                color: white;
                text-align: center;
                font-size: 2.2rem;
                font-weight: 700;
                margin: 0;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
            '>Competitive Analysis</h2>
        </div>
    """, unsafe_allow_html=True)

    if 'Competitor' in df.columns:
        # Competitor Win/Loss Analysis
        competitor_analysis = df.groupby('Competitor').agg({
            'Amount': 'sum',
            'Sales Stage': lambda x: (x.str.contains('Won', case=False, na=False)).sum(),
            'Opportunity Name': 'count'
        }).reset_index()
        
        competitor_analysis.columns = ['Competitor', 'Total Amount', 'Won Deals', 'Total Deals']
        competitor_analysis['Win Rate'] = competitor_analysis['Won Deals'] / competitor_analysis['Total Deals'] * 100
        competitor_analysis['Loss Rate'] = 100 - competitor_analysis['Win Rate']
        
        # Competitive Landscape
        fig = px.scatter(
            competitor_analysis,
            x='Win Rate',
            y='Total Amount'/100000,
            size='Total Deals',
            color='Competitor',
            title='Competitive Landscape Analysis',
            labels={'Total Amount': 'Total Pipeline (Lakhs)'}
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Win/Loss Analysis
        col1, col2 = st.columns(2)
        with col1:
            fig_win = px.bar(
                competitor_analysis,
                x='Competitor',
                y=['Win Rate', 'Loss Rate'],
                title='Win/Loss Rate by Competitor',
                barmode='stack'
            )
            st.plotly_chart(fig_win, use_container_width=True)
        
        with col2:
            fig_amount = px.pie(
                competitor_analysis,
                values='Total Amount',
                names='Competitor',
                title='Pipeline Share by Competitor'
            )
            st.plotly_chart(fig_amount, use_container_width=True)
    else:
        st.info("Competitor information not available in the dataset")

def main():
    # Initialize session state for navigation if not exists
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "Data Input"

    # Sidebar navigation with new views
    st.sidebar.title("Navigation")
    
    # First check if data is uploaded
    if 'df_current' not in st.session_state or 'df_previous' not in st.session_state:
        st.session_state.current_page = "Data Input"
    else:
        st.session_state.current_page = st.sidebar.radio(
            "Select a page",
            ["Data Input", "Dashboard", "Overview", "Sales Team", "Pipeline Analysis", 
             "Performance Insights", "Competitive Analysis", "YTD Dashboard", "Detailed Data"]
        )

    # Display the selected page
    if st.session_state.current_page == "Data Input":
        display_data_input()
    elif st.session_state.current_page == "Dashboard":
        display_dashboard()
    elif st.session_state.current_page == "Overview":
        show_overview()
    elif st.session_state.current_page == "Sales Team":
        show_sales_team()
    elif st.session_state.current_page == "Pipeline Analysis":
        show_pipeline_analysis()
    elif st.session_state.current_page == "Performance Insights":
        show_performance_insights()
    elif st.session_state.current_page == "Competitive Analysis":
        show_competitive_analysis()
    elif st.session_state.current_page == "YTD Dashboard":
        show_ytd_dashboard()
    elif st.session_state.current_page == "Detailed Data":
        show_detailed()

if __name__ == "__main__":
    main()
