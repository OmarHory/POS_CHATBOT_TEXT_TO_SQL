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
        import pandas as pd
        today_ = date.today()
        today = today_.strftime("%Y-%m-%d")
        yesterday = (today_ - timedelta(days=1)).strftime("%Y-%m-%d")
        hour = datetime.now().hour


        prompt_temp = f"""
        1- Given an input question, first create a syntactically correct MySQL query to run based on the table schema, then look at the results of the query and return the answer based on the following instructions:  

        Your task is to answer questions related a restaurant called [Shawarma 4 Chicks], the restaurant works everyday, the weekends are on Friday and Saturday.
        Do the necessary analysis to answer, do the necessary aggregations and calculations to answer the questions.
        Today's date is {today}, the current hour is {hour}.
        Return the answer in a readable format, do not return the SQL query, return the answer only.
        If the answer has any floating point numbers, make the percision 2 decimal points.
        Add a thousand separator to the numbers.

        Examples:

        - Question: What is the cash flow yesterday?
        - SQLQuery: SELECT SUM(cashflow) FROM orders_gpt WHERE date = '{yesterday}' GROUP BY date

        - Question: What is the total cash flow on {yesterday} at 9 PM?
        - SQLQuery: SELECT date, hour, SUM(cashflow) FROM orders_gpt WHERE date = '{yesterday}' AND hour = 21 GROUP BY date, hour

        - Question: What is the total cash flow on {yesterday} at 9 AM?
        - SQLQuery: SELECT date, hour, SUM(cashflow) FROM orders_gpt WHERE date = '{yesterday}' AND hour = 9 GROUP BY date, hour

        - Question: What is the cash flow on {yesterday} at 1 PM for Dine In orders?
        - SQLQuery: SELECT date, hour, SUM(cashflow) FROM orders_gpt WHERE date = '{yesterday}' AND hour = 13 AND type = 'Dine In' GROUP BY date, hour, type

        - Question: Compare the total cash flow on {yesterday} at 4 PM for Dine In orders and Pick Up orders?
        - SQLQuery: SELECT date, hour, type, SUM(cashflow) FROM orders_gpt WHERE date = '{yesterday}' and hour = 16 AND (type = 'Dine In' OR type = 'Pick Up') GROUP BY date, hour, type
        
        - Question: Compare the cash flow between April and May in 2023?
        - SQLQuery: SELECT month, year, SUM(cashflow) FROM orders_gpt WHERE month=4 OR month=5 AND year=2023 GROUP BY month, year

        2- Tables Schemas and description:

        - "orders_gpt": Sales orders table, contains the following columns:
                - date: date of the created order. (Primary Key)
                - hour: hour of the created order. (Primary Key)
                - day_name: day name of created order. (Primary Key)
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
        - Answer: "Final answer here in {user_language} only."
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


translate_ar_prompt_ = """Translate the following Arabic (MSA or Dialect) to English:

                        {}"""
language_map = {
    "af": "Afrikaans",
    "ar": "Arabic",
    "bg": "Bulgarian",
    "bn": "Bengali",
    "ca": "Catalan",
    "cs": "Czech",
    "da": "Danish",
    "de": "German",
    "el": "Greek",
    "en": "English",
    "es": "Spanish",
    "et": "Estonian",
    "fi": "Finnish",
    "fr": "French",
    "he": "Hebrew",
    "hi": "Hindi",
    "hr": "Croatian",
    "hu": "Hungarian",
    "id": "Indonesian",
    "it": "Italian",
    "ja": "Japanese",
    "ko": "Korean",
    "lt": "Lithuanian",
    "lv": "Latvian",
    "ms": "Malay",
    "nl": "Dutch",
    "no": "Norwegian",
    "pl": "Polish",
    "pt": "Portuguese",
    "ro": "Romanian",
    "ru": "Russian",
    "sk": "Slovak",
    "sl": "Slovenian",
    "sq": "Albanian",
    "sr": "Serbian",
    "sv": "Swedish",
    "sw": "Swahili",
    "th": "Thai",
    "tl": "Tagalog",
    "tr": "Turkish",
    "uk": "Ukrainian",
    "vi": "Vietnamese",
    "zh-cn": "Chinese (Simplified)",
    "zh-tw": "Chinese (Traditional)"
}
