import streamlit as st
import pandas as pd

st.set_page_config(page_title="Quarter Summary Dashboard", layout="wide")
st.title("📊 Quarter Summary Dashboard")

# Upload Excel file
uploaded_file = st.file_uploader("Upload Excel file with 'raw_data' and 'previousweek_raw_data' sheets", type=["xlsx"])

if uploaded_file:
    try:
        # Read both sheets
        current_df = pd.read_excel(uploaded_file, sheet_name="raw_data")
        previous_df = pd.read_excel(uploaded_file, sheet_name="previousweek_raw_data")

        required_cols = {"Week", "Quarter", "Type", "Amount"}

        if not required_cols.issubset(current_df.columns) or not required_cols.issubset(previous_df.columns):
            st.error(f"Sheets must contain the columns: {', '.join(required_cols)}")
            st.stop()

        # Show week info
        current_week = current_df['Week'].iloc[0]
        previous_week = previous_df['Week'].iloc[0]

        st.markdown(f"**Current Week:** {current_week} &nbsp;&nbsp;&nbsp;&nbsp; **Previous Week:** {previous_week}")

        # Group by Type
        current_data = current_df.groupby('Type')['Amount'].sum()
        previous_data = previous_df.groupby('Type')['Amount'].sum()
        delta_data = current_data.subtract(previous_data, fill_value=0)

        # Display metrics
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Committed")
            st.metric(
                label="Overall (Current Week)",
                value=f"₹{current_data.get('Committed', 0):,.0f}",
                delta=f"₹{delta_data.get('Committed', 0):,.0f}"
            )

        with col2:
            st.subheader("Upside")
            st.metric(
                label="Overall (Current Week)",
                value=f"₹{current_data.get('Upside', 0):,.0f}",
                delta=f"₹{delta_data.get('Upside', 0):,.0f}"
            )

    except Exception as e:
        st.error(f"An error occurred while processing the file: {e}")
else:
    st.info("📥 Please upload an Excel file with sheets: 'raw_data' and 'previousweek_raw_data'")
