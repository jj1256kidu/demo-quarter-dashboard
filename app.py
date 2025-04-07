import streamlit as st
import pandas as pd

st.set_page_config(page_title="Commit Delta Tracker", layout="wide")
st.title("📊 Weekly Commit Comparison")

uploaded_file = st.file_uploader("📁 Upload Excel with 'Raw_Data' and 'PreviousWeek_Raw_Data'", type=["xlsx"])

if uploaded_file:
    try:
        # Load the sheets
        current_df = pd.read_excel(uploaded_file, sheet_name="Raw_Data")
        previous_df = pd.read_excel(uploaded_file, sheet_name="PreviousWeek_Raw_Data")

        # Filter only "Committed for the month"
        current_commit = current_df[current_df["Status"] == "Committed for the month"]
        previous_commit = previous_df[previous_df["Status"] == "Committed for the month"]

        # Group by Sales Owner and sum the Amount
        current_sum = current_commit.groupby("Sales Owner")["Amount"].sum().reset_index()
        current_sum.columns = ["Sales Owner", "Overall Committed (Current Week)"]

        previous_sum = previous_commit.groupby("Sales Owner")["Amount"].sum().reset_index()
        previous_sum.columns = ["Sales Owner", "Overall Committed (Previous Week)"]

        # Merge both
        combined = pd.merge(current_sum, previous_sum, on="Sales Owner", how="outer").fillna(0)

        # Calculate Delta
        combined["Delta"] = combined["Overall Committed (Current Week)"] - combined["Overall Committed (Previous Week)"]

        # Convert to Lakhs if needed
        combined[["Overall Committed (Current Week)", "Overall Committed (Previous Week)", "Delta"]] = \
            combined[["Overall Committed (Current Week)", "Overall Committed (Previous Week)", "Delta"]] / 100000
        combined = combined.round(2)

        # Show the result
        st.subheader("🔍 Commitment Comparison Table")
        st.dataframe(combined, use_container_width=True)

    except Exception as e:
        st.error(f"❌ Error: {e}")
else:
    st.info("Please upload the Excel file with both sheets.")
