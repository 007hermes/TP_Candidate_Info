import streamlit as st
import pandas as pd
import plotly.express as px

# Load the dataset
@st.cache_data
def load_data():
    tpci = pd.read_csv('TalkpushCI_data_fetch.csv')
    tpci['INVITATIONDT'] = pd.to_datetime(tpci['INVITATIONDT'], errors='coerce')
    return tpci.dropna(subset=['INVITATIONDT'])  # Drop invalid dates

tpci = load_data()

# Sidebar filters
st.sidebar.header("📊 Filters")
view_option = st.sidebar.selectbox("Select View", ["Daily", "Weekly", "Monthly", "All Time"], index=0)

# Function to aggregate data
def get_aggregated_data(tpci, freq, period):
    if tpci.empty:
        return pd.DataFrame(columns=['INVITATIONDT', 'RECORDID'])  # Return empty DataFrame
    
    lead_counts = (
        tpci.groupby(tpci['INVITATIONDT'].dt.floor(freq))
        .agg({'RECORDID': 'count'})
        .reset_index()
    )
    lead_counts['INVITATIONDT'] = lead_counts['INVITATIONDT'].astype(str)

    if period:
        lead_counts = lead_counts.iloc[-period:]
    
    return lead_counts

# Map view selection to frequency and period
view_map = {"Daily": ("D", 30), "Weekly": ("W", 12), "Monthly": ("M", 12), "All Time": ("D", None)}
freq, period = view_map[view_option]

# Generate lead counts
lead_counts = get_aggregated_data(tpci, freq, period)

# Display lead trends
st.subheader("📈 Lead Count Trends Over Time")
if lead_counts.empty:
    st.warning("No data available for the selected view.")
else:
    fig1 = px.line(
        lead_counts, x='INVITATIONDT', y='RECORDID',
        title=f'📊 Lead Count Trends ({view_option} View)',
        labels={'INVITATIONDT': 'Date', 'RECORDID': 'Lead Count'},
        markers=True
    )
    fig1.update_xaxes(title_text='Date', tickangle=-45)
    fig1.update_yaxes(title_text='Lead Count')
    st.plotly_chart(fig1)

# Function to get top counts for categorical columns
def get_top_counts(tpci, column, period):
    if tpci.empty or column not in tpci.columns:
        return pd.DataFrame(columns=[column, 'Count'])

    if period:
        start_date = tpci['INVITATIONDT'].max() - pd.DateOffset(days=period)
        tpci_filtered = tpci[tpci['INVITATIONDT'] >= start_date]
    else:
        tpci_filtered = tpci

    return tpci_filtered[column].value_counts().nlargest(10).reset_index()

# Generate and display top 10 campaign titles
st.subheader("🏆 Top 10 Campaign Titles")
campaign_counts = get_top_counts(tpci, 'CAMPAIGNTITLE', period)
if campaign_counts.empty:
    st.warning("No data available for campaign titles.")
else:
    campaign_counts.columns = ['Campaign Title', 'Count']
    fig2 = px.bar(campaign_counts, x='Campaign Title', y='Count', title='📢 Top 10 Campaign Titles')
    st.plotly_chart(fig2)

# Generate and display top 10 sources
st.subheader("🌍 Top 10 Sources")
source_counts = get_top_counts(tpci, 'SOURCE', period)
if source_counts.empty:
    st.warning("No data available for sources.")
else:
    source_counts.columns = ['Source', 'Count']
    fig3 = px.bar(source_counts, x='Source', y='Count', title='🔗 Top 10 Sources')
    st.plotly_chart(fig3)

# Generate and display top 10 assigned managers
st.subheader("👥 Top 10 Assigned Managers")
manager_counts = get_top_counts(tpci, 'ASSIGNEDMANAGER', period)
if manager_counts.empty:
    st.warning("No data available for assigned managers.")
else:
    manager_counts.columns = ['Assigned Manager', 'Count']
    fig4 = px.bar(manager_counts, x='Assigned Manager', y='Count', title='📌 Top 10 Assigned Managers')
    st.plotly_chart(fig4)

# Deployment: Run `streamlit run script.py` and share via Streamlit Cloud
