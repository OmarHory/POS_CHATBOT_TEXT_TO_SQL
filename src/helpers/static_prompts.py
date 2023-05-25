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


def demand_forecast_every_distribution_center_total():
    todays_date = pd.to_datetime(date.today())
    forecast_dates_list = []
    for i in range(0, 3 + 1):
        forecast_dates_list.append(
            get_wsd(todays_date.strftime("%Y-%m-%d")) + timedelta(weeks=i)
        )
    dirname = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    filename = os.path.join(dirname, "data/demand_gpt.csv")
    df = pd.read_csv(filename)
    df["week_start_date"] = pd.to_datetime(df["week_start_date"])
    df = df[df["week_start_date"].isin(forecast_dates_list)]
    df = df.groupby(["region"]).agg({"demand_quantity": "sum"}).reset_index()
    df = df.sort_values(by=["demand_quantity"])
    df = df.reset_index(drop=True)
    if not len(df):
        return "No data available, please contact your adminstrator."

    string_returned = ""
    for _, row in df.iterrows():
        DC_REGION = row["region"]
        FORECASTED_ORDERED_QUANTITIES = int(row["demand_quantity"])

        string_returned += f"\n\U0001F3E2 DC Region: _*{DC_REGION}*_\n\U0001F951 Forecasted Orders: _*{FORECASTED_ORDERED_QUANTITIES} Cases*_\n"

    return string_returned


def specific_size_total_demand_last_week():
    todays_date = pd.to_datetime(date.today())
    last_wsd = get_wsd(todays_date.strftime("%Y-%m-%d")) - timedelta(weeks=1)
    dirname = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    filename = os.path.join(dirname, "data/demand_gpt.csv")
    df = pd.read_csv(filename)
    df["week_start_date"] = pd.to_datetime(df["week_start_date"])
    df = df[df["week_start_date"] == last_wsd]
    df = (
        df.groupby(["week_start_date", "week_number", "year", "size"])
        .agg({"demand_quantity": "sum"})
        .reset_index()
    )
    df = df.sort_values(by=["week_start_date", "week_number", "year", "size"])
    df = df.reset_index(drop=True)
    if not len(df):
        return "No data available, please contact your adminstrator."

    string_returned = ""
    for _, row in df.iterrows():
        size = int(row["size"])
        quantity = int(row["demand_quantity"])
        string_returned += (
            f"\n\U0001F951 Size: *{size}*\n\U0001F4E6 Quantity: *{quantity} Cases*\n"
        )

    return string_returned


def specific_size_average_price_last_n_weeks(weeks=1):
    todays_date = pd.to_datetime(date.today())
    last_wsds = []
    for i in range(1, weeks + 1):
        last_wsds.append(get_wsd(todays_date.strftime("%Y-%m-%d")) - timedelta(weeks=i))
    dirname = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    filename = os.path.join(dirname, "data/pricing_supply_gpt.csv")
    df = pd.read_csv(filename)
    df["week_start_date"] = pd.to_datetime(df["week_start_date"])
    df = df[df["week_start_date"].isin(last_wsds)]
    df = df.groupby(["size"]).agg({"border_cost_mexico": "mean"}).reset_index()
    df = df.sort_values(by=["size"])
    df = df.reset_index(drop=True)
    if not len(df):
        return "No data available, please contact your adminstrator."

    string_returned = ""
    for _, row in df.iterrows():
        size = int(row["size"])
        price = round(row["border_cost_mexico"], 2)
        string_returned += (
            f"\n\U0001F951 Size: *{size}*\n\U0001F4B5 Price: *{price}$*\n"
        )

    return string_returned


