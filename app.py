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

        # Ask the user to select a sheet
        selected_sheet = st.selectbox("Select a sheet", sheet_names)

        # Load the selected sheet into a DataFrame
        df = pd.read_excel(uploaded_file, sheet_name=selected_sheet)

        # Display the first few rows of the selected sheet for preview
        st.write(f"Data from {selected_sheet}:")
        st.dataframe(df.head())

        return df

# Function to display the dashboard with metrics
def display_dashboard(df):
    st.title("Sales Dashboard")

    if df is None:
        st.warning("Please upload your sales data first.")
        return

    # Committed for the Month Data
    st.markdown("### 📝 Committed Data")
    committed_current_week = df['Committed for the Month (Current Week)'].sum()  # Example column name
    committed_previous_week = df['Committed for the Month (Previous Week)'].sum()  # Example column name
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
    upside_current_week = df['Upside for the Month (Current Week)'].sum()  # Example column name
    upside_previous_week = df['Upside for the Month (Previous Week)'].sum()  # Example column name
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
    closed_won_current_week = df['Closed Won (Current Week)'].sum()  # Example column name
    closed_won_previous_week = df['Closed Won (Previous Week)'].sum()  # Example column name
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
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Select Page", ["Data Input", "Dashboard"])

    if page == "Data Input":
        df = display_data_input()
    else:
        display_dashboard(df)

if __name__ == "__main__":
    main()
