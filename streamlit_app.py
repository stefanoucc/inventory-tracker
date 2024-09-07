"""
Functionalities needed

1. We are able to see the current inventory
2. We get alerts about running low on certain products. 
 

"""
import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime, timedelta

# Set the title and favicon that appear in the Browser's tab bar.
st.set_page_config(
    page_title="Inventory tracker",
    page_icon=":shopping_bags:",  # This is an emoji shortcode. Could be a URL too.
)

sheet_url = "https://docs.google.com/spreadsheets/d/1Hq3rTWvJvKEUmogU8NW-gTxIm97ySlqf4NRXn5tJCmM/export?format=csv"

# Read the Google Sheets data into a pandas DataFrame
df = pd.read_csv(sheet_url)

# -----------------------------------------------------------------------------
# Draw the actual page, starting with the inventory table.

st.title(":shopping_bags: Inventory tracker")

# Display the Google Sheets data as a table
st.subheader("Current Inventory from Google Sheets")
st.dataframe(df)

# -----------------------------------------------------------------------------
# Add Calendar for Projections

# Function to generate the current month's calendar
def get_month_calendar():
    today = datetime.today()
    start_date = today.replace(day=1)
    num_days = (today.replace(month=today.month % 12 + 1, day=1) - start_date).days
    
    # Create a DataFrame for the current month with dates
    calendar_df = pd.DataFrame({
        "Date": [start_date + timedelta(days=i) for i in range(num_days)],
        "Projection": [0] * num_days  # Initialize projections with 0
    })
    
    return calendar_df

# Load the calendar for the current month
calendar_df = get_month_calendar()

st.subheader("Edit Projections for the Current Month")

# Editable table for projections
edited_df = st.experimental_data_editor(calendar_df, num_rows="dynamic")

# Display the editable DataFrame
st.write("Current Projections", edited_df)

# -----------------------------------------------------------------------------
# Generate the Projections Graph

st.subheader("Projection Graph")

# Create a graph using Altair
projection_chart = alt.Chart(edited_df).mark_line().encode(
    x="Date:T",
    y="Projection:Q"
).properties(
    width=700,
    height=400
)

st.altair_chart(projection_chart, use_container_width=True)

# -----------------------------------------------------------------------------
# Save projections (optional, can be extended with database or file system)
st.button("Save Projections", type="primary")
