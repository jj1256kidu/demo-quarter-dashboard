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
        /* Add your CSS styling here for modern design */
        .metric-container {
            display: flex;
            justify-content: space-evenly;
            margin-top: 40px;
        }
        .card {
            background: #2C3E50;
            padding: 20px;
            border-radius: 12px;
            box-shadow: 0px 10px 20px rgba(0, 0, 0, 0.2);
            text-align: center;
            margin: 15px;
        }
        .metric-label {
            font-size: 1.2em;
            color: #BDC3C7;
            margin-bottom: 10px;
        }
        .metric-value {
            font-size: 3.5em;
            color: #FFFFFF;
            font-weight: 800;
        }
        .delta-positive {
            color: #2ECC71;
        }
        .delta-negative {
            color: #E74C3C;
        }
    </style>
""", unsafe_allow_html=True)

# Function to display data input (upload and preview)
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

        # Clean column names to remove extra spaces
        df_current.columns = df_current.columns.str.strip()
        df_previous.columns = df_previous.columns.str.strip()

        # Store the data in session state
        st.session_state.df_current = df_current
        st.session_state.df_previous = df_previous

        # Display the first few rows of the selected sheets for preview
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

    # Filter the data based on "Status" column to check for Committed and Upside data
    committed_current_week = df_current[df_current['Status'] == "Committed for the Month"]['Amount'].sum()
    upside_current_week = df_current[df_current['Status'] == "Upside for the Month"]['Amount'].sum()

    committed_previous_week = df_previous[df_previous['Status'] == "Committed for the Month"]['Amount'].sum()
    upside_previous_week = df_previous[df_previous['Status'] == "Upside for the Month"]['Amount'].sum()

    # Calculate deltas
    committed_delta = committed_current_week - committed_previous_week
    upside_delta = upside_current_week - upside_previous_week

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

def main():
    page = st.sidebar.radio("Select Page", ["Data Input", "Dashboard"])

    if page == "Data Input":
        display_data_input()
    elif page == "Dashboard":
        display_dashboard()

if __name__ == "__main__":
    main()
