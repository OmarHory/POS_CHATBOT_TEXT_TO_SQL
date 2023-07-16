from datetime import datetime
import pytz


def for_more_info():
    return ""


def general_menu(username, client_name):
    general_menu = f"""Hello {username}! Welcome to the {client_name} AI Assistant! \U0001F44B \U0001F44B\n"""
    return general_menu


def intent_prompt(incoming_msg, client_type, client_name):
    intent_prompt = f"""What is the intent of this sentence:

        Sentence: "{incoming_msg}"

        Work as an intent classifier that works for a {client_type} called [{client_name}]. Classify the intent of the above prompt, return the output without formatting, just the intent.

        Please choose one of the following intents, do not generate your own intents:
        - Greeting 
                When the user says hello, hi, hello there, etc.

        - Orders
                When the user intention is to know information about the orders or sales.

        - Farewell 
                When the user says goodbye, have a good one, see ya, etc..

        - Undefined 
                When the user says something that is not totally related to the above intents.

        If the prompt has mix intents, choose the intent that has the higher weight."""

    return intent_prompt


def farewell(username):
    return f"Thank you {username}! Have a nice day! \U0001F44B \U0001F44B\n"


def gpt_sql_prompt(
    user_language,
    client_branches,
    client_type,
    client_name,
    client_currency_full,
    client_currency_short,
    client_country,
    client_timezone,
    client_categories,
    client_order_types,
    client_order_sources,
    client_order_statuses,
    client_id,
):
    #if client_branches is list don't split
    if type(client_branches) != list:  
        client_branches = client_branches.split(",")
        client_order_types = client_order_types.split(",")
        client_order_sources = client_order_sources.split(",")
        client_order_statuses = client_order_statuses.split(",")
        client_categories = client_categories.split(",")
    timezone_tz = pytz.timezone(client_timezone)
    timezone_datetime = datetime.now(timezone_tz)

    # Extract the date and time components
    today = timezone_datetime.strftime("%Y-%m-%d")
    time = timezone_datetime.strftime("%H:%M:%S")

    #adjust branches list in the following format
    # - Branch 1
    # - Branch 2
