import streamlit as st
import pandas as pd

# Set page config
st.set_page_config(
    page_title="Sales Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern design
st.markdown("""
    <style>
        .metric-container {
            display: flex;
            justify-content: center;
            flex-wrap: wrap;
            gap: 20px;
            margin-top: 30px;
        }
        .card {
            background: #2C3E50;
            padding: 15px 10px;
            border-radius: 10px;
            box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.15);
            text-align: center;
            flex: 0 0 250px;
            min-width: 200px;
            min-height: 150px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
        }
        .metric-label {
            font-size: 1em;
            color: #BDC3C7;
            margin-bottom: 5px;
        }
        .metric-value {
            font-size: 2.2em;
            color: #FFFFFF;
            font-weight: 800;
            line-height: 1.2;
        }
        .delta-positive {
            color: #2ECC71;
        }
        .delta-negative {
            color: #E74C3C;
        }

        @media (max-width: 768px) {
            .metric-container {
                flex-direction: column;
                align-items: center;
            }
        }
    </style>
""", unsafe_allow_html=True)
""", unsafe_allow_html=True)

# Function to display data input (upload and preview)
def display_data_input():
    st.title("Data Input")

    uploaded_file = st.file_uploader("Upload your Excel file", type=["xlsx"])

    if uploaded_file:
        excel_file = pd.ExcelFile(uploaded_file)
        sheet_names = excel_file.sheet_names
        st.write("Available Sheets:", sheet_names)

        selected_current_sheet = st.selectbox("Select Current Week Sheet", sheet_names, key="current_week")
        selected_previous_sheet = st.selectbox("Select Previous Week Sheet", sheet_names, key="previous_week")

        df_current = pd.read_excel(uploaded_file, sheet_name=selected_current_sheet)
        df_previous = pd.read_excel(uploaded_file, sheet_name=selected_previous_sheet)

        df_current.columns = df_current.columns.str.strip()
        df_previous.columns = df_previous.columns.str.strip()

        st.session_state.df_current = df_current
        st.session_state.df_previous = df_previous

        st.write(f"Current Week Data from {selected_current_sheet}:")
        st.dataframe(df_current.head())
        
        st.write(f"Previous Week Data from {selected_previous_sheet}:")
        st.dataframe(df_previous.head())

        return df_current, df_previous
    else:
        st.warning("Please upload a file to proceed.")
        return None, None

# Function to display the dashboard with metrics
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

def main():
    page = st.sidebar.radio("Select Page", ["Data Input", "Dashboard"])

    if page == "Data Input":
        display_data_input()
    elif page == "Dashboard":
        display_dashboard()

if __name__ == "__main__":
    main()
