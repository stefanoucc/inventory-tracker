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

# Load the inventory data from the Google Sheets
inventory_url = "https://docs.google.com/spreadsheets/d/1Hq3rTWvJvKEUmogU8NW-gTxIm97ySlqf4NRXn5tJCmM/export?format=csv"
inventory_df = pd.read_csv(inventory_url)

# Load the sales data from the Google Sheets
sales_url = "https://docs.google.com/spreadsheets/d/1W_jm2sIkZiwrjHXL279VD_3nu2FyK6CUPtVyQepDQfo/export?format=csv"
sales_df = pd.read_csv(sales_url)

# -----------------------------------------------------------------------------
# Calculate projections based on last week's sales

# Convert the "Date" column in sales_df to datetime
sales_df['Date'] = pd.to_datetime(sales_df['Date'], format="%d/%m/%Y")

# Get the last date in the dataset and filter for the last 7 days
last_date = sales_df['Date'].max()
start_date = last_date - timedelta(days=7)
last_week_sales = sales_df[(sales_df['Date'] >= start_date) & (sales_df['Date'] <= last_date)]

# Function to extract mg from Product names (e.g., "Zyn Spearmint 3mg")
def extract_mg(product_name):
    if "3mg" in product_name:
        return "3mg"
    elif "6mg" in product_name:
        return "6mg"
    elif "9mg" in product_name:
        return "9mg"
    elif "1.5mg" in product_name:
        return "1.5mg"
    elif "11mg" in product_name:
        return "11mg"
    return None

# Add a column for mg type (3mg, 6mg, 9mg)
last_week_sales['mg'] = last_week_sales['Product'].apply(extract_mg)

# Calculate total sales for each mg category in the last week
weekly_sales = last_week_sales.groupby('mg')['Amount'].sum()

# Add 10% to each sales figure for the weekly projection
weekly_projections = weekly_sales * 1.10

# Calculate the projection date range (next seven days)
projection_start_date = last_date + timedelta(days=1)
projection_end_date = projection_start_date + timedelta(days=6)



st.subheader("Highlights: Stock Status")

# Get inventory counts for each mg category
total_1p5mg = inventory_df.loc[inventory_df['Current Inventory'] == 'Total 1.5mg', 'Total Mg'].values[0]
total_3mg = inventory_df.loc[inventory_df['Current Inventory'] == 'Total 3mg', 'Total Mg'].values[0]
total_6mg = inventory_df.loc[inventory_df['Current Inventory'] == 'Total 6mg', 'Total Mg'].values[0]
total_9mg = inventory_df.loc[inventory_df['Current Inventory'] == 'Total 9mg', 'Total Mg'].values[0]
total_11mg = inventory_df.loc[inventory_df['Current Inventory'] == 'Total 11mg', 'Total Mg'].values[0]

# Get projections for each mg category
projection_1p5mg = weekly_projections.get('1.5mg', 5)  # Default to 15 if no data available
projection_3mg = weekly_projections.get('3mg', 15)  # Default to 15 if no data available
projection_6mg = weekly_projections.get('6mg', 15)  # Default to 15 if no data available
projection_9mg = weekly_projections.get('9mg', 8)   # Default to 8 if no data available
projection_11mg = weekly_projections.get('11mg', 5)  # Default to 15 if no data available

# Calculate remaining weeks of stock
weeks_left_1p5mg = total_1p5mg / projection_1p5mg
weeks_left_3mg = total_3mg / projection_3mg
weeks_left_6mg = total_6mg / projection_6mg
weeks_left_9mg = total_9mg / projection_9mg
weeks_left_11mg = total_11mg / projection_11mg
# Display alerts based on the calculated weeks of stock
if weeks_left_3mg < 2:
    st.error(f"3mg: Alert, stock is running low, it is only enough for {weeks_left_3mg:.2f} weeks")
elif weeks_left_3mg < 3:
    st.warning(f"3mg: Stock is starting to run low, it is only enough for {weeks_left_3mg:.2f} weeks")
else:
    st.success(f"3mg: Stock is alright, enough for {weeks_left_3mg:.2f} weeks")

if weeks_left_6mg < 2:
    st.error(f"6mg: Alert, stock is running low, it is only enough for {weeks_left_6mg:.2f} weeks")
elif weeks_left_6mg < 3:
    st.warning(f"6mg: Stock is starting to run low, it is only enough for {weeks_left_6mg:.2f} weeks")
else:
    st.success(f"6mg: Stock is alright, enough for {weeks_left_6mg:.2f} weeks")

# Updated threshold logic for 9mg
if weeks_left_9mg < 2:
    st.error(f"9mg: Alert, stock is running low, it is only enough for {weeks_left_9mg:.2f} weeks")
elif weeks_left_9mg < 3:
    st.warning(f"9mg: Stock is starting to run low, it is only enough for {weeks_left_9mg:.2f} weeks")
else:
    st.success(f"9mg: Stock is alright, enough for {weeks_left_9mg:.2f} weeks")


# -----------------------------------------------------------------------------
# Display the "Past Sales" section as a table

st.subheader("Past Sales")

# Prepare the data for the table
past_sales_data = {
    "mg Category": ["3mg", "6mg", "9mg"],
    "Sold Last 7 Days": [
        weekly_sales.get('3mg', 0), 
        weekly_sales.get('6mg', 0), 
        weekly_sales.get('9mg', 0)
    ],
    "Projected Sales (Next 7 Days)": [
        weekly_projections.get('3mg', 0), 
        weekly_projections.get('6mg', 0), 
        weekly_projections.get('9mg', 0)
    ]
}

# Convert the data into a DataFrame for easy display
past_sales_df = pd.DataFrame(past_sales_data)

# Display the past sales data as a table
st.table(past_sales_df)
# -----------------------------------------------------------------------------
# Highlights / Alerts section based on stock levels
# -----------------------------------------------------------------------------
# Display the current inventory from Google Sheets
st.subheader("Current Inventory from Google Sheets")
st.dataframe(inventory_df)

# -----------------------------------------------------------------------------
# Display the sales data used for projections
st.subheader("Sales Data Used for Projections (Last 7 Days)")
st.dataframe(last_week_sales)
