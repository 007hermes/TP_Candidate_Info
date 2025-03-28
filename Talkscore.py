import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.figure_factory as ff

# Load data
TPSC1 = pd.read_csv('TalkpushCI_SC1.csv')
TPSC1['INVITATIONDT_UTC'] = pd.to_datetime(TPSC1['INVITATIONDT_UTC'])
TPSC1 = TPSC1[TPSC1['TALKSCORE_OVERALL'] > 0]

# Dropdown options
options = {"Last 30 days": 30, "Last 12 Weeks": 84, "Last 1 Year": 365, "All Time": None}
selection = st.selectbox("Select Time Period", list(options.keys()))

# Filter data based on selection
if options[selection]:
    start_date = pd.Timestamp.today() - pd.Timedelta(days=options[selection])
    filtered_df = TPSC1[TPSC1['INVITATIONDT_UTC'] >= start_date]
else:
    filtered_df = TPSC1

# Define colors
colors = ["#001E44", "#F5F5F5", "#E53855", "#B4BBBE", "#2F76B9", "#3B9790", "#F5BA2E", "#6A4C93", "#F77F00"]

# Graph 1: Top 5 Rejection Reasons
st.subheader("Top 5 Rejection Reasons")
if 'REJECTED_REASON' in filtered_df.columns:
    rejection_counts = filtered_df['REJECTED_REASON'].value_counts().nlargest(5)
    fig1 = px.bar(x=rejection_counts.index, y=rejection_counts.values, 
                  labels={'x': 'Rejection Reason', 'y': 'Count'}, color=rejection_counts.index,
                  color_discrete_sequence=colors[:5])
    st.plotly_chart(fig1)
else:
    st.write("No rejection reasons available in the dataset.")

# Graph 2: Correlation Heatmap of Talkscore Variables
st.subheader("Correlation Heatmap of Talkscore Variables")
talkscore_vars = ['TALKSCORE_VOCAB', 'TALKSCORE_FLUENCY', 'TALKSCORE_GRAMMAR',
                  'TALKSCORE_COMPREHENSION', 'TALKSCORE_PRONUNCIATION', 'TALKSCORE_OVERALL']
if all(var in filtered_df.columns for var in talkscore_vars):
    corr_matrix = filtered_df[talkscore_vars].corr().round(2)
    fig2 = ff.create_annotated_heatmap(z=corr_matrix.values, x=talkscore_vars, y=talkscore_vars,
                                       annotation_text=corr_matrix.round(2).astype(str).values,
                                       colorscale='Blues', showscale=True)
    st.plotly_chart(fig2)
else:
    st.write("Talkscore variables not available in the dataset.")
