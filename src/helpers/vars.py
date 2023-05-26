from helpers.utils import get_wsd, get_wsd_string

for_more_info = ""

list_of_approved_emails = ["o_hawary@hotmail.com", "omar@sitech.me"]

general_menu = """Hello there, I am Bash Mohandes, I am here to help you with your questions about Shawarma 4 Chicks.\nAsk any question you would like about Sales / Orders."""


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

def gpt_sql_prompt():
        import datetime
        from datetime import datetime, date
        import pandas as pd

        today = date.today().strftime("%Y-%m-%d")
        hour = datetime.now().hour
        prompt_temp = f"""
        1- Given an input question, first create a syntactically correct MySQL query to run based on the table schema, then look at the results of the query and return the answer based on the following instructions:  

        Your task is to answer questions related a restaurant called [Shawarma 4 Chicks], the restaurant works everyday, the weekends are on Friday and Saturday.
        Do the necessary analysis to answer, do the necessary aggregations and calculations to answer the questions.
        Today's date is {today}, the current hour is {hour}.
        
        2- Tables Schemas and description:

        - "orders_gpt": Sales orders table, contains the following columns:
                - date:date of the order created. (Primary Key)
                - hour: date of the order created. (Primary Key)
                - day_name: day name of the date. (Primary Key)
                - is_weekend: is the order on the weekend or not. (Primary Key)
                - month: month of year. (Primary Key)
                - year: year. (Primary Key)
                - type: type of order, can be one of the following: [Dine In, Pick Up, Delivery, Drive Thru]. (Primary Key)
                - source: source of order, can be one of the following: [Cashier, API, Call Center]. (Primary Key)
                - cashflow: cash flow on the specified date and hour in Jordanian Dinars or JD.

        3- Use the following format:
        - Question: "Question here"
        - SQLQuery: "SQL Query to run"
        - SQLResult: "Result of the SQLQuery"
        - Answer: "Final answer here"
        """

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
