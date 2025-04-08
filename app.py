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
            width: 20%;
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
        .table-container {
            margin-top: 20px;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        .table th {
            background-color: #2C3E50;
            color: white;
            font-weight: 700;
            padding: 10px;
        }
        .table td {
            text-align: center;
            padding: 10px;
            border: 1px solid #ddd;
        }
        .highlight-row {
            background-color: #fce8e6;
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

    # Filter the relevant columns and prepare the data for display
    df_current['Overall Committed (Current Week)'] = df_current['Committed for the Month'].fillna(0)
    df_previous['Overall Committed (Previous Week)'] = df_previous['Committed for the Month'].fillna(0)

    # Merging current and previous week data by "Sales Owner"
    merged_df = pd.merge(df_current[['Sales Owner', 'Overall Committed (Current Week)']], 
                         df_previous[['Sales Owner', 'Overall Committed (Previous Week)']], 
                         on="Sales Owner", how="outer")
    
    # Calculate Delta
    merged_df['Delta'] = merged_df['Overall Committed (Current Week)'] - merged_df['Overall Committed (Previous Week)']

    # Add a row for "Total"
    total_row = pd.DataFrame({
        'Sales Owner': ['Total'],
        'Overall Committed (Current Week)': [merged_df['Overall Committed (Current Week)'].sum()],
        'Overall Committed (Previous Week)': [merged_df['Overall Committed (Previous Week)'].sum()],
        'Delta': [merged_df['Delta'].sum()]
    })
    
    merged_df = pd.concat([merged_df, total_row], ignore_index=True)

    # Display KPI Cards
    st.markdown("""
        <div class="metric-container">
            <div class="card">
                <div class="metric-label">Committed Data (Current Week)</div>
                <div class="metric-value">₹{:.0f}L</div>
                <div class="metric-label">Current Week Total</div>
            </div>
            <div class="card">
                <div class="metric-label">Committed Data (Previous Week)</div>
                <div class="metric-value">₹{:.0f}L</div>
                <div class="metric-label">Previous Week Total</div>
            </div>
            <div class="card">
                <div class="metric-label">Delta</div>
                <div class="metric-value {'delta-positive' if committed_delta > 0 else 'delta-negative'}">₹{:.0f}L</div>
                <div class="metric-label">Change</div>
            </div>
        </div>
    """.format(
        merged_df['Overall Committed (Current Week)'].sum() / 100000,
        merged_df['Overall Committed (Previous Week)'].sum() / 100000,
        merged_df['Delta'].sum() / 100000
    ), unsafe_allow_html=True)

    # Display the data table with static rows
    st.subheader("Sales Owner Breakdown")
    st.markdown("<div class='table-container'>", unsafe_allow_html=True)
    st.dataframe(merged_df, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

def main():
    page = st.sidebar.radio("Select Page", ["Data Input", "Dashboard"])

    if page == "Data Input":
        display_data_input()
    elif page == "Dashboard":
        display_dashboard()

if __name__ == "__main__":
    main()
