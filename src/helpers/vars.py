from datetime import datetime
import pytz
from config import config_business

business_name = config_business["business_name"]
business_type = config_business["business_type"]
business_currency_full = config_business["business_currency_full"]
business_currency_short = config_business["business_currency_short"]
business_branches = config_business["business_branches"]
business_country = config_business["business_country"]
business_timezone = config_business["business_timezone"]
business_categories = config_business["business_categories"]
business_order_types = config_business["business_order_types"]
business_order_sources = config_business["business_order_sources"]
business_order_statuses = config_business["business_order_statuses"]

for_more_info = ""

general_menu = f"""Hello _USERNAME_HERE_! Welcome to the {business_name} AI Assistant! \U0001F44B \U0001F44B\n"""

intent_prompt = f"""What is the intent of this sentence:

"_PROMPT_HERE_"

Work as an intent classifier that works for a {business_type} called [{business_name}]. Classify the intent of the above prompt, return the output without formatting, just the intent.

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


def gpt_sql_prompt(user_language):

        timezone_tz = pytz.timezone(business_timezone)
        timezone_datetime = datetime.now(timezone_tz)

        # Extract the date and time components
        today = timezone_datetime.strftime("%Y-%m-%d")
        time = timezone_datetime.strftime("%H:%M:%S")
        
        prompt_temp = f"""
        Given an input question, first create a syntactically correct MySQL query to run based on the table schema, then look at the results of the query and return the answer based on the following instructions:  

        1- Instructions:
       

                A. General instructions:
                        - You are a {business_type} data analyst, you report analytics about your {business_type}, and you give actions and recommendations to increase revenue.
                        - Your task is to answer questions related to a {business_type}.
                        - If the answer has any floating point numbers, make the percision 2 decimal points.
                        - Add a thousand separator to the numbers.

                B. {business_type} instructions:
                        - {business_type} name: {business_name}.
                        - {business_type} country and Location: {business_country}.
                        - {business_type} branches (branch_name : branch_id): {business_branches}
                        - The {business_type} works everyday on specific hours based on the branch.
                        - Weekends are on Friday and Saturday.
                        - When asked about quantity, return the quantity in units.
                        - When asked about sales or price, return the sales or price in {business_currency_full} or {business_currency_short}.
                        - If the user asks about future analysis and promotions, return the analysis based on the current date and time.
                        - Expect the user to mispell the product name, if not mentioned, then do not filter on the product.
                
                C. SQL instructions:
                        - Use the following format: 
                                - SELECT: select the columns that are needed to answer the question, return more columns where suitable.
                                - FROM: select the table that has the columns that are needed to answer the question.
                                - WHERE: filter the columns based on the question.
                                - GROUP BY: group the columns based on the question.
                                - ORDER BY: order the columns based on the question.
                                - LIMIT: limit the number of rows based on the question.
                                - JOIN: join the tables based on the question.
                                - HAVING: filter the columns based on the question after the group by.
                        - Read the tables Schemas carefully, do not select columns that are not in the table you are querying.
                        - If a column exists in multiple tables, use the table name as a prefix to the column name.
                        - Always use the table name as a prefix to the column name.
                        - Return the answer in a readable format, do not return the MySQL query, return the answer only.
                        - Generate a full MySQL query, do not use any predefined queries, generate the query based on the question.
                        - Do not cut off the generated query, return the full query.
                        - Expect the user to misspell the branch name so use the branch id in the SQL query, expect the user to mention the branch name in the question, if not mentioned, then do not filter on the branch.
                        - Do the necessary analysis to answer, do the necessary aggregations and calculations to answer the questions.
                        - Return SQL queries that do not result in a huge amount of data, limit the number of rows returned to 100 rows where suitable.

                D. Time instructions:
                        - Today's date is {today}, the current time is {time}, use it as a reference to answer the questions where needed.
                        - The time is in the following format: HH:MM:SS.
                        - The time is in 24 hour format.
                        - The time is in {business_country} timezone.

        2- Tables Schemas and description:

                A. "branches": Branches table, contains the following columns:
                        - branch_id: branch id. (Primary Key)
                        - branch_name: branch name. 
                        - opening_from: opening hour, format HH. 
                        - opening_to: closing hour, format HH.

                B. "categories": Categories table, contains the following columns:
                        - category_id: category id. (Primary Key)
                        - category_name: category name can be one of the following: {business_categories}.

                C. "products": Products table, contains the following columns:
                        - product_id: product id. (Primary Key)
                        - product_name: product name. 
                        - product_sku: product sku. 
                        - category_id: category id. (Foreign Key to categories table)
                        - is_active: is the product active or not. 
                        - is_stock_product: is the product a stock product or not. 
                        - price: price of the product in {business_currency_full} or {business_currency_short}. 

                D. "order_header": Order header table, contains the following columns:
                        - order_header_id: order header id. (Primary Key)
                        - branch_id: branch id. (Foreign Key to branches table)
                        - order_datetime: order datetime, format: YYYY-MM-DD HH:MM:SS.
                        - order_type: order type, can be one of the following: {business_order_types}.
                        - order_source: order source, can be one of the following: {business_order_sources}.
                        - order_status: order status, can be one of the following: {business_order_statuses}.
                        - order_total_price: order total price in {business_currency_full} or {business_currency_short}.

                E. "order_details": Order details table, contains the following columns:
                        - order_details_id: order details id. (Primary Key)
                        - order_header_id: order header id. (Foreign Key to order_header table)
                        - product_id: product id. (Foreign Key to products table)
                        - category_id: category id. (Foreign Key to categories table)
                        - quantity: quantity of the product in units. 
                        - price: price of the product in {business_currency_full} or {business_currency_short}. 


        3- Use the following format:
        - Question: "Question here"
        - SQLQuery: "SQL Query to run"
        - SQLResult: "Result of the SQLQuery"
        - Answer: "Final answer here in {user_language} only."
        - Recommendations: "Always Provide professional recommendations and actions to take based on the data to increase revenue."
        """

        prompt_temp += '\n\n\tQuestion: {input}'
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
    "Arabic": ['ا', 'ب', 'ت', 'ث', 'ج', 'ح', 'خ', 'د', 'ذ', 'ر', 'ز', 'س', 'ش', 'ص', 'ض', 'ط', 'ظ', 'ع', 'غ', 'ف', 'ق', 'ك', 'ل', 'م', 'ن', 'ه', 'و', 'ي'],
}

sql_revision_prompt = """Your task is to debug MySQL Queries based on a user question, below is a MySQL query that I got the followng error on:
Error: 
{}

SQL Query: 
{}

Just return the result in the following format:
"Only write the SQL Query, I want to copy paste your response, do not write anything other than the SQL query"
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