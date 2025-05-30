"""This module contains the function to update the database from an Excel file."""

from datetime import datetime
import sqlite3
import pandas as pd


def month_name_to_int(month_name):
    """Convert a month name (e.g., 'Jan') to its corresponding integer (e.g., 1)."""
    try:
        return datetime.strptime(month_name, "%b").month  # Parse abbreviated month name
    except ValueError:
        return None  # Return None if the month name is invalid


def merge_start_date(row):
    """Merge 'Start Month' and 'Start Year' into 'Start Date'."""
    try:
        if row["Start Month"] == "-":
            return "2023-01-01"  # Default to January 1, 2023 if month is missing
        month_int = month_name_to_int(
            row["Start Month"]
        )  # Convert month name to integer
        return f"{int(row['Start Year'])}-{month_int:02d}-01"
    except (ValueError, TypeError, KeyError):
        return None


def merge_end_date(row):
    """Merge "End Month" and "End Year" into "End Date" (handle missing end dates)."""
    try:
        if row["End Month"] == "-":
            return None  # Default to None if month is missing
        month_int = month_name_to_int(row["End Month"])  # Convert month name to integer
        return f"{int(row['End Year'])}-{month_int:02d}-01"
    except (ValueError, TypeError, KeyError):
        return None


# pylint: disable=too-many-branches, too-many-locals
def update_database_from_excel(file_path, db_year):
    """
    Update the database with data from an Excel file.

    Args:
        file_path (str): Path to the Excel file.
        db_year (int): Year of the database to update.
    """
    # Connect to the database
    conn = sqlite3.connect(f"expenses_{db_year}.db")
    cursor = conn.cursor()

    # Read the Excel file
    excel_data = pd.ExcelFile(file_path)

    for sheet_name in excel_data.sheet_names:
        # Update the Recurring sheet into the recurring_expenses table
        if "Recurring" in sheet_name:
            recurring_data = pd.read_excel(excel_data, sheet_name="Recurring")

            # Remove the first row and use the new first row as the header
            recurring_data.columns = recurring_data.iloc[
                0
            ]  # Set the first row as header
            recurring_data = recurring_data[1:]

            recurring_data["start_date"] = recurring_data.apply(
                merge_start_date, axis=1
            )

            recurring_data["end_date"] = recurring_data.apply(merge_end_date, axis=1)

            # Insert data into the recurring_expenses table
            for _, row in recurring_data.iterrows():
                # Check if the record already exists
                cursor.execute(
                    """SELECT COUNT(*) FROM recurring_expenses WHERE
                    category = ? AND item = ? AND location = ?""",
                    (
                        row["Category"],
                        row["Item"],
                        row["Location"],
                    ),
                )
                if cursor.fetchone()[0] == 0:  # If the record does not exist
                    cursor.execute(
                        """INSERT OR REPLACE INTO recurring_expenses (
                            start_date, end_date, category, item, location, ori_price, currency, price_sgd
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                        (
                            row["start_date"],
                            row["end_date"],
                            row["Category"],
                            row["Item"],
                            row["Location"],
                            abs(int(row["Price"])),
                            "SGD",
                            abs(int(row["Price"])),
                        ),
                    )

        elif (
            "Summary" not in sheet_name
        ):  # Update the subsequent sheets (month names) into the expenses table
            month_data = pd.read_excel(excel_data, sheet_name=sheet_name, header=None)

            real_row_idx = 0

            for row_idx, row in month_data.iterrows():
                if pd.isna(row.iloc[1]):
                    real_row_idx = row_idx + 1
                    break

            new_month_data = month_data.iloc[real_row_idx:]
            new_month_data.columns = month_data.iloc[real_row_idx]  # Set the new header
            new_month_data = new_month_data.iloc[1:]

            for _, row in new_month_data.iterrows():
                # Check if the record already exists
                cursor.execute(
                    """SELECT COUNT(*) FROM expenses WHERE
                    category = ? AND item = ? AND location = ?""",
                    (
                        row["Category"],
                        row["Item"],
                        row["Location"],
                    ),
                )
                if cursor.fetchone()[0] == 0:  # If the record does not exist
                    if (
                        not (pd.isna(row["Remarks"]))
                        and row["Remarks"].split(" ")[0].isdigit()
                    ):
                        split_remarks = row["Remarks"].split(" ")
                        ori_price = abs(int(split_remarks[0]))
                        ori_currency = split_remarks[1]
                    else:
                        ori_price = row["Price"]
                        ori_currency = "SGD"
                    if pd.isna(row["Price"]):  # Handle missing price
                        fin_price = 0
                    else:
                        fin_price = abs(int(row["Price"]))
                    cursor.execute(
                        """INSERT OR REPLACE INTO expenses (
                                date, category, item, location, price, currency, price_sgd
                            ) VALUES (?, ?, ?, ?, ?, ?, ?)""",
                        (
                            row["Date"],
                            row["Category"],
                            row["Item"],
                            row["Location"],
                            ori_price,
                            ori_currency,
                            fin_price,
                        ),
                    )

    # Commit changes and close the connection
    conn.commit()
    conn.close()