#     client_branches = "\n".join([f"- {branch}" for branch in client_branches])
    print(client_branches)

    #adjust branches list in the following format
    # - Branch 1
    # - Branch 2
    client_branches = "\n".join([f"- {branch}" for branch in client_branches])
    print(client_branches)


    prompt_temp = f"""
        Given an input question, first create a syntactically correct MySQL query to run based on the table schema, then look at the results of the query and return the answer based on the following instructions:  

        1- Tables Schemas and description (only use those):
                A. "branches": Branches of the {client_type}, contains the following columns:
                        - id: incremental id. (Primary Key)
                        - external_id: branch id.
                        - name: branch name. 
                        - slug: branch slug.
                        - client_id: client id. (Foreign Key to clients table)
                        - opening_from: opening hour, format HH:MM. 
                        - opening_to: closing hour, format HH:MM.

                B. "products": A product has a single category and multiple options / modifiers, contains the following columns:
                        - id: incremental id. (Primary Key)
                        - external_id: product id.
                        - name: product name.
                        - sku: product sku.
                        - category_id: category id. (Foreign Key to categories table)
                        - client_id: client id. (Foreign Key to clients table)

                C. "categories": Categories of the products, each product has a single category, contains the following columns:
                        - id: incremental id. (Primary Key)
                        - external_id: category id.
                        - name: category name; can be one of the following: {client_categories}
                        - slug: category slug.
                        - client_id: client id. (Foreign Key to clients table)

                D. "order_headers": Order header is the main table for different orders at a certain timestamp, which has general information about the order, contains the following columns:
                        - id: incremental id. (Primary Key)
                        - external_id: order id.
                        - order_date: order date (business date), format YYYY-MM-DD.
                        - order_time: order time, format HH:MM:SS.
                        - branch_id: branch id. (Foreign Key to branches table)
                        - type: order type, can be one of the following: {client_order_types}.
                        - source: order source, can be one of the following: {client_order_sources}.
                        - status: order status, can be one of the following: {client_order_statuses}.
                        - total_price: order total price in {client_currency_full} or {client_currency_short}.
                        - discount_amount: order discount amount in {client_currency_full} or {client_currency_short}.
                        - client_id: client id. (Foreign Key to clients table)

                E. "order_details": Order details is the table that contains the information of the ordered products per order, contains the following columns:
                        - id: incremental id. (Primary Key)
                        - external_id: order details id.
                        - order_header_id: order header id. (Foreign Key to order_headers table)
                        - product_id: product id. (Foreign Key to products table)
                        - quantity: quantity of the product in units.
                        - price: price of the ordered product in {client_currency_full} or {client_currency_short}, this price is already multiplied by the quantity.
                        - client_id: client id. (Foreign Key to clients table)

                F. "order_options": Order Options is the table that contains the options / modifiers on the ordered products, contains the following columns:
                        - id: incremental id. (Primary Key)
                        - external_id: option or modifier id.
                        - order_details_id: order details id. (Foreign Key to order_details table)
                        - name: option or modifier name.
                        - name_localized: option or modifier name.
                        - sku: option or modifier sku.
                        - quantity: quantity of the option or modifier in units.
                        - unit_price: unit price of the option or modifier in {client_currency_full} or {client_currency_short}.
                        - price: price of the option or modifier in {client_currency_full} or {client_currency_short}.
                        - cost: cost of the option or modifier in {client_currency_full} or {client_currency_short}.
                        - client_id: client id. (Foreign Key to clients table)

        2- Instructions:
                A. General instructions:
                        - You are a {client_type} data analyst, you report analytics about your {client_type}, and you give actions and recommendations to increase revenue.
                        - Your task is to answer questions related to a {client_type}.
                        - If the answer has any floating point numbers, make the percision 2 decimal points.
                        - Add a thousand separator to the numbers.

                B. {client_type} instructions:
                        - {client_type} name: {client_name}.
                        - Country: {client_type} country and Location: {client_country}.
                        - Branches: The goal is to map any incoming branch name filter to one of the names in the predefined list:
                                {client_branches}
                        - A business day is from the branch opening hour to the branch closing hour.
                        - The {client_type} works everyday on specific hours based on the branch.
                        - Each order has multiple products, and each product might have multiple options / modifiers.
                        - Each product has a single category, and each product might have multiple options / modifiers.
                        - Weekends are on Friday and Saturday.
                        - When asked about quantity, return the quantity in units.
                        - When asked about sales or price, return the sales or price in {client_currency_full} or {client_currency_short}.
                        - If the user asks about future analysis and promotions, return the analysis based on the current date and time.
                        - Expect the user to mispell the product name, if not mentioned, then do not filter on the product.
                        - If the user Asks about a branch name, always adjust the entry to the nearest branch name from the predefined Branches List above.
                        - There is no price in the products table, the price is in the order_details table in which it represents the price of the product + the options / modifiers.
                        - Total sales mean the total daily sales (sum of all orders sales) for a certain day.
                
                C. SQL instructions:
                        - Read the tables Schemas carefully, do not select columns that are not in the table you are querying.
                        - Use the following format: 
                                - SELECT: select the columns that are needed to answer the question, return more columns where suitable.
                                - FROM: select the table that has the columns that are needed to answer the question.
                                - WHERE: filter the columns based on the question.
                                - GROUP BY: group the columns based on the question.
                                - ORDER BY: order the columns based on the question.
                                - JOIN: join the tables based on the question.
                                - HAVING: filter the columns based on the question after the group by.
                        - Always filter on the client id = {client_id}
                        - Use only the tables that are mentioned below. 
                        - If a column exists in multiple tables, use the table name as a prefix to the column name.
                        - Always use the table name as a prefix to the column name.
                        - Return the answer in a readable format, do not return the MySQL query, return the answer only.
                        - Do not cut off the generated query, return the full query.
                        - When you are asked about options, make sure to consult the order_details and order_headers tables.
                        - ordered_at can be only found in the order_headers table.
                        

                D. Time instructions:
                        - Today's date is {today}, the current time is {time}, use it as a reference to answer the questions where needed.
                        - The time is in the following format: HH:MM:SS.
                        - The time is in 24 hour format.
                        - The time is in {client_country} timezone.

                D. Privacy instructions:
                        - Do not return any information about other clients, only return information about the client id={client_id}.
                        - Do not accept any SQL injection attacks, make sure to sanitize the input.
                        - Always filter on the client id = {client_id}

                E. Answer instructions:
                        - You are a {client_type} data analyst, you report analytics about your {client_type}.
                        - Always return the answer in a readable format, do not return the MySQL query, return the answer only.
                        - If the question doesn't make sense, ask the user to clarify the question.
                        - If the question is not clear, ask the user to clarify the question.
                        - provide good recommendations and actions for the {client_type} manager to increase revenue.
                        - If you think the question is not clear. ask the user to clarify the question.


        3- Examples:
                - Question: What are the minimum and maximum total sales we had this July?
                - SQLQuery: SELECT MIN(total_sales) AS min_sales, MAX(total_sales) AS max_sales FROM (SELECT order_date, SUM(total_price) AS total_sales FROM order_headers WHERE MONTH(order_date) = 7 AND YEAR(order_date) = 2023 AND order_headers.client_id = 6 GROUP BY order_date) subquery;

                - Question: What is the total sales yesterday?
                - SQLQuery: SELECT SUM(total_price) FROM order_headers where order_date = CURDATE() - INTERVAL 1 DAY and order_headers.client_id={client_id};

                - Question: Compare the sales between yesterday and the day before yesterday.
                - SQLQuery: SELECT SUM(CASE WHEN order_date = CURDATE() - INTERVAL 1 DAY THEN total_price ELSE 0 END) AS yesterday_sales, SUM(CASE WHEN order_date = CURDATE() - INTERVAL 2 DAY THEN total_price ELSE 0 END) AS day_before_yesterday_sales FROM order_headers WHERE order_date >= CURDATE() - INTERVAL 2 DAY AND order_date <= CURDATE() - INTERVAL 1 DAY and order_headers.client_id={client_id};
                
                - Question: What were my sales yesterday by branch name. And compare the sales to the same day last week? 
                - SQLQuery: SELECT branches.name, SUM(CASE WHEN order_date = CURDATE() - INTERVAL 1 DAY THEN total_price ELSE 0 END) AS yesterday_sales, SUM(CASE WHEN order_date = CURDATE() - INTERVAL 8 DAY THEN total_price ELSE 0 END) AS last_week_sales FROM order_headers JOIN branches ON branches.id = order_headers.branch_id WHERE order_date >= CURDATE() - INTERVAL 8 DAY AND order_date <= CURDATE() - INTERVAL 1 DAY and order_headers.client_id={client_id} GROUP BY branches.name;

                - Question: What is the top 5 products by sales yesterday?
                - SQLQuery: SELECT products.name, SUM(order_details.price) AS total_sales FROM order_details JOIN products ON products.id = order_details.product_id JOIN order_headers ON order_headers.id = order_details.order_header_id WHERE order_headers.order_date = CURDATE() - INTERVAL 1 DAY AND order_headers.client_id = {client_id} GROUP BY products.name ORDER BY total_sales DESC LIMIT 5;
                
                - Question: What is the top 5 products by sales yesterday by branch name?
                - SQLQuery: SELECT branches.name, products.name, SUM(order_details.price) AS total_sales FROM order_details JOIN products ON products.id = order_details.product_id JOIN order_headers ON order_headers.id = order_details.order_header_id JOIN branches ON branches.id = order_headers.branch_id WHERE order_headers.order_date = CURDATE() - INTERVAL 1 DAY AND order_headers.client_id = {client_id} GROUP BY branches.name, products.name ORDER BY total_sales DESC LIMIT 5;

                - Question: What is the top option by sales yesterday?
                - SQLQuery: SELECT order_options.name, SUM(order_options.price) AS total_sales FROM order_options JOIN order_details ON order_details.id = order_options.order_details_id JOIN order_headers ON order_headers.id = order_details.order_header_id WHERE order_headers.order_date = CURDATE() - INTERVAL 1 DAY AND order_headers.client_id = {client_id} GROUP BY order_options.name ORDER BY total_sales DESC LIMIT 1;

                - Question: What is the top option in sales, and which product it belongs to?
                - SQLQuery: SELECT products.name, order_options.name, SUM(order_options.price) AS total_sales FROM order_options JOIN order_details ON order_details.id = order_options.order_details_id JOIN order_headers ON order_headers.id = order_details.order_header_id JOIN products ON products.id = order_details.product_id WHERE order_headers.order_date = CURDATE() - INTERVAL 1 DAY AND order_headers.client_id = {client_id} GROUP BY products.name, order_options.name ORDER BY total_sales DESC LIMIT 1;
        
                - Question: Compare the percentage of sales between yesterday and the day before yesterday?
                - SQLQuery: SELECT SUM(CASE WHEN order_date = CURDATE() - INTERVAL 1 DAY THEN total_price ELSE 0 END) AS yesterday_sales, SUM(CASE WHEN order_date = CURDATE() - INTERVAL 2 DAY THEN total_price ELSE 0 END) AS day_before_yesterday_sales, (SUM(CASE WHEN order_date = CURDATE() - INTERVAL 1 DAY THEN total_price ELSE 0 END) - SUM(CASE WHEN order_date = CURDATE() - INTERVAL 2 DAY THEN total_price ELSE 0 END)) / SUM(CASE WHEN order_date = CURDATE() - INTERVAL 2 DAY THEN total_price ELSE 0 END) * 100 AS percentage_change FROM order_headers WHERE order_date >= CURDATE() - INTERVAL 2 DAY AND order_date <= CURDATE() - INTERVAL 1 DAY and order_headers.client_id={client_id};

                - Question: Compare yesterdays sales per item with the average daily sales from June 2023. And highlight some key changes, for example, highest growth item, highest decrease in sales, etc.
                - SQLQuery: SELECT products.name, SUM(CASE WHEN order_headers.order_date = CURDATE() - INTERVAL 1 DAY THEN order_details.price ELSE 0 END) AS yesterday_sales, SUM(CASE WHEN MONTH(order_headers.order_date) = 6 AND YEAR(order_headers.order_date) = 2023 THEN order_details.price/30 ELSE 0 END) AS average_daily_june_sales FROM order_details JOIN products ON products.id = order_details.product_id JOIN order_headers ON order_headers.id = order_details.order_header_id WHERE (order_headers.order_date = CURDATE() - INTERVAL 1 DAY OR (MONTH(order_headers.order_date) = 6 AND YEAR(order_headers.order_date) = 2023)) AND order_headers.client_id = {client_id} GROUP BY products.name;

                - Question: What was the fastest growing items of sales yesterday, compared with a day before?
                - SQLQuery: SELECT products.name, SUM(CASE WHEN order_headers.order_date = CURDATE() - INTERVAL 1 DAY THEN order_details.price ELSE 0 END) AS yesterday_sales, SUM(CASE WHEN order_headers.order_date = CURDATE() - INTERVAL 2 DAY THEN order_details.price ELSE 0 END) AS day_before_yesterday_sales, ((SUM(CASE WHEN order_headers.order_date = CURDATE() - INTERVAL 1 DAY THEN order_details.price ELSE 0 END) - SUM(CASE WHEN order_headers.order_date = CURDATE() - INTERVAL 2 DAY THEN order_details.price ELSE 0 END)) / SUM(CASE WHEN order_headers.order_date = CURDATE() - INTERVAL 2 DAY THEN order_details.price ELSE 0 END)) * 100 AS percentage_growth FROM order_details JOIN products ON products.id = order_details.product_id JOIN order_headers ON order_headers.id = order_details.order_header_id WHERE order_headers.order_date >= CURDATE() - INTERVAL 2 DAY AND order_headers.order_date <= CURDATE() - INTERVAL 1 DAY AND order_headers.client_id = {client_id} GROUP BY products.name ORDER BY percentage_growth DESC LIMIT 1;

                - Question: Compare today's sales for the average daily sales last may.
                - SQLQuery: SELECT SUM(CASE WHEN order_date = CURDATE() THEN total_price ELSE 0 END) AS today_sales, SUM(CASE WHEN MONTH(order_date) = 5 AND YEAR(order_date) = 2023 THEN total_price/31 ELSE 0 END) AS average_daily_may_sales FROM order_headers WHERE client_id={client_id};

                - Question: Compare today's sales to same day last week.
                - SQLQuery: SELECT SUM(CASE WHEN order_date = CURDATE() THEN total_price ELSE 0 END) AS today_sales, SUM(CASE WHEN order_date = CURDATE() - INTERVAL 7 DAY THEN total_price ELSE 0 END) AS last_week_sales FROM order_headers WHERE order_headers.client_id = 6;
        
        4- Use the following format:
                - Question: "Question here"
                - SQLQuery: "SQL Query to run"
                - SQLResult: "Result of the SQLQuery"
                - Answer: "Final answer here in {user_language} only. Add emojis to each paragraph (to be compatible with whatsapp)."
                
        """
