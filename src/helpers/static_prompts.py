import pandas as pd
from datetime import date, timedelta
import os
from helpers.utils import *


def demand_last_week_every_distribution_center():
    todays_date = pd.to_datetime(date.today())
    last_wsd = get_wsd(todays_date.strftime("%Y-%m-%d")) - timedelta(weeks=1)
    dirname = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    filename = os.path.join(dirname, "data/demand_gpt.csv")
    df = pd.read_csv(filename)
    df["week_start_date"] = pd.to_datetime(df["week_start_date"])
    df = df[df["week_start_date"] == last_wsd]
    df = (
        df.groupby(["week_start_date", "week_number", "year", "region"])
        .agg(
            {
                "demand_quantity": "sum",
                "count_of_orders": "sum",
                "count_of_customers": "sum",
            }
        )
        .reset_index()
    )
    df = df.sort_values(by=["week_start_date", "week_number", "year"])
    df = df.reset_index(drop=True)
    if not len(df):
        return "No data available, please contact your adminstrator."

    string_returned = ""
    for _, row in df.iterrows():
        # DC = row['Distribution_Center']
        dc_region = row["region"]

        demand_quantity = int(row["demand_quantity"])
        count_of_orders = int(row["count_of_orders"])
        count_of_customers = int(row["count_of_customers"])

        string_returned += f"\n\U0001F3E2 Distribution Center Region: _*{dc_region}*_\n\U0001F951 Ordered Quantities: _*{demand_quantity} Cases*_\n\U0001F64B Count of Customers: _*{count_of_customers}*_\n\U0001F4E6 Count of Orders: _*{count_of_orders}*_\n"

    return string_returned