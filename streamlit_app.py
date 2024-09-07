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
# Weekly Projections (for the next 4 weeks)

def get_weekly_projections(weeks=4):
    """Generates a DataFrame with weeks and projection placeholders."""
    today = datetime.today()
    weeks_data = []
    
    for week in range(weeks):
        start_of_week = today + timedelta(days=week*7)
        end_of_week = start_of_week + timedelta(days=6)
        week_label = f"Week {week + 1} ({start_of_week.strftime('%b %d')} - {end_of_week.strftime('%b %d')})"
        weeks_data.append({"Week": week_label, "Projection": 0})  # Initialize projections with 0
    
    return pd.DataFrame(weeks_data)

# Load the weekly projections for the next 4 weeks
projections_df = get_weekly_projections(weeks=4)

st.subheader("Edit Sales Projections for the Next Few Weeks")

# Editable table for projections using st.data_editor
edited_df = st.data_editor(projections_df, num_rows="dynamic")

# Display the editable DataFrame
st.write("Current Projections", edited_df)

# -----------------------------------------------------------------------------
# Generate the Projections Graph

st.subheader("Projection Graph")

# Create a graph using Altair
projection_chart = alt.Chart(edited_df).mark_line().encode(
    x="Week:N",
    y="Projection:Q"
).properties(
    width=700,
    height=400
)

st.altair_chart(projection_chart, use_container_width=True)

# -----------------------------------------------------------------------------
# Save projections (optional, can be extended with database or file system)
st.button("Save Projections", type="primary")
