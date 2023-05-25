from helpers.utils import get_wsd, get_wsd_string

for_more_info = "\n\nFor more information, you can check the FDM Analytics Portal on your desktop.\n\n\U0001F951 \U0001F951 \U0001F951"

list_of_approved_emails = ["o_hawary@hotmail.com", "omar@sitech.me"]


specific_menu = """\n1\u20E3 Last week average price for every size of avocado. 
        \n2\u20E3 Last 2 weeks average price for every size of avocado. 
        \n3\u20E3 Last 3 weeks average price for every size of avocado. 
        \n4\u20E3 Last 4 weeks average price for every size of avocado. 
        \n5\u20E3 Last week total demand for every size of avocado. 
        \n6\u20E3 Supply overview. 
        \n\U0001F6AA Type 'exit' if you want to go back to the main menu. 
        \n\U0001F5D2 If you do not wish to use the above list, feel free to ask any question of your choice \U0001F601"""

general_menu = """\n1\u20E3 Last week average price for every category of avocado. 
        \n2\u20E3 Last Week total Purchases per category.
        \n3\u20E3 Average weather forecast for the next 4 weeks in Mexico.
        \n4\u20E3 Forecasted average price for the next 4 weeks for every category of avocado. 
        \n5\u20E3 Last week total demand quantities for every Distribution Center Region.
        \n6\u20E3 Forecasted total demand quantities for every Distribution Center Region over the next 4 weeks.
        \n\U0001F4CC Type 'specific' if you want to go to a more specific menu.
        \n\U0001F5D2 If you do not wish to use the above list, feel free to ask any question of your choice \U0001F601"""


intent_prompt = """What is the intent of this sentence:

"{prompt}"

Work as an intent classifier that works for Delmonte fresh avocados producer and distributor. Classify the intent of the above prompt, return the output without formatting, just the intent.

Please choose one of the following intents, do not generate your own intents:
- Intent: Greeting 
        When the user says hello, hi, hello there, etc.

- Intent: Pricing of Avocado
        When the user intention is to know information about the avocado pricing or cost in USD at the border. Expect the user to ask about the supply, demand, weather, or holidays impact on pricing.

- Intent: Demand of Avocado 
        When the user intention is to know information about the customers demand for avocados, which is represented by ordered quantities in cases placed for the different Delmonte distribution centers and can be in total or per size and per category. Expect the user to ask about the pricing, supply, weather, or holidays impact on demand. Look for keywords 'Customer', 'demand' and 'distribution centers (DC)'.

- Intent: Supply of Avocado 
        When the user intention is to know information about the total supply of avocados exported to the US from different regions that grow avocados or the harvested quantities from Mexico orchards by Delmonte. Expect the user to ask about the pricing, demand, weather, or holidays impact on supply.

- Intent: Weather of US and Mexico
        When the user intention is to know information only about the weather without mentioning any information about anything else.

- Intent: Holidays and Events
        When the user intention is to know information about the holidays and/or events that can have direct or indirect impact on the avocados market without mentioning any information about anything else.

- Intent: Farewell 
        When the user says goodbye, have a good one, see ya, etc..

- Intent: Undefined 
        When the user says something that is not totally related to the above intents.

If the prompt has mix intents, choose the intent that has the higher weight."""


gpt_prompt = """{prompt}"""

