import streamlit as st
import pandas as pd

# Set page config
st.set_page_config(
    page_title="Sales Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

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

    # Assuming the columns you want to show
    # Example: Total Commitment, Total Upside, Total Closed Won, etc.
    # You can modify these columns based on your data

    st.markdown("### 📝 Committed Data")
    committed_total_current_week = df['Committed for the Month (Current Week)'].sum()  # Example column name
    committed_total_previous_week = df['Committed for the Month (Previous Week)'].sum()  # Example column name
    committed_delta = committed_total_current_week - committed_total_previous_week

    # Display metrics for Committed Data
    st.write(f"**Committed Data (Current Week): ₹{committed_total_current_week / 100000:.0f} L**")
    st.write(f"**Committed Data (Previous Week): ₹{committed_total_previous_week / 100000:.0f} L**")
    st.write(f"**Delta: ₹{committed_delta / 100000:.0f} L**")

    # Repeat for Upside, Closed Won, and Overall Committed Data
    st.markdown("### 🔁 Upside Data")
    upside_total_current_week = df['Upside for the Month (Current Week)'].sum()  # Example column name
    upside_total_previous_week = df['Upside for the Month (Previous Week)'].sum()  # Example column name
    upside_delta = upside_total_current_week - upside_total_previous_week

    st.write(f"**Upside Data (Current Week): ₹{upside_total_current_week / 100000:.0f} L**")
    st.write(f"**Upside Data (Previous Week): ₹{upside_total_previous_week / 100000:.0f} L**")
    st.write(f"**Delta: ₹{upside_delta / 100000:.0f} L**")

    st.markdown("### ✅ Closed Won Data")
    closed_won_total_current_week = df['Closed Won (Current Week)'].sum()  # Example column name
    closed_won_total_previous_week = df['Closed Won (Previous Week)'].sum()  # Example column name
    closed_won_delta = closed_won_total_current_week - closed_won_total_previous_week

    st.write(f"**Closed Won Data (Current Week): ₹{closed_won_total_current_week / 100000:.0f} L**")
    st.write(f"**Closed Won Data (Previous Week): ₹{closed_won_total_previous_week / 100000:.0f} L**")
    st.write(f"**Delta: ₹{closed_won_delta / 100000:.0f} L**")

    st.markdown("### 📊 Overall Committed Data")
    overall_committed_current_week = committed_total_current_week + closed_won_total_current_week
    overall_committed_previous_week = committed_total_previous_week + closed_won_total_previous_week
    overall_committed_delta = overall_committed_current_week - overall_committed_previous_week

    st.write(f"**Overall Committed (Current Week): ₹{overall_committed_current_week / 100000:.0f} L**")
    st.write(f"**Overall Committed (Previous Week): ₹{overall_committed_previous_week / 100000:.0f} L**")
    st.write(f"**Delta: ₹{overall_committed_delta / 100000:.0f} L**")

# Main function to navigate between pages
def main():
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Select Page", ["Data Input", "Dashboard"])

    if page == "Data Input":
        df = display_data_input()
    else:
        display_dashboard(df)

if __name__ == "__main__":
    main()
