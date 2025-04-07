import streamlit as st
import pandas as pd

st.set_page_config(page_title="Quarter Summary Dashboard", layout="wide")
st.title("📊 Quarter Summary Dashboard")

# Upload Excel file
uploaded_file = st.file_uploader("Upload your Excel file", type=["xlsx"])

if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file)

        # Ensure required columns exist
        required_cols = {"Week", "Quarter", "Type", "Amount"}
        if not required_cols.issubset(df.columns):
            st.error(f"Your Excel file must contain the following columns: {', '.join(required_cols)}")
            st.stop()

        # Select quarter from sidebar
        quarters = df['Quarter'].unique()
        selected_quarter = st.sidebar.selectbox("Select Quarter", quarters)

        # Filter data for selected quarter
        df_qtr = df[df['Quarter'] == selected_quarter]

        # Get latest and previous week
        weeks = sorted(df_qtr['Week'].unique())
        if len(weeks) < 2:
            st.warning("Not enough data for delta comparison.")
            st.stop()

        current_week = weeks[-1]
        previous_week = weeks[-2]

        # Display selected weeks
        st.markdown(f"**Current Week:** {current_week} &nbsp;&nbsp;&nbsp;&nbsp; **Previous Week:** {previous_week}")

        # Aggregate data
        current_data = df_qtr[df_qtr['Week'] == current_week].groupby('Type')['Amount'].sum()
        previous_data = df_qtr[df_qtr['Week'] == previous_week].groupby('Type')['Amount'].sum()
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
    st.info("📥 Please upload an Excel file with columns: Week, Quarter, Type, Amount")
