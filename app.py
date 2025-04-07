import streamlit as st
import pandas as pd

st.set_page_config(page_title="Weekly Commit Delta", layout="wide")
st.title("📊 Weekly Commitment Comparison")

uploaded_file = st.file_uploader("📁 Upload Excel file", type=["xlsx"])

if uploaded_file:
    try:
        # Load the entire Excel file
        xls = pd.ExcelFile(uploaded_file)
        st.success("✅ Excel file loaded successfully!")

        # Let user select the correct sheets
        sheet_names = xls.sheet_names
        col1, col2 = st.columns(2)
        with col1:
            current_sheet = st.selectbox("Select Current Week Sheet", options=sheet_names, index=0)
        with col2:
            previous_sheet = st.selectbox("Select Previous Week Sheet", options=sheet_names, index=1 if len(sheet_names) > 1 else 0)

        # Load selected sheets
        current_df = pd.read_excel(xls, sheet_name=current_sheet)
        previous_df = pd.read_excel(xls, sheet_name=previous_sheet)

        # Preview both
        st.subheader("📄 Current Week Data")
        st.dataframe(current_df.head())
        st.subheader("📄 Previous Week Data")
        st.dataframe(previous_df.head())

        # Show unique statuses to help user
        st.markdown("### 🧩 Unique 'Status' Values")
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**{current_sheet}**", current_df["Status"].unique())
        with col2:
            st.write(f"**{previous_sheet}**", previous_df["Status"].unique())

        # Filter for "Committed for the month"
        current_commit = current_df[current_df["Status"] == "Committed for the month"]
        previous_commit = previous_df[previous_df["Status"] == "Committed for the month"]

        # Group and sum Amount
        current_sum = current_commit.groupby("Sales Owner")["Amount"].sum().reset_index()
        current_sum.columns = ["Sales Owner", "Overall Committed (Current Week)"]

        previous_sum = previous_commit.groupby("Sales Owner")["Amount"].sum().reset_index()
        previous_sum.columns = ["Sales Owner", "Overall Committed (Previous Week)"]

        # Merge and compute delta
        combined = pd.merge(current_sum, previous_sum, on="Sales Owner", how="outer").fillna(0)
        combined["Delta"] = combined["Overall Committed (Current Week)"] - combined["Overall Committed (Previous Week)"]

        # Convert to Lakhs
        for col in ["Overall Committed (Current Week)", "Overall Committed (Previous Week)", "Delta"]:
            combined[col] = (combined[col] / 100000).round(2)

        st.subheader("✅ Final Comparison Table")
        st.dataframe(combined, use_container_width=True)

    except Exception as e:
        st.error(f"❌ Error: {e}")

else:
    st.info("Upload an Excel file to begin.")
