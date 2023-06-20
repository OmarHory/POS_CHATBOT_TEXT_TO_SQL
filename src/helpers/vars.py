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


    prompt_temp = f"""
        Given an input question, first create a syntactically correct MySQL query to run based on the table schema, then look at the results of the query and return the answer based on the following instructions:  

        1- Tables Schemas and description (only use those):
                A. "branches": Branches of the {client_type}, contains the following columns:
                        - id: incremental id. (Primary Key)
                        - external_id: branch id.
                        - name: branch name. 
                        - slug: branch slug.
                        - client_id: client id. (Foreign Key to clients table)
                        - opening_from: opening hour, format HH. 
                        - opening_to: closing hour, format HH.

                B. "products": A product has a single category and multiple options / modifiers, contains the following columns:
                        - id: incremental id. (Primary Key)
                        - external_id: product id.
                        - name: product name.
                        - sku: product sku.
                        - category_id: category id. (Foreign Key to categories table)
                        - is_active: is the product active or not.
                        - is_stock: is the product a stock product or not.
                        - price: price of the product in {client_currency_full} or {client_currency_short}.
                        - client_id: client id. (Foreign Key to clients table)

                B. "categories": Categories of the products, each product has a single category, contains the following columns:
                        - id: incremental id. (Primary Key)
                        - external_id: category id.
                        - name: category name; can be one of the following: {client_categories}
                        - slug: category slug.
                        - client_id: client id. (Foreign Key to clients table)

                D. "order_headers": Order header is the main table, which has general information about the order, contains the following columns:
                        - id: incremental id. (Primary Key)
                        - external_id: order id.
                        - ordered_at: order date and time, format YYYY-MM-DD HH:MM:SS.
                        - branch_id: branch id. (Foreign Key to branches table)
                        - type: order type, can be one of the following: {client_order_types}.
                        - source: order source, can be one of the following: {client_order_sources}.
                        - status: order status, can be one of the following: {client_order_statuses}.
                        - total_price: order total price in {client_currency_full} or {client_currency_short}.
                        - client_id: client id. (Foreign Key to clients table)

                E. "order_details": Order details is the table that contains the products of the order, contains the following columns:
                        - id: incremental id. (Primary Key)
                        - external_id: order details id.
                        - order_header_id: order header id. (Foreign Key to order_headers table)
                        - product_id: product id. (Foreign Key to products table)
                        - quantity: quantity of the product in units.
                        - client_id: client id. (Foreign Key to clients table)

                F. "order_options": Order Options is the table that contains the options / modifiers on the order, contains the following columns:
                        - id: incremental id. (Primary Key)
                        - external_id: option id.
                        - order_details_id: order details id. (Foreign Key to order_details table)
                        - name: option name.
                        - name_localized: option name.
                        - sku: option sku.
                        - quantity: quantity of the option in units.
                        - client_id: client id. (Foreign Key to clients table)

        2- Instructions:
                A. General instructions:
                        - You are a {client_type} data analyst, you report analytics about your {client_type}, and you give actions and recommendations to increase revenue.
                        - Your task is to answer questions related to a {client_type}.
                        - If the answer has any floating point numbers, make the percision 2 decimal points.
                        - Add a thousand separator to the numbers.

                B. {client_type} instructions:
                        - {client_type} name: {client_name}.
                        - {client_type} country and Location: {client_country}.
                        - {client_type} branches (branch_name : branch_id): {client_branches}
                        - The {client_type} works everyday on specific hours based on the branch.
                        - Each order has multiple products, and each product might have multiple options / modifiers.
                        - Each product has a single category, and each product might have multiple options / modifiers.
                        - Weekends are on Friday and Saturday.
                        - When asked about quantity, return the quantity in units.
                        - When asked about sales or price, return the sales or price in {client_currency_full} or {client_currency_short}.
                        - If the user asks about future analysis and promotions, return the analysis based on the current date and time.
                        - Expect the user to mispell the product name, if not mentioned, then do not filter on the product.
                        
                
                C. SQL instructions:
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
                        - Read the tables Schemas carefully, do not select columns that are not in the table you are querying.
                        - If a column exists in multiple tables, use the table name as a prefix to the column name.
                        - Always use the table name as a prefix to the column name.
                        - Return the answer in a readable format, do not return the MySQL query, return the answer only.
                        - Generate a full MySQL query, do not use any predefined queries, generate the query based on the question.
                        - Do not cut off the generated query, return the full query.
                        - Do the necessary analysis to answer, do the necessary aggregations and calculations to answer the questions.
                        - When you are asked about options, make sure to consult the order_details and order_headers tables.
                        - ordered_at can be only found in the order_headers table.
                        - When you are asked about sales, consult the order_headers total_price column only!

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

                

        3- Use the following format:
                - Question: "Question here"
                - SQLQuery: "SQL Query to run"
                - SQLResult: "Result of the SQLQuery"
                - Answer: "Final answer here in {user_language} only."
                
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

Tables Schemas and description:
        A. "branches": Branches table, contains the following columns:
                - id: incremental id. (Primary Key)
                - external_id: branch id.
                - name: branch name. 
                - slug: branch slug.
                - client_id: client id. (Foreign Key to clients table)
                - opening_from: opening hour, format HH. 
                - opening_to: closing hour, format HH.

        B. "categories": Categories table, contains the following columns:
                - id: incremental id. (Primary Key)
                - external_id: category id.
                - name: category name.
                - slug: category slug.
                - client_id: client id. (Foreign Key to clients table)

        C. "products": Products table, contains the following columns:
                - id: incremental id. (Primary Key)
                - external_id: product id.
                - name: product name.
                - sku: product sku.
                - category_id: category id. (Foreign Key to categories table)
                - is_active: is the product active or not.
                - is_stock: is the product a stock product or not.
                - client_id: client id. (Foreign Key to clients table)

        D. "order_headers": Order header table, contains the following columns:
                - id: incremental id. (Primary Key)
                - external_id: order id.
                - ordered_at: order date and time, format YYYY-MM-DD HH:MM:SS.
                - branch_id: branch id. (Foreign Key to branches table)
                - type: order type.
                - source: order source.
                - status: order status.
                - total_price: order total price.
                - client_id: client id. (Foreign Key to clients table)

        E. "order_details": Order details table, contains the following columns:
                - id: incremental id. (Primary Key)
                - external_id: order details id.
                - order_header_id: order header id. (Foreign Key to order_headers table)
                - product_id: product id. (Foreign Key to products table)
                - quantity: quantity of the product in units.
                - client_id: client id. (Foreign Key to clients table)

        F. "order_options": Order Options table, contains the following columns:
                - id: incremental id. (Primary Key)
                - external_id: option id.
                - order_details_id: order details id. (Foreign Key to order_details table)
                - name: option name.
                - name_localized: option name.
                - sku: option sku.
                - quantity: quantity of the option in units.
                - client_id: client id. (Foreign Key to clients table)

Just return the result in the following format:
"Only write the SQL Query, I want to copy paste your response, do not write anything other than the SQL query"
"""

