"""
Functionalities needed

1. We are able to see the current inventory
2. We get alerts about running low on certain products. 
    2.1 email alerts about low flavors/mgs 
3. Think about how to incorporate sales projections.     






"""






from collections import defaultdict
from pathlib import Path
import sqlite3

import streamlit as st
import altair as alt
import pandas as pd


# Set the title and favicon that appear in the Browser's tab bar.
st.set_page_config(
    page_title="Inventory tracker",
    page_icon=":shopping_bags:",  # This is an emoji shortcode. Could be a URL too.
)

# -----------------------------------------------------------------------------
# Declare some useful functions.

def connect_db():
    """Connects to the sqlite database."""
    DB_FILENAME = Path(__file__).parent / "inventory.db"
    db_already_exists = DB_FILENAME.exists()
    conn = sqlite3.connect(DB_FILENAME)
    db_was_just_created = not db_already_exists
    return conn, db_was_just_created


def initialize_data():
    """Initializes the inventory table with some data."""
    with sqlite3.connect(Path(__file__).parent / "inventory.db") as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS inventory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_name TEXT,
                price REAL,
                units_sold INTEGER,
                units_left INTEGER,
                cost_price REAL,
                reorder_point INTEGER,
                description TEXT
            )
            """
        )

        cursor.execute(
            """
            INSERT INTO inventory
                (item_name, price, units_sold, units_left, cost_price, reorder_point, description)
            VALUES
                ('Bottled Water (500ml)', 1.50, 115, 15, 0.80, 16, 'Hydrating bottled water'),
                ('Soda (355ml)', 2.00, 93, 8, 1.20, 10, 'Carbonated soft drink'),
                -- Add more items as needed
                ('Newspaper', 1.50, 22, 20, 1.00, 5, 'Daily newspaper')
            """
        )
        conn.commit()


def load_data():
    """Loads the inventory data from the database."""
    with sqlite3.connect(Path(__file__).parent / "inventory.db") as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT * FROM inventory")
            data = cursor.fetchall()
        except:
            return None

        df = pd.DataFrame(
            data,
            columns=[
                "id",
                "item_name",
                "price",
                "units_sold",
                "units_left",
                "cost_price",
                "reorder_point",
                "description",
            ],
        )

    return df


def update_data(df, changes):
    """Updates the inventory data in the database."""
    with sqlite3.connect(Path(__file__).parent / "inventory.db") as conn:
        cursor = conn.cursor()

        if changes["edited_rows"]:
            deltas = st.session_state.inventory_table["edited_rows"]
            rows = []

            for i, delta in deltas.items():
                row_dict = df.iloc[i].to_dict()
                row_dict.update(delta)
                rows.append(row_dict)

            cursor.executemany(
                """
                UPDATE inventory
                SET
                    item_name = :item_name,
                    price = :price,
                    units_sold = :units_sold,
                    units_left = :units_left,
                    cost_price = :cost_price,
                    reorder_point = :reorder_point,
                    description = :description
                WHERE id = :id
                """,
                rows,
            )

        if changes["added_rows"]:
            cursor.executemany(
                """
                INSERT INTO inventory
                    (id, item_name, price, units_sold, units_left, cost_price, reorder_point, description)
                VALUES
                    (:id, :item_name, :price, :units_sold, :units_left, :cost_price, :reorder_point, :description)
                """,
                (defaultdict(lambda: None, row) for row in changes["added_rows"]),
            )

        if changes["deleted_rows"]:
            cursor.executemany(
                "DELETE FROM inventory WHERE id = :id",
                ({"id": int(df.loc[i, "id"])} for i in changes["deleted_rows"]),
            )

        conn.commit()


# -----------------------------------------------------------------------------
# Draw the actual page, starting with the inventory table.

st.title(":shopping_bags: Inventory tracker")

st.info(
    """
    Use the table below to add, remove, and edit items.
    And don't forget to commit your changes when you're done.
    """
)

# Connect to database and create table if needed
conn, db_was_just_created = connect_db()

# Initialize data if the database was just created.
if db_was_just_created:
    initialize_data()
    st.toast("Database initialized with some sample data.")

# Load data from database
df = load_data()

# Display data with editable table
edited_df = st.data_editor(
    df,
    disabled=["id"],  # Don't allow editing the 'id' column.
    num_rows="dynamic",  # Allow appending/deleting rows.
    column_config={
        # Show dollar sign before price columns.
        "price": st.column_config.NumberColumn(format="$%.2f"),
        "cost_price": st.column_config.NumberColumn(format="$%.2f"),
    },
    key="inventory_table",
)

has_uncommitted_changes = any(len(v) for v in st.session_state.inventory_table.values())

st.button(
    "Commit changes",
    type="primary",
    disabled=not has_uncommitted_changes,
    on_click=update_data,
    args=(df, st.session_state.inventory_table),
)


# -----------------------------------------------------------------------------
# Now some cool charts

st.subheader("Units left", divider="red")

need_to_reorder = df[df["units_left"] < df["reorder_point"]].loc[:, "item_name"]

if len(need_to_reorder) > 0:
    items = "\n".join(f"* {name}" for name in need_to_reorder)
    st.error(f"We're running dangerously low on the items below:\n {items}")

st.altair_chart(
    alt.Chart(df)
    .mark_bar(
        orient="horizontal",
    )
    .encode(
        x="units_left",
        y="item_name",
    )
    + alt.Chart(df)
    .mark_point(
        shape="diamond",
        filled=True,
        size=50,
        color="salmon",
        opacity=1,
    )
    .encode(
        x="reorder_point",
        y="item_name",
    ),
    use_container_width=True,
)

st.caption("NOTE: The :diamonds: location shows the reorder point.")

st.subheader("Best sellers", divider="orange")

st.altair_chart(
    alt.Chart(df)
    .mark_bar(orient="horizontal")
    .encode(
        x="units_sold",
        y=alt.Y("item_name").sort("-x"),
    ),
    use_container_width=True,
)
