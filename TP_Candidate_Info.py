import streamlit as st
import pandas as pd
import plotly.express as px

# Load the dataset
@st.cache_data
def load_data():
    tpci = pd.read_csv('TalkpushCI_data_fetch.csv')
    tpci['INVITATIONDT'] = pd.to_datetime(tpci['INVITATIONDT'])
    return tpci

tpci = load_data()

# Sidebar filter
st.sidebar.header("Filters")
view_option = st.sidebar.selectbox("Select View", ["Daily", "Weekly", "Monthly", "All Time"], index=0)

def get_aggregated_data(tpci, freq, period):
    lead_counts = (
        tpci.groupby(tpci['INVITATIONDT'].dt.to_period(freq))
        .agg({'RECORDID': 'count'})
        .reset_index()
    )
    lead_counts['INVITATIONDT'] = lead_counts['INVITATIONDT'].astype(str)
    if period:
        lead_counts = lead_counts.iloc[-period:]
    return lead_counts

view_map = {"Daily": ("D", 30), "Weekly": ("W", 12), "Monthly": ("M", 12), "All Time": ("D", None)}
freq, period = view_map[view_option]

lead_counts = get_aggregated_data(tpci, freq, period)
st.subheader("Trend of Lead Counts Over Time")
fig1 = px.line(lead_counts, x='INVITATIONDT', y='RECORDID', title='Trend of Lead Counts', labels={'INVITATIONDT': 'Date', 'RECORDID': 'Lead Count'}, markers=True)
st.plotly_chart(fig1)

def get_top_counts(tpci, column, period):
    if period:
        start_date = tpci['INVITATIONDT'].max() - pd.DateOffset(days=period)
        tpci_filtered = tpci[tpci['INVITATIONDT'] >= start_date]
    else:
        tpci_filtered = tpci
    return tpci_filtered[column].value_counts().nlargest(10).reset_index()

st.subheader("Top 10 Campaign Titles")
campaign_counts = get_top_counts(tpci, 'CAMPAIGNTITLE', period)
campaign_counts.columns = ['Campaign Title', 'Count']
fig2 = px.bar(campaign_counts, x='Campaign Title', y='Count', title='Top 10 Campaign Titles')
st.plotly_chart(fig2)

st.subheader("Top 10 Sources")
source_counts = get_top_counts(tpci, 'SOURCE', period)
source_counts.columns = ['Source', 'Count']
fig3 = px.bar(source_counts, x='Source', y='Count', title='Top 10 Sources')
st.plotly_chart(fig3)

st.subheader("Top 10 Assigned Managers")
manager_counts = get_top_counts(tpci, 'ASSIGNEDMANAGER', period)
manager_counts.columns = ['Assigned Manager', 'Count']
fig4 = px.bar(manager_counts, x='Assigned Manager', y='Count', title='Top 10 Assigned Managers')
st.plotly_chart(fig4)

# Deploy using: `streamlit run script.py` and share via Streamlit Cloud