def gpt_sql_prompt():
        import datetime
        from datetime import timedelta
        import pandas as pd

        today = datetime.date.today()
        current_wsd = pd.to_datetime(get_wsd(today.strftime("%Y-%m-%d")))
        current_woy = current_wsd.weekofyear
        current_year = current_wsd.year
        current_month = current_wsd.month
        current_month_name = current_wsd.month_name()

        
        next_wsd = (pd.to_datetime(current_wsd) + timedelta(weeks=1))
        next_woy = next_wsd.weekofyear
        next_year = next_wsd.year
        # next_month = next_wsd.month

        last_wsd = (pd.to_datetime(current_wsd) - timedelta(weeks=1))
        last_woy = last_wsd.weekofyear
        last_year = last_wsd.year
        # last_month = last_wsd.month

        date_string = get_wsd_string(current_wsd)
        print(date_string)


        #update
        current_wsd = current_wsd.strftime("%Y-%m-%d")
        next_wsd = next_wsd.strftime("%Y-%m-%d")
        last_wsd = last_wsd.strftime("%Y-%m-%d")

        prompt_temp = f"""
        1- Given an input question, first create a syntactically correct MySQL query to run based on the table schema, then look at the results of the query and return the answer based on the following instructions:  

        Your task is to answer questions related to predictive analytics of Del Monte avocados, one of the largest producers and distributors in the world. Avocados come in seven standard sizes, which are denoted by numbers such as 32, 36, 40, 48, 60, 70, and 84. The size of an avocado is determined by how many pieces can fit in a standard box. For example, a box of size 32 avocados contains 32 pieces. The smaller the avocado, the larger the size number. 
        There are three main avocado categories: Category "0" (Organic), Category "1" (Conventional one), and Category "2" (Conventional two). Not every size has all three categories.
        The "week start date" is the first date of an ISO week (Date data type, not String). The current week start date is {date_string}, which is ISO week ({current_woy}) of month ({current_month}) {current_month_name} and year ({current_year}), do not use CURDATE and CURRENT_DATE in the MySQL queries; use the provided current date instead ({current_wsd}). 
        When the question mentioned "expected, forecast or prediction" the question intents to know future or next week values, by default predict next week if a date is not specified.
        When querying a specific table, only ask for the relevant columns given the question, rather than all columns. Even if input question is provided in the instructions, write an SQL query for it.
        Note that border costs are in USD and quantities are in cases, which are equivalent to 11.3 kg. Use only the column names that are specified in the schema description and be careful not to query for columns that do not exist. It's also important to pay attention to which column is in which table.
        The holidays are for the US only, and they are the ones that impact the avocados market.
        There are no selling price of avocados in the data, only the border cost of avocados crossing the Mexico border. This is not the selling price used for the customer, but the cost of the avocados at the border.
        The location column is for the distribution centers (DC) are in the US only and are as the following, the input will not contain any other location, assume that the question will always mention a location from the following list, expect some misspellings and abbreviations:
        [Kansas City, Atlanta, Phoenix, Dallas, Portland, Seatte, Santa Fe Springs, Ft Lauderdale, Denver, Columbus, Greensboro, Boston Dc, Plant City, Jacksonville, Baltimore, Philadelphia, Toronto, FOB Border, Houston Tx]
        For the region of demand and weather, the input will not contain any other region, assume that the question will always mention a region from the following list, expect some misspellings and abbreviations:
        [Central, Mexico, Northeastern, Southeastern, Western] 
        Each distribution center is located at one of the regions, and each region has one or more distribution centers.
        There is no location for pricing, border cost, harvest and supply; Only for demand and weather.
        Include the selected primary keys in the GROUP BY clause of the query when required.
        If more than one table required in the question, do a join between the two tables.
        Use alias for the tables, and use the alias in the query in case of a join.
        Use the current "week start date" ({current_wsd}), current "week_number" ({current_woy}), current "month" ({current_month}), current "year" ({current_year}) question does not specify any of them.


        Examples:

        Example 1: What is the expected avg border cost in week {next_woy}?
        SELECT week_start_date, week_number, year, AVG(border_cost_mexico) FROM border_cost_pricing_gpt WHERE week_number = {next_woy} and year={next_year} and week_start_date = {next_wsd} GROUP BY week_number, year, week_start_date;

        Example 2: What is the average expected border cost?
        SELECT week_start_date, week_number, year, AVG(border_cost_mexico) FROM border_cost_pricing_gpt WHERE week_number = {current_woy} and year={current_year} and week_start_date = '{current_wsd}' GROUP BY week_number, year, week_start_date;

        Example 3: What is the expected demand? (if the user did not mention an aggregate function, then default to SUM)
        SELECT week_start_date, week_number, year, location, SUM(demand_quantity) FROM demand_gpt WHERE week_number = {current_woy} and year={current_year} and week_start_date = '{current_wsd}' GROUP BY week_number, year, week_start_date, location;

        Example 4: What is the expected demand in general? (in general means no specific date or week number is mentioned)
        SELECT week_start_date, week_number, year, location, SUM(demand_quantity) FROM demand_gpt WHERE week_number = {current_woy} and year={current_year} and week_start_date = '{current_wsd}'  GROUP BY week_number, year, week_start_date, location;

        Example 5: What is the forecasted demand per size and category? (forecasted means current week unless the user mentioned next week or more)
        SELECT week_start_date, week_number, year, size, category, SUM(demand_quantity) FROM demand_gpt WHERE Week_number = {current_woy} and year={current_year} and week_start_date = '{current_wsd}' GROUP BY size, category, week_number, year, week_start_date;

        Example 6: what is the border cost and demand for size 48?
        SELECT bp.week_start_date, bp.week_number, bp.year, bp.size, bp.category, AVG(bp.border_cost_mexico), SUM(demand.demand_quantity) FROM border_cost_pricing_gpt bp JOIN demand_gpt demand ON bp.week_start_date = demand.week_start_date AND bp.size = demand.size AND bp.category = demand.category WHERE bp.size = 48 and bp.week_number = {current_woy} and bp.year={current_year} and bp.week_start_date = '{current_wsd}' GROUP BY bp.week_number, bp.year, bp.size, bp.category, bp.week_start_date;

        Example 7: what is the harvest quantity for size 48 for week {last_woy}?
        SELECT week_start_date, week_number, category, year, SUM(harvested_quantity) FROM harvest_gpt WHERE size = 48 and week_start_date = '{last_wsd}' and week_number = {last_woy} and year={last_year} GROUP BY week_start_date, week_number, year, category

        Example 8: what is the border cost and harvest quantity for size 48 last week?
        SELECT bp.week_start_date, bp.week_number, bp.year, bp.category, bp.border_cost_mexico, SUM(harvested_quantity) FROM border_cost_pricing_gpt bp JOIN harvest_gpt harvest ON bp.week_start_date = harvest.week_start_date AND bp.size = harvest.size AND bp.category = harvest.category WHERE bp.size = 48 and bp.week_start_date = '{last_wsd}' and bp.week_number = {last_woy} and bp.year={last_year} GROUP BY bp.week_start_date, bp.week_number, bp.year, bp.border_cost_mexico, bp.category

        Example 9: What are all the demand forecasts for size 48 category 1?
        SELECT week_start_date, week_number, year, location, demand_quantity FROM demand_gpt WHERE size = 48 and category = 1 and week_number >={current_woy} and year={current_year} GROUP BY week_number, year, week_start_date;

        Example 10: What is the border cost forecast next week for size 48 category 1?
        SELECT week_start_date, week_number, year, AVG(border_cost_mexico) FROM border_cost_pricing_gpt WHERE size = 48 and category = 1 and week_number ={next_woy} and year={next_year} and week_start_date={next_wsd} GROUP BY week_number, year, week_start_date;

        Example 11: What is the weather in central region?
        SELECT week_start_date, week_number, year, location, region, Min_Temperature_In_C, Max_Temperature_In_C, Mean_Temperature_In_C FROM weather_gpt WHERE region = 'Central' and week_start_date = '{current_wsd}' and week_number = {current_woy} and year={current_year} GROUP BY week_number, year, week_start_date;

        Example 12: What is the demand in western region? 
        SELECT week_start_date, week_number, year, location, region, SUM(demand_quantity) FROM demand_gpt WHERE region = 'Western' and week_start_date = '{current_wsd}' and week_number = {current_woy} and year={current_year} GROUP BY week_number, year, location, week_start_date;

        Example 13: What is the difference in demand next week for size 60 category 1 and size 48 category 1?
        SELECT week_start_date, week_number, year,  size, category, SUM(demand_quantity) FROM demand_gpt WHERE ((size = 60 and category = 1) OR (size = 48 and category = 1)) and week_start_date = '{current_wsd}' and week_number = {next_woy} and year={next_year} GROUP BY size, category, week_number, year, week_start_date;
        
        Example 14: What is the expected demand in week {next_woy}?
        SELECT week_start_date, week_number, year, SUM(demand_quantity) FROM demand_gpt WHERE week_number = {next_woy} and year={next_year} and week_start_date = '{next_wsd}' GROUP BY week_number, year, week_start_date;

        Example 15: How many shipped orders for {last_wsd}?
        SELECT COUNT(*) FROM demand_customers_gpt WHERE order_status = 'S' AND week_start_date = '{last_wsd}';

        Example 16: How many shipped orders and their quantities for {last_wsd}?
        SELECT COUNT(*), SUM(demand_quantity) FROM demand_customers_gpt WHERE order_status = 'S' AND week_start_date = '{last_wsd}' GROUP BY week_start_date;

        Example 17: Compare the shipped orders year over year?
        SELECT year, COUNT(*) FROM demand_customers_gpt WHERE order_status = 'S' GROUP BY year;

        Example 18: Which demand customer has disappeared from denver dc from july 2022?
        SELECT DISTINCT customer_name FROM demand_customers_gpt WHERE location = 'Denver' AND year = 2022 AND month <7 AND customer_name NOT IN (SELECT DISTINCT customer_name FROM demand_customers_gpt WHERE location = 'Denver' AND year<2022)


        2- Tables Schemas and description:

        - "border_cost_pricing_gpt": border cost of avocados crossing the Mexico border. This is not the cost sold to the customer, but the cost of the avocados at the border.
                - week_start_date:first date of an ISO week, border cost calculation date. (Primary Key)
                - size: avocado size. (Primary Key)
                - category: avocado category. (Primary Key)
                - week_number: ISO week number. (Primary Key)
                - month: month. (Primary Key)
                - year: year. (Primary Key)
                - border_cost_mexico: border cost in USD.

        - "holiday_gpt": holidays that impact the avocados market either by increasing or decreasing the demand, pricing.
                - week_start_date:first date of an ISO week, holiday date. (Primary Key)
                - week_number: ISO week number. (Primary Key)
                - month: month. (Primary Key)
                - year: year. (Primary Key)
                - holiday_name: holiday name that impacts avocado market.

        - "weather_gpt": weather and temperatures.
                - week_start_date:first date of an ISO week, weather measurement date. (Primary Key)
                - week_number: ISO week number. (Primary Key)
                - month: month. (Primary Key)
                - year: year. (Primary Key)
                - location: location of the weather. (Primary Key)
                - region: region of the location that the weather is being measured at. (Primary Key)
                - Min_Temperature_In_C: minimum temperature in Celsius.
                - Max_Temperature_In_C: maximum temperature in Celsius.
                - Mean_Temperature_In_C: mean temperature in Celsius.

        - "harvest_gpt": harvested quantities from Mexico orchards by Delmonte.
                - week_start_date:first date of an ISO week, harvest date. (Primary Key)
                - week_number: ISO week number. (Primary Key)
                - month: month. (Primary Key)
                - year: year. (Primary Key)
                - size: avocado size. (Primary Key)
                - category: avocado category. (Primary Key)
                - harvested_quantity: harvested quantity from orchards in Mexico in cases.

        - "demand_gpt": demand of avocados in the US (without customers, with historicals and forecasts starting from current date {current_wsd}) from different distribution centers. Use this table when the user is not interested in the customer level data.
                - week_start_date:first date of an ISO week, shipment date. (Primary Key)
                - week_number: ISO week number. (Primary Key)
                - month: month. (Primary Key)
                - year: year. (Primary Key)
                - size: avocado size. (Primary Key)
                - category: avocado category. (Primary Key)
                - location: location of the demand distribution center. (Primary Key)
                - region: region of the location. (Primary Key)
                - demand_quantity: demand quantity in cases.

        - "demand_customers_gpt": Status table for demand of avocados in the US (with customers, with historicals and without forecasts. The last date for data is {last_wsd}, query this date by default unless specified) from different distribution centers. Use this table when the user is interested in the customer level data.
                - week_start_date: first date of an ISO week, shipment date. (Primary Key)
                - week_number: ISO week number. (Primary Key)
                - month: month. (Primary Key)
                - year: year. (Primary Key)
                - size: avocado size. (Primary Key)
                - category: avocado category. (Primary Key)
                - customer_name: customer name. (Primary Key)
                - order_status: order status. (S: Shipped Order, V: Cancelled order) (Primary Key)
                - location: location of the demand distribution center. (Primary Key)
                - region: region of the location. (Primary Key)
                - demand_quantity: demand quantity in cases per customer.
                - planned_order_count: number of orders that are planned, a planned order is an order that was confirmed by the customer more than a week of the shipment date. 
                - instant_order_count: number of orders that are instant (unplanned), an instant order is an order that was confirmed by the customer less than a week of the shipment date.
                - total_order_count: number of orders that are placed (planned + instant).

        - "supply_market_gpt": Market supply of avocados that will enter the US market (not by Delmonte).
                - week_start_date:first date of an ISO week, supply date. (Primary Key)
                - week_number: ISO week number. (Primary Key)
                - month: month. (Primary Key)
                - year: year. (Primary Key)
                - producing_region: avocado category. (Primary Key)
                - supply_quantity: supply quantity in cases.

        3- Use the following format:
        - Question: "Question here"
        - SQLQuery: "SQL Query to run"
        - SQLResult: "Result of the SQLQuery"
        - Answer: "Final answer here"
        - Recommendations: "Provide recommendations and actions to take based on the data."""

        prompt_temp += '\n\n\tQuestion: {input}'
        print(prompt_temp)
        return prompt_temp


predefined_report_prompt = """You are tasked with summarizing two texts, 
you are working at Del Monte's avocado market. 
When necessary; do your best to find a relationship between the first text and the second text, 
and try to justify the first text by the second text. Do not return the original texts. 
Read both texts and create a summary of the texts, include all the necessary numbers as bullet points. 
Provide a title for the summarized text. Remove any words related to SQLResults or SQL in general."""

sorry_instruction = """Say sorry if you do not know the answer to the question, 
otherwise answer the question. do not mention "an AI language model" sort of response, 
just answer the question with clarifications.

Question: {}
"""


sorry_words = [
    "sorry",
    "apologize",
    "regretful",
    "apologetic",
    "mea culpa",
    "lo siento",
    "disculpa",
    "lamentable",
    "arrepentido",
    "mea culpa",
    "آسف",
    "معذرة",
    "نادم",
    "اعتذاري",
    "خطأي",
    "عذرا"
]