def pricing_last_week_every_category():
    todays_date = pd.to_datetime(date.today())
    last_wsd = get_wsd(todays_date.strftime("%Y-%m-%d")) - timedelta(weeks=1)
    dirname = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    filename = os.path.join(dirname, "data/pricing_supply_gpt.csv")
    df = pd.read_csv(filename)
    df["week_start_date"] = pd.to_datetime(df["week_start_date"])
    df = df[df["week_start_date"] == last_wsd]
    df = (
        df.groupby(["week_start_date", "week_number", "year", "category"])
        .agg({"border_cost_mexico": "mean"})
        .reset_index()
    )
    df = df.sort_values(by=["week_start_date", "week_number", "year", "category"])
    df = df.reset_index(drop=True)
    if not len(df):
        return "No data available, please contact your adminstrator."

    string_returned = ""
    for _, row in df.iterrows():
        category = row["category"]
        if category == 0:
            category = "Organic"
        price = round(row["border_cost_mexico"], 2)
        string_returned += (
            f"\n\U0001F951 Category: *{category}*\n\U0001F4B5 Price: *{price}$*\n"
        )

    return string_returned


def pricing_forecast_every_category_4_weeks():
    todays_date = pd.to_datetime(date.today())
    forecast_dates_list = []
    for i in range(0, 3 + 1):
        forecast_dates_list.append(
            get_wsd(todays_date.strftime("%Y-%m-%d")) + timedelta(weeks=i)
        )
    dirname = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    filename = os.path.join(dirname, "data/pricing_supply_gpt.csv")
    df = pd.read_csv(filename)
    df["week_start_date"] = pd.to_datetime(df["week_start_date"])
    df = df[df["week_start_date"].isin(forecast_dates_list)]
    df = (
        df.groupby(["week_start_date", "week_number", "year", "category"])
        .agg({"border_cost_mexico": "mean"})
        .reset_index()
    )
    df = df.sort_values(by=["week_start_date", "week_number", "year", "category"])
    df = df.reset_index(drop=True)
    if not len(df):
        return "No data available, please contact your adminstrator."

    string_returned = ""
    for _, row in df.iterrows():
        week = row["week_number"]
        category = row["category"]
        if category == 0:
            category = "Organic"
        price = round(row["border_cost_mexico"], 2)
        string_returned += f"\n\U0001F4C5 Week *{week}*\n\U0001F951 Category: *{category}*\n\U0001F4B5 Price: *{price}$*\n"

    return string_returned


def supply_last_week_total_purchases_per_category():
    todays_date = pd.to_datetime(date.today())
    last_wsd = get_wsd(todays_date.strftime("%Y-%m-%d")) - timedelta(weeks=1)
    print("last_wsd", last_wsd)
    dirname = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    filename = os.path.join(dirname, "data/pricing_supply_gpt.csv")
    df = pd.read_csv(filename)
    df["week_start_date"] = pd.to_datetime(df["week_start_date"])
    df = df[df["week_start_date"] == last_wsd]
    df = df.sort_values(by=["week_start_date"])
    df = df.reset_index(drop=True)
    df = (
        df.groupby(["week_start_date", "category"])
        .agg({"harvested_quantity": "sum"})
        .reset_index()
    )
    if not len(df):
        return "No data available, please contact your adminstrator."

    string_returned = ""
    for _, row in df.iterrows():
        cat_cases = int(row["harvested_quantity"] / 11.3)
        category = int(row["category"])
        if category == 0:
            category = "Organic"
        string_returned += f"\n\U0001F951\n - Category {category}: *{row['harvested_quantity']}* KGs / *{cat_cases}* cases \n\n"

    # df = df.to_string(index=False)

    return string_returned


