config_client = dict(
    client_id=0,
    client_type="",
    client_name="",
    client_branches="",
    client_country="",
    client_categories="",
    client_timezone="",
    client_currency_full="",
    client_currency_short="",
    client_order_types="",
    client_order_sources="",
    client_order_statuses="",
)

redis_config = dict(
    redis_host="",
    redis_port=6379,
    redis_db=1,
    redis_timeout=86400,
    redis_otp_timeout=300,
)

config_mysql = dict(
    mysql_raise_on_warnings=True,
    mysql_pool_timeout=None,
    mysql_pool_size=5,
    DATABASE_URI="",
    include_tables=[
        "branches",
        "categories",
        "products",
        "order_headers",
        "order_details",
        "order_options",
    ],
)

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
