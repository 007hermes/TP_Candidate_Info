import streamlit as st
import pandas as pd
import plotly.express as px

# Load the dataset with proper date parsing
@st.cache_data
def load_data():
    try:
        # Load data
        tpci = pd.read_csv('TalkpushCI_data_fetch.csv')
        
        # Convert datetime with format specification
        tpci['INVITATIONDT'] = pd.to_datetime(tpci['INVITATIONDT'],
                                             format='%m/%d/%Y',  # Adjust this format if needed
                                             errors='coerce')  # Convert parsing errors to NaT
        
        # Handle/drop NaT values
        tpci = tpci.dropna(subset=['INVITATIONDT'])
        
        return tpci
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None

# Define colors
colors = ["#001E44", "#F5F5F5", "#E53855", "#B4BBBE", "#2F76B9", "#3B9790", "#F5BA2E", "#6A4C93", "#F77F00"]

# Common function to get data
def get_data(tpci, column, period):
    if period:
        start_date = tpci['INVITATIONDT'].max() - pd.DateOffset(days=period)
        tpci_filtered = tpci[tpci['INVITATIONDT'] >= start_date]
    else:
        tpci_filtered = tpci
    
    counts = tpci_filtered[column].value_counts().nlargest(10).reset_index()
    counts.columns = [column, 'COUNT']
    
    return counts

# Function to create graph
def create_graph(data, x_col, title):
    fig = px.bar(data, x=x_col, y='COUNT', 
                 title=title,
                 labels={x_col: x_col, 'COUNT': 'Count'},
                 color='COUNT', color_continuous_scale=[colors[4], colors[2]])
    fig.update_xaxes(title_text=x_col, tickangle=-45)
    fig.update_yaxes(title_text='Count')
    return fig

# Streamlit app
st.title('Talkpush CI Data Visualization')

# Load data
tpci = load_data()

if tpci is not None:
    # Display date range info
    st.write("Date range:", tpci['INVITATIONDT'].min().date(), "to", tpci['INVITATIONDT'].max().date())

    # Common dropdown for all graphs
    period_options = {
        'Daily (30 Days)': 30,
        'Weekly (12 Weeks)': 84,
        'Monthly (1 Year)': 365,
        'All Time': None
    }
    selected_period = st.selectbox('Select Time Period', list(period_options.keys()))

    # Get the selected period value
    period = period_options[selected_period]

    # Graph 1: Top 10 Campaign Title Counts
    campaign_data = get_data(tpci, 'CAMPAIGNTITLE', period)
    st.plotly_chart(create_graph(campaign_data, 'CAMPAIGNTITLE', f'Top 10 Campaign Titles ({selected_period})'))

    # Graph 2: Top 10 Source Counts
    source_data = get_data(tpci, 'SOURCE', period)
    st.plotly_chart(create_graph(source_data, 'SOURCE', f'Top 10 Sources ({selected_period})'))

    # Graph 3: Top 10 Assigned Manager Counts
    manager_data = get_data(tpci, 'ASSIGNEDMANAGER', period)
    st.plotly_chart(create_graph(manager_data, 'ASSIGNEDMANAGER', f'Top 10 Assigned Managers ({selected_period})'))
else:
    st.error("Failed to load data. Please check your CSV file and try again.")
