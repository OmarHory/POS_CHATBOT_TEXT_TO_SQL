config_business = dict(

    business_name="Shawarma 4 Chicks",
    # business_address="1234 Main Street, Anytown, USA",
    # business_phone_number="+1 123-456-7890",
    # business_email="info@lexchicks",

)

redis_config = dict(host="localhost", port=6379, db=1, timeout=86400, otp_timeout=300)

config_mysql = dict(
    user="chicks_mysql",
    password="Sqlchickspassword@97",
    host="localhost",
    port="3306",
    raise_on_warnings=True,
    pool_timeout=None,
    pool_size=5,
)

config_databases = dict(
    users="chicks_users", data="chicks_data", log="chicks_log"
)

#config_aws = dict(access_key='AKIAWQV573E5NJ6IB2XR', secret_access_key = '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', bucket_name='lexchicks')


config_twilio = dict(
    account_sid="ACf3c95d5cac6bde8f4cade4ddcab27e1d",
    auth_token="9e4adfb56f4f7131fa9f48e5381916b2",
    twilio_phone_number="whatsapp:+14346036659",
    avocado_robot_image="https://i.ibb.co/ZGyZ0Gz/avocado-robot.png",
    avocado_smile_image="https://i.ibb.co/FXMQfm6/smile-avocado.png",
)


config_gpt = dict(
    api_key="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",
    model_name="gpt-3.5-turbo",
    temperature=0.0,
    max_tokens=300,
    request_timeout=120,
)  # gpt-3.5-turbo	$0.002 / 1K tokens

# mysql 'mysql://chicks_mysql:Sqlchickspassword%4097@localhost:3306/chicks_data'
config_gpt_sqlchemy = dict(
    database="mysql://{}:{}@{}:{}/{}",
    include_tables=[
        "orders_gpt",
    ],
)