sql_revision_prompt = """Your task is to add MySQL Queries based on an error, user question and table schema, below is a MySQL query that I got the followng error on:
Error and SQL Query: 
{}

Tables Schemas and description:
        A. "branches": Branches table, contains the following columns:
                - id: incremental id. (Primary Key)
                - external_id: branch id.
                - name: branch name. 
                - slug: branch slug.
                - client_id: client id. (Foreign Key to clients table)
                - opening_from: opening hour, format HH. 
                - opening_to: closing hour, format HH.

        B. "categories": Categories table, contains the following columns:
                - id: incremental id. (Primary Key)
                - external_id: category id.
                - name: category name.
                - slug: category slug.
                - client_id: client id. (Foreign Key to clients table)

        C. "products": Products table, contains the following columns:
                - id: incremental id. (Primary Key)
                - external_id: product id.
                - name: product name.
                - sku: product sku.
                - category_id: category id. (Foreign Key to categories table)
                - is_active: is the product active or not.
                - is_stock: is the product a stock product or not.
                - client_id: client id. (Foreign Key to clients table)

        D. "order_headers": Order header table, contains the following columns:
                - id: incremental id. (Primary Key)
                - external_id: order id.
                - ordered_at: order date and time, format YYYY-MM-DD HH:MM:SS.
                - branch_id: branch id. (Foreign Key to branches table)
                - type: order type.
                - source: order source.
                - status: order status.
                - total_price: order total price.
                - client_id: client id. (Foreign Key to clients table)

        E. "order_details": Order details table, contains the following columns:
                - id: incremental id. (Primary Key)
                - external_id: order details id.
                - order_header_id: order header id. (Foreign Key to order_headers table)
                - product_id: product id. (Foreign Key to products table)
                - quantity: quantity of the product in units.
                - client_id: client id. (Foreign Key to clients table)

        F. "order_options": Order Options table, contains the following columns:
                - id: incremental id. (Primary Key)
                - external_id: option id.
                - order_details_id: order details id. (Foreign Key to order_details table)
                - name: option name.
                - name_localized: option name.
                - sku: option sku.
                - quantity: quantity of the option in units.
                - client_id: client id. (Foreign Key to clients table)

Just return the result in the following format:
"Only write the SQL Query, I want to copy paste your response, do not write anything other than the SQL query"
"""


