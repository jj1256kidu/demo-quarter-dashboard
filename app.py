import streamlit as st
import pandas as pd

st.set_page_config(page_title="Weekly Commitment Delta", layout="wide")

st.title("🗓️ Weekly Sales Commit Comparison")

uploaded_file = st.file_uploader("Upload Excel file with both Raw_Data & PreviousWeek_Raw_Data", type=["xlsx"])

if uploaded_file:
    try:
        raw_df = pd.read_excel(uploaded_file, sheet_name="Raw_Data")
        prev_df = pd.read_excel(uploaded_file, sheet_name="PreviousWeek_Raw_Data")

        # Filter only 'Committed for the month'
        current_week = raw_df[raw_df['Status'] == 'Committed for the month']
        previous_week = prev_df[prev_df['Status'] == 'Committed for the month']

        # Group and sum amounts by Sales Owner
        current_summary = current_week.groupby('Sales Owner')['Amount'].sum().reset_index().rename(columns={"Amount": "Current Week"})
        previous_summary = previous_week.groupby('Sales Owner')['Amount'].sum().reset_index().rename(columns={"Amount": "Previous Week"})

        # Merge both summaries
        comparison = pd.merge(current_summary, previous_summary, on='Sales Owner', how='outer').fillna(0)

        # Calculate delta
        comparison["Delta"] = comparison["Current Week"] - comparison["Previous Week"]

        # Format as Lakhs
        comparison["Current Week (₹L)"] = (comparison["Current Week"] / 100000).round(2)
        comparison["Previous Week (₹L)"] = (comparison["Previous Week"] / 100000).round(2)
        comparison["Delta (₹L)"] = (comparison["Delta"] / 100000).round(2)

        # Final display table
        display_df = comparison[["Sales Owner", "Current Week (₹L)", "Previous Week (₹L)", "Delta (₹L)"]]

        st.subheader("🔍 Commit Comparison by Sales Owner")
        st.dataframe(display_df, use_container_width=True)

    except Exception as e:
        st.error(f"⚠️ Error reading the file: {e}")
else:
    st.info("📁 Please upload a valid Excel file with both sheets: Raw_Data and PreviousWeek_Raw_Data.")
