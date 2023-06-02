for_more_info = ""

list_of_approved_emails = ["o_hawary@hotmail.com", "omar@sitech.me"]

general_menu = """مرحبا بك! انا مساعدك الشخصي لشاورما فور تشكس 🤖 يا حياالله فيك!"""


intent_prompt = """What is the intent of this sentence:

"{prompt}"

Work as an intent classifier that works for a restaurant called [Shawarma 4 Chicks]. Classify the intent of the above prompt, return the output without formatting, just the intent.

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


gpt_prompt = """{prompt}"""

def gpt_sql_prompt(user_language):
        import datetime
        from datetime import datetime, date, timedelta
        import pytz

        # today_ = date.today()
        # today = today_.strftime("%Y-%m-%d")
        # yesterday = (today_ - timedelta(days=1)).strftime("%Y-%m-%d")
        # hour = datetime.now().hour + 3
        # print(date.today())
        jordan_tz = pytz.timezone('Asia/Amman')
        jordan_datetime = datetime.now(jordan_tz)

        # Extract the date and time components
        today = jordan_datetime.strftime("%Y-%m-%d")
        time = jordan_datetime.strftime("%H:%M:%S")
        prompt_temp = f"""
        Given an input question, first create a syntactically correct MySQL query to run based on the table schema, then look at the results of the query and return the answer based on the following instructions:  

        1- Instructions:
       

                A. General instructions:
                        - You are a restaurant data analyst, you report analytics about your restaurant.
                        - Your task is to answer questions related to a restaurant.
                        - If the answer has any floating point numbers, make the percision 2 decimal points.
                        - Add a thousand separator to the numbers.

                B. Restaurant instructions:
                        - Restaurant name: Shawarma 4 Chicks.
                        - Restaurant country and Location: Jordan.
                        - Restaurant branches (branch_name : branch_id): [4Chicks Abdoun : 975b3d24-cb71-4df8-930e-054bcd67f90c, 4Chicks 7th circle:975b3d24-ce3d-4801-9c11-582a817cc591, 4Chicks Al-Jubeha:976744f0-20ac-4dd5-a06a-6a1ee9ffa7b5]
                        - The restaurant works everyday on specific hours based on the branch.
                        - Weekends are on Friday and Saturday.
                
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

                D. Time instructions:
                        - Today's date is {today}, the current time is {time}, use it as a reference to answer the questions where needed.
                        - The time is in the following format: HH:MM:SS.
                        - The time is in 24 hour format.
                        - The time is in Jordanian timezone.

        2- Tables Schemas and description:

                A. "branches": Branches table, contains the following columns:
                        - branch_id: branch id. (Primary Key)
                        - branch_name: branch name. 
                        - opening_from: opening hour, format HH. 
                        - opening_to: closing hour, format HH.

                B. "categories": Categories table, contains the following columns:
                        - category_id: category id. (Primary Key)
                        - category_name: category name can be one of the following: [Shawarma, Fries, Drinks, Juices, Chicken burger, Sauces].

                C. "products": Products table, contains the following columns:
                        - product_id: product id. (Primary Key)
                        - product_name: product name. 
                        - product_sku: product sku. 
                        - category_id: category id. (Foreign Key to categories table)
                        - is_active: is the product active or not. 
                        - is_stock_product: is the product a stock product or not. 
                        - price: price of the product in Jordanian Dinars or JD. 

                D. "order_header": Order header table, contains the following columns:
                        - order_header_id: order header id. (Primary Key)
                        - branch_id: branch id. (Foreign Key to branches table)
                        - order_datetime: order datetime, format: YYYY-MM-DD HH:MM:SS.
                        - order_type: order type, can be one of the following: [Dine In, Pick Up, Delivery, Drive Thru].
                        - order_source: order source, can be one of the following: [Cashier, API, Call Center].
                        - order_status: order status, can be one of the following: [Pending, Active, Declined, Closed, Returned, Joined, Void].
                        - order_total_price: order total price in Jordanian Dinars or JD.

                E. "order_details": Order details table, contains the following columns:
                        - order_details_id: order details id. (Primary Key)
                        - order_header_id: order header id. (Foreign Key to order_header table)
                        - product_id: product id. (Foreign Key to products table)
                        - category_id: category id. (Foreign Key to categories table)
                        - quantity: quantity of the product in units. 
                        - price: price of the product in Jordanian Dinars or JD. 


        3- Use the following format:
        - Question: "Question here"
        - SQLQuery: "SQL Query to run"
        - SQLResult: "Result of the SQLQuery"
        - Answer: "Final answer here in {user_language} only."
        - Recommendations: "Provide recommendations and actions to take based on the data."
        """

        prompt_temp += '\n\n\tQuestion: {input}'
        return prompt_temp

sorry_instruction = """Say sorry if you do not know the answer to the question, 
otherwise answer the question. do not mention "an AI language model" sort of response, 
just answer the question with clarifications.
Answer the question in {} only.

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
    "عذرا",
    "للأسف",
    "لا أعلم",
    "عفوًا",
    "لا أعرف",
]


translate_ar_prompt_ = """Translate the following {} (MSA or Dialect) to English:

                        {}"""
language_map = {
    "Arabic": ['ا', 'ب', 'ت', 'ث', 'ج', 'ح', 'خ', 'د', 'ذ', 'ر', 'ز', 'س', 'ش', 'ص', 'ض', 'ط', 'ظ', 'ع', 'غ', 'ف', 'ق', 'ك', 'ل', 'م', 'ن', 'ه', 'و', 'ي'],
}

sql_revision_prompt = """Your task is to debug MySQL Queries, below is a MySQL query that I got the followng error on:
Error: 
{}

SQL Query: 
{}

Just return the result in the following format:
"Only write the SQL Query, I want to copy paste your response, do not write anything other than the SQL query"
"""