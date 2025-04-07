import streamlit as st
import pandas as pd

# Set page config
st.set_page_config(
    page_title="Sales Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for a modern, sleek look
st.markdown("""
    <style>
        /* Main background styling */
        .main {
            background-color: #1E1E1E;
            color: white;
        }

        /* Header Styling */
        .header {
            font-size: 2.5em;
            font-weight: 700;
            color: #FFFFFF;
            margin-top: 20px;
            text-align: center;
        }

        /* Card styling for KPIs */
        .card {
            background: #2C3E50;
            padding: 20px;
            border-radius: 12px;
            box-shadow: 0px 10px 20px rgba(0, 0, 0, 0.2);
            text-align: center;
            margin: 15px;
        }

        /* Metric label inside the card */
        .metric-label {
            font-size: 1.2em;
            color: #BDC3C7;
            margin-bottom: 10px;
        }

        /* Metric value inside the card */
        .metric-value {
            font-size: 3.5em;
            color: #FFFFFF;
            font-weight: 800;
        }

        /* Delta text styling */
        .delta-positive {
            color: #2ECC71;
        }

        .delta-negative {
            color: #E74C3C;
        }

        /* Metric container for layout */
        .metric-container {
            display: flex;
            justify-content: space-evenly;
            margin-top: 40px;
        }

        .metric-container .card {
            flex: 1;
        }

        /* Info box styling */
        .info-box {
            background-color: rgba(74, 144, 226, 0.1);
            border-left: 4px solid #4A90E2;
            padding: 15px;
            border-radius: 4px;
            margin: 10px 0;
        }

        .data-table {
            background-color: #2C3E50;
            color: white;
            border-radius: 10px;
            padding: 15px;
        }
    </style>
""", unsafe_allow_html=True)

# Function to display the sheet selection and preview data
def display_data_input():
    st.title("Data Input")

    # Upload file widget
    uploaded_file = st.file_uploader("Upload your Excel file", type=["xlsx"])

    if uploaded_file:
        # Read the uploaded Excel file
        excel_file = pd.ExcelFile(uploaded_file)

        # Show all available sheet names
        sheet_names = excel_file.sheet_names
        st.write("Available Sheets:", sheet_names)

        # Ask the user to select a sheet for current week and previous week
        selected_current_sheet = st.selectbox("Select Current Week Sheet", sheet_names, key="current_week")
        selected_previous_sheet = st.selectbox("Select Previous Week Sheet", sheet_names, key="previous_week")

        # Load the selected sheets into DataFrames
        df_current = pd.read_excel(uploaded_file, sheet_name=selected_current_sheet)
        df_previous = pd.read_excel(uploaded_file, sheet_name=selected_previous_sheet)

        # Display the first few rows of the selected sheets for preview
        st.write(f"Current Week Data from {selected_current_sheet}:")
        st.dataframe(df_current.head())
        
        st.write(f"Previous Week Data from {selected_previous_sheet}:")
        st.dataframe(df_previous.head())

        return df_current, df_previous

# Function to display the dashboard with metrics
def display_dashboard(df_current, df_previous):
    st.title("Sales Dashboard")

    if df_current is None or df_previous is None:
        st.warning("Please upload your sales data first.")
        return

    # Committed for the Month Data
    st.markdown("### 📝 Committed Data")
    committed_current_week = df_current['Committed for the Month'].sum()  # Adjust column name based on your data
    committed_previous_week = df_previous['Committed for the Month'].sum()  # Adjust column name based on your data
    committed_delta = committed_current_week - committed_previous_week

    # Create KPI Card for Committed Data
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

    # Upside Data
    st.markdown("### 🔁 Upside Data")
    upside_current_week = df_current['Upside for the Month'].sum()  # Adjust column name based on your data
    upside_previous_week = df_previous['Upside for the Month'].sum()  # Adjust column name based on your data
    upside_delta = upside_current_week - upside_previous_week

    # Create KPI Card for Upside Data
    with st.container():
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

    # Closed Won Data
    st.markdown("### ✅ Closed Won Data")
    closed_won_current_week = df_current['Closed Won'].sum()  # Adjust column name based on your data
    closed_won_previous_week = df_previous['Closed Won'].sum()  # Adjust column name based on your data
    closed_won_delta = closed_won_current_week - closed_won_previous_week

    # Create KPI Card for Closed Won Data
    with st.container():
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

    # Overall Committed Data (Commit + Closed Won)
    st.markdown("### 📊 Overall Committed Data")
    overall_committed_current_week = committed_current_week + closed_won_current_week
    overall_committed_previous_week = committed_previous_week + closed_won_previous_week
    overall_committed_delta = overall_committed_current_week - overall_committed_previous_week

    # Create KPI Card for Overall Committed Data
    with st.container():
        st.markdown(f"""
            <div class="metric-container">
                <div class="card">
                    <div class="metric-label">Overall Committed (Current Week)</div>
                    <div class="metric-value">₹{overall_committed_current_week / 100000:.0f}L</div>
                    <div class="metric-label">Current Week Total</div>
                </div>
                <div class="card">
                    <div class="metric-label">Overall Committed (Previous Week)</div>
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
        df_current, df_previous = display_data_input()
    else:
        display_dashboard(df_current, df_previous)

if __name__ == "__main__":
    main()
