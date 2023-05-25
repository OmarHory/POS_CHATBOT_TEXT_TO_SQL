import pandas as pd
import os, sys
from datetime import date, timedelta

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(parent_dir)

from helpers.utils import get_wsd


def get_general_report():
    dirname = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    filename = os.path.join(dirname, "data/pricing_supply_gpt.csv")
    data = pd.read_csv(filename)
    data = data[data.historical_or_forecast == "historical"]

    last_4_weeks_border = (
        data.groupby(["week_start_date"])
        .agg(
            {
                "border_cost_mexico": "mean",
                "harvested_quantity": "sum",
            }
        )
        .reset_index()
        .sort_values("week_start_date")
        .iloc[-4:]
        .set_index(["week_start_date"])
    )

    filename = os.path.join(dirname, "data/demand_gpt.csv")
    data = pd.read_csv(filename)
    data = data[data.historical_or_forecast == "historical"]
    last_4_weeks_demand = (
        data.groupby(["week_start_date"])
        .agg(
            {
                "demand_quantity": "sum",
            }
        )
        .reset_index()
        .sort_values("week_start_date")
        .iloc[-4:]
        .set_index(["week_start_date"])
    )

    todays_wsd = get_wsd(date.today().strftime("%Y-%m-%d")) - timedelta(weeks=1)
    last_4_weeks_wsd = todays_wsd - timedelta(weeks=3)

    filename = os.path.join(dirname, "data/hab_data.csv")
    data = pd.read_csv(filename)
    data.week_start_date = pd.to_datetime(data.week_start_date)

    data = data[
        (data.week_start_date >= last_4_weeks_wsd)
        & (data.week_start_date <= todays_wsd)
    ]
    last_4_weeks_hab = (
        data.groupby(["week_start_date", "producing_region"])
        .agg(
            {
                "supply_quantity": "first",
            }
        )
        .reset_index()
        .sort_values("week_start_date")
        .set_index(["week_start_date"])
    )

    filename = os.path.join(dirname, "data/holidays.csv")
    data = pd.read_csv(filename)
    data.week_start_date = pd.to_datetime(data.week_start_date)

    data = data[
        (data.week_start_date >= last_4_weeks_wsd)
        & (data.week_start_date <= todays_wsd)
    ]
    last_4_weeks_holidays = (
        data.groupby(["week_start_date"])
        .agg(
            {
                "holiday_name": "first",
            }
        )
        .reset_index()
        .sort_values("week_start_date")
        .set_index(["week_start_date"])
    )

    last_4_weeks_border.index = pd.to_datetime(last_4_weeks_border.index)

    report = "In last 4 weeks we have the following observations:\n\n"

    col = "border_cost_mexico"
    report += f'\t\U0001F4B0 The {col.replace("_", " ").capitalize()} was {last_4_weeks_border.loc[:, col].round(2).values.tolist()} with an average of {last_4_weeks_border.loc[:, col].mean().squeeze().round(2)} USD.'

    report += "\n"

    col = "demand_quantity"
    report += f"\t\U0001F64B The Demand quantity was {last_4_weeks_demand.loc[:, col].astype(int).values.tolist()} with a total of {last_4_weeks_demand.loc[:, col].astype(int).sum()} cases.\n"

    col = "harvested_quantity"
    report += f"\t\U000026CF The Harvested quantity was {last_4_weeks_border.loc[:, col].astype(int).values.tolist()} with a total of {last_4_weeks_border.loc[:, col].astype(int).sum()} cases.\n"

    for region in last_4_weeks_hab.producing_region.unique():
        subset = last_4_weeks_hab[last_4_weeks_hab.producing_region == region]
        list_vals = subset.loc[:, "supply_quantity"].round(2).values.tolist()
        total_val = subset.loc[:, "supply_quantity"].sum().squeeze().round(2)
        report += f'\t\U0001F4E6 The Market Supply in {region.replace("_", " ").capitalize()} was {list_vals} with a total of {total_val} cases.'

        report += "\n"

    col = "holiday_name"
    report += f"\t\U0001F334 The Holidays were {last_4_weeks_holidays.loc[:, col].astype(str).values.tolist()}\n"

    print(report)

    return report