def specific_supply_overview():
    todays_date = pd.to_datetime(date.today())
    last_wsd = get_wsd(todays_date.strftime("%Y-%m-%d")) - timedelta(weeks=1)
    print("last_wsd", last_wsd)
    dirname = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    filename = os.path.join(dirname, "data/pricing_supply_gpt.csv")
    supply = pd.read_csv(filename)
    supply["week_start_date"] = pd.to_datetime(supply["week_start_date"])
    supply_chosen = supply[supply["week_start_date"] == last_wsd]
    supply_chosen = supply_chosen.sort_values(by=["week_start_date"])
    supply_chosen = supply_chosen.reset_index(drop=True)
    supply_chosen = (
        supply_chosen.groupby(["week_start_date", "size", "category"])
        .agg({"harvested_quantity": "sum"})
        .reset_index()
    )
    supply_chosen = supply_chosen[
        ["week_start_date", "size", "category", "harvested_quantity"]
    ]
    if not len(supply_chosen):
        return "No data available, please contact your adminstrator."

    string_returned = "\nLast week's purchases:\n "
    for _, row in supply_chosen.iterrows():
        size = int(row["size"])
        cat = int(row["category"])

        harvested_quantity_cases = int(row["harvested_quantity"] / 11.3)

        string_returned += f"\n\U0001F951 Size: *{size}* \n - Category {cat}: *{row['harvested_quantity']}* KGs / *{harvested_quantity_cases}* cases \n"

    next_week_wsd = get_wsd(todays_date.strftime("%Y-%m-%d")) + timedelta(weeks=1)
    print("last_wsd", next_week_wsd)
    supply_chosen = supply[supply["week_start_date"] == next_week_wsd]
    supply_chosen = supply_chosen.sort_values(by=["week_start_date"])
    supply_chosen = supply_chosen.reset_index(drop=True)
    supply_chosen = (
        supply_chosen.groupby(["week_start_date"])
        .agg(
            {
                "US_market_supply_quantity_from_california": "first",
                "US_market_supply_quantity_from_chile": "first",
                "US_market_supply_quantity_from_peru": "first",
                "US_market_supply_quantity_from_mexico": "first",
                "US_market_supply_quantity_from_colombia": "first",
            }
        )
        .reset_index()
    )
    if not len(supply_chosen):
        return "No data available, please contact your adminstrator."

    string_returned += "\nNext Week Hass Avocado Board Market Supply forecast: "

    region_season = []
    for col in [
        "US_market_supply_quantity_from_california",
        "US_market_supply_quantity_from_chile",
        "US_market_supply_quantity_from_peru",
        "US_market_supply_quantity_from_mexico",
        "US_market_supply_quantity_from_colombia",
    ]:
        if supply_chosen[col].squeeze() != 0:
            region_season.append(col.split("_")[-1].capitalize())

    for _, row in supply_chosen.iterrows():
        california = int(row["US_market_supply_quantity_from_california"])
        chile = int(row["US_market_supply_quantity_from_chile"])
        peru = int(row["US_market_supply_quantity_from_peru"])
        mexico = int(row["US_market_supply_quantity_from_mexico"])
        colombia = int(row["US_market_supply_quantity_from_colombia"])

        string_returned += f"\n\U0001F951\n - California: *{california} cases* \n - Chile: *{chile} cases* \n - Peru: *{peru} cases* \n - Mexico: *{mexico} cases* \n - Colombia: *{colombia} cases* \n"
    string_returned += f"\n\U0001F4CD Current region with the most market supply: *{tuple(region_season)}* \n"
    return string_returned


def mexico_weather_forecast_4_weeks():
    todays_date = pd.to_datetime(date.today())
    forecast_dates_list = []
    for i in range(0, 3 + 1):
        forecast_dates_list.append(
            get_wsd(todays_date.strftime("%Y-%m-%d")) + timedelta(weeks=i)
        )
    dirname = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    filename = os.path.join(dirname, "data/forecast_weather_all_locations.csv")
    df = pd.read_csv(filename)
    df = df[df.location == "Mexico"]
    df["week_start_date"] = pd.to_datetime(df["week_start_date"])
    df = df[df["week_start_date"].isin(forecast_dates_list)]
    df = df.sort_values(by=["week_start_date"])
    df = df.reset_index(drop=True)
    if not len(df):
        return "No data available, please contact your adminstrator."

    cols = df.select_dtypes(include=[float]).columns
    df[cols] = df[cols].round(1)
    string_returned = ""
    for _, row in df.iterrows():
        week = row["week_number"]
        min_F = int(row["Min_Temperature_In_C"] + 32)
        max_F = int(row["Max_Temperature_In_C"] + 32)
        mean_F = int(row["Mean_Temperature_In_C"] + 32)

        string_returned += f"\nWeek: {week}\n\U000026C5 Minimum Temperature: *{row['Min_Temperature_In_C']} C* / *{min_F} F*\n\U000026C5 Maximum Temperature: *{row['Max_Temperature_In_C']} C* / *{max_F} F*\n\U000026C5 Mean Temperature: *{row['Mean_Temperature_In_C']} C* / *{mean_F} F*\n"

    return string_returned
