import streamlit as st
import pandas as pd

# Set page config
st.set_page_config(
    page_title="Sales Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

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

    # Check if 'Committed for the Month' exists in the data
    if 'Committed for the Month' in df_current.columns:
        committed_current_week = df_current['Committed for the Month'].sum()
    else:
        st.warning("'Committed for the Month' column not found in current week data")
        committed_current_week = 0

    if 'Committed for the Month' in df_previous.columns:
        committed_previous_week = df_previous['Committed for the Month'].sum()
    else:
        st.warning("'Committed for the Month' column not found in previous week data")
        committed_previous_week = 0

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

def main():
    page = st.sidebar.radio("Select Page", ["Data Input", "Dashboard"])

    if page == "Data Input":
        display_data_input()
    elif page == "Dashboard":
        display_dashboard()

if __name__ == "__main__":
    main()