sql_add_filter_prompt = """Your task is to modify to the below MySQL query a filter client_id=2  (handle the aliasing correctly and prefixes if exist.)

SQL Query: {}

Tables Schemas and description:
        A. "branches": Branches table, contains the following columns:
                - id: incremental id. (Primary Key)
                - external_id: branch id.
                - name: branch name. 
                - slug: branch slug.
                - client_id: client id. (Foreign Key to clients table)
                - opening_from: opening hour, format HH. 
                - opening_to: closing hour, format HH.

        B. "categories": Categories table, contains the following columns:
                - id: incremental id. (Primary Key)
                - external_id: category id.
                - name: category name.
                - slug: category slug.
                - client_id: client id. (Foreign Key to clients table)

        C. "products": Products table, contains the following columns:
                - id: incremental id. (Primary Key)
                - external_id: product id.
                - name: product name.
                - sku: product sku.
                - category_id: category id. (Foreign Key to categories table)
                - is_active: is the product active or not.
                - is_stock: is the product a stock product or not.
                - price: price of the product.
                - client_id: client id. (Foreign Key to clients table)

        D. "order_headers": Order header table, contains the following columns:
                - id: incremental id. (Primary Key)
                - external_id: order id.
                - ordered_at: order date and time, format YYYY-MM-DD HH:MM:SS.
                - branch_id: branch id. (Foreign Key to branches table)
                - type: order type.
                - source: order source.
                - status: order status.
                - total_price: order total price.
                - client_id: client id. (Foreign Key to clients table)

        E. "order_details": Order details table, contains the following columns:
                - id: incremental id. (Primary Key)
                - external_id: order details id.
                - order_header_id: order header id. (Foreign Key to order_headers table)
                - product_id: product id. (Foreign Key to products table)
                - quantity: quantity of the product in units.
                - price: price of the product.
                - client_id: client id. (Foreign Key to clients table)

        F. "order_options": Order Options table, contains the following columns:
                - id: incremental id. (Primary Key)
                - external_id: option id.
                - order_details_id: order details id. (Foreign Key to order_details table)
                - name: option name.
                - name_localized: option name.
                - sku: option sku.
                - quantity: quantity of the option in units.
                - unit_price: unit price of the option.
                - total_price: total price of the option.
                - total_cost: total cost of the option.
                - client_id: client id. (Foreign Key to clients table)


Return the result in the following format:
SQL Query: [The Modified SQL Query]

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
]
