# 🛍️ Inventory tracker 
Based on past sales data, this Streamlit app is designed to track inventory levels and provide alerts when stock is running low. Below is an overview of its functionality:

Key Features:
Current Inventory Display:

Displays the current inventory levels retrieved from a Google Sheets document.
Sales Projections:

Projects sales for the upcoming week based on sales data from the last 7 days.
Sales data is categorized into 3mg, 6mg, and 9mg product types.
Stock Alerts:

Generates alerts if any product type is running low, using stock projections for the next 7 days.
Alerts are color-coded to indicate urgency (red for urgent, yellow for warning, green for sufficient stock).
Past Sales Overview:

Displays the amount sold for each mg category over the past 7 days, along with projected sales for the next 7 days.
Data Sources:
Inventory Data: Pulled from a Google Sheets file.
Sales Data: Pulled from another Google Sheets file and used for generating stock alerts and projections.
How It Works:
Sales projections are based on the past 7 days' data and are adjusted by adding 10%.
Stock alerts are calculated by dividing current inventory levels by projected weekly sales, giving the estimated number of weeks remaining for each mg category.
If stock for a product is expected to last less than 2 weeks, an urgent alert is displayed.
This app is intended to assist with managing stock levels efficiently and proactively by forecasting demand based on recent sales trends.

