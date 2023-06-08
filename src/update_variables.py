from config import *
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


def update_keys(config):
    for key in config:
        env_value = os.getenv(key)
        if env_value is not None:
            # Convert environment variable to the appropriate type
            if isinstance(config[key], bool):
                config[key] = env_value.lower() in ["true", "1"]
            elif isinstance(config[key], int):
                config[key] = int(env_value)
            elif isinstance(config[key], float):
                config[key] = float(env_value)
            else:
                config[key] = env_value
    return config


config_gpt = update_keys(config_gpt)
config_twilio = update_keys(config_twilio)
config_aws = update_keys(config_aws)
config_databases = update_keys(config_databases)
config_mysql = update_keys(config_mysql)
config_business = update_keys(config_business)
redis_config = update_keys(redis_config)


print(config_gpt)
print(config_twilio)
print(config_aws)
print(config_databases)
print(config_mysql)
print(config_business)
print(redis_config)