# - Recommendations: "Always Provide professional recommendations and actions to take based on the data to increase revenue."

    prompt_temp += "\n\n\tQuestion: {input}"
    return prompt_temp


sorry_instruction = """Say sorry if you do not know the answer to the question, 
otherwise answer the question. do not mention "an AI language model" sort of response, 
just answer the question with clarifications.
Answer the question in {} only.

Question: {}
"""

translate_ar_prompt_ = """Translate the following {} (MSA or Dialect) to English:

                        {}"""
language_map = {
    "Arabic": [
        "ا",
        "ب",
        "ت",
        "ث",
        "ج",
        "ح",
        "خ",
        "د",
        "ذ",
        "ر",
        "ز",
        "س",
        "ش",
        "ص",
        "ض",
        "ط",
        "ظ",
        "ع",
        "غ",
        "ف",
        "ق",
        "ك",
        "ل",
        "م",
        "ن",
        "ه",
        "و",
        "ي",
    ],
}

sql_revision_prompt = """Your task is to debug MySQL Queries based on an error, user question and table schema, below is a MySQL query that I got the followng error on:
Error and SQL Query: 
{}

User Question:
{}

Tables Schemas and description (only use those):
                A. "branches": Branches table.
                        - id: incremental id. (Primary Key)
                        - external_id: branch id.
                        - name: branch name. 
                        - slug: branch slug.
                        - client_id: client id. (Foreign Key to clients table)
                        - opening_from: opening hour, format HH:MM. 
                        - opening_to: closing hour, format HH:MM.

                B. "products": A product has a single category and multiple options / modifiers, contains the following columns:
                        - id: incremental id. (Primary Key)
                        - external_id: product id.
                        - name: product name.
                        - sku: product sku.
                        - category_id: category id. (Foreign Key to categories table)
                        - client_id: client id. (Foreign Key to clients table)

                C. "categories": Categories of the products, each product has a single category, contains the following columns:
                        - id: incremental id. (Primary Key)
                        - external_id: category id.
                        - name: category name.
                        - slug: category slug.
                        - client_id: client id. (Foreign Key to clients table)

                D. "order_headers": Order header is the main table, which has general information about the order, contains the following columns:
                        - id: incremental id. (Primary Key)
                        - external_id: order id.
                        - order_date: order date (business date), format YYYY-MM-DD.
                        - order_time: order time, format HH:MM:SS.
                        - branch_id: branch id. (Foreign Key to branches table)
                        - type: order type.
                        - source: order source.
                        - status: order status.
                        - total_price: order total price.
                        - discount_amount: order discount amount.
                        - client_id: client id. (Foreign Key to clients table)

                E. "order_details": Order details is the table that contains the information of the ordered products, contains the following columns:
                        - id: incremental id. (Primary Key)
                        - external_id: order details id.
                        - order_header_id: order header id. (Foreign Key to order_headers table)
                        - product_id: product id. (Foreign Key to products table)
                        - quantity: quantity of the product in units.
                        - price: price of the ordered product.
                        - client_id: client id. (Foreign Key to clients table)

                F. "order_options": Order Options is the table that contains the options / modifiers on the ordered products, contains the following columns:
                        - id: incremental id. (Primary Key)
                        - external_id: option or modifier id.
                        - order_details_id: order details id. (Foreign Key to order_details table)
                        - name: option or modifier name.
                        - name_localized: option or modifier name.
                        - sku: option or modifier sku.
                        - quantity: quantity of the option or modifier in units.
                        - unit_price: unit price of the option or modifier.
                        - price: price of the option or modifier.
                        - cost: cost of the option or modifier.
                        - client_id: client id. (Foreign Key to clients table)


Just return the result in the following format:
"Only write the SQL Query, I want to copy paste your response, do not write anything other than the SQL query"
"""


sql_add_filter_prompt = """
Your task is to modify MySQL Queries. For any `select` statement in the below MySQL query, make sure to add client_id = {}  in the `where` clause.
- Add the client_id filter for each selected table.
- Handle aliasing accordingly when adding the filter.

MySQL Query: {}

Return the answer in the following format:
- Return the SQL Query only without any extra text.
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
    "عذرا",
    "للأسف",
    "لا أعلم",
    "عفوًا",
    "لا أعرف",
    "أعتذر"
]
