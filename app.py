import streamlit as st
import pandas as pd

# Title
st.set_page_config(page_title="Quarter Summary Dashboard", layout="wide")
st.title("📊 Quarter Summary Dashboard")

# Load data
@st.cache_data
def load_data():
    return pd.read_csv('data/sales_data.csv')

df = load_data()

# Sidebar to select quarter
quarters = df['Quarter'].unique()
selected_quarter = st.sidebar.selectbox("Select Quarter", quarters)

# Filter data by selected quarter
df_qtr = df[df['Quarter'] == selected_quarter]

# Get list of weeks and pick latest two
weeks = sorted(df_qtr['Week'].unique())
if len(weeks) < 2:
    st.warning("Not enough data for delta comparison.")
    st.stop()

current_week = weeks[-1]
previous_week = weeks[-2]

# Display selected weeks
st.markdown(f"**Current Week:** {current_week} &nbsp;&nbsp;&nbsp;&nbsp; **Previous Week:** {previous_week}")

# Filter for the two weeks
current_data = df_qtr[df_qtr['Week'] == current_week].groupby('Type')['Amount'].sum()
previous_data = df_qtr[df_qtr['Week'] == previous_week].groupby('Type')['Amount'].sum()

# Calculate delta
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
