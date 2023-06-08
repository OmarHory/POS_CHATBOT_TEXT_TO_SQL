config_business = dict(
    business_type="",
    business_name="",
    business_branches="",
    business_country="",
    business_categories="",
    business_timezone="",
    business_currency_full="",
    business_currency_short="",
    business_order_types="",
    business_order_sources="",
    business_order_statuses="",
)

redis_config = dict(
    redis_host="",
    redis_port=6379,
    redis_db=1,
    redis_timeout=86400,
    redis_otp_timeout=300,
)

config_mysql = dict(
    mysql_user="",
    mysql_password="",
    mysql_host="localhost",
    mysql_port="3306",
    mysql_raise_on_warnings=True,
    mysql_pool_timeout=None,
    mysql_pool_size=5,
)

config_databases = dict(mysql_db_users="", mysql_db_data="", mysql_db_log="")

config_aws = dict(
    aws_access_key="", aws_secret_access_key="", aws_bucket_name="", aws_folder_name=""
)


config_twilio = dict(
    twilio_account_sid="",
    twilio_auth_token="",
    twilio_phone_number="",
)


config_gpt = dict(
    llm_api_key="",
    llm_name="",
    llm_temperature=0.1,
    llm_max_tokens=400,
    llm_request_timeout=120,
)

config_gpt_sqlchemy = dict(
    sqlchemy_database="mysql://{}:{}@{}:{}/{}",
    sqlchemy_include_tables=[
        "branches",
        "categories",
        "products",
        "order_header",
        "order_details",
    ],
)
