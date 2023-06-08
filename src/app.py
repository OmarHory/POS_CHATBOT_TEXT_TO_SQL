import update_variables

import os
import logging
import warnings
import datetime
import time

from flask import Flask, request
import redis
from config import (
    redis_config,
    config_mysql,
    config_gpt,
    config_gpt_sqlchemy,
    config_twilio,
    config_databases,
)

# Initialize the engines
from models import user, log_message
from models.log_message import log_user_message

from response_builder import prepare_response
from models.user import fetch_user
# from registration import registration_process
from sqlalchemy import create_engine

from langchain.chat_models import ChatOpenAI


from twilio.rest import Client
# from openai import Audio
import requests, io
from pydub import AudioSegment
import tempfile
import whisper

warnings.simplefilter("ignore")
logging.disable(logging.CRITICAL)

# set environment variables
os.environ["OPENAI_API_KEY"] = config_gpt["llm_api_key"]


# redis settings
redis_client = redis.Redis(
    host=redis_config["redis_host"], port=redis_config["redis_port"], db=redis_config["redis_db"]
)

# SQL Chaining
print("SQL Engine created for Database Chaining...")
gpt_sql_engine = create_engine(
    config_gpt_sqlchemy["sqlchemy_database"].format(
        config_mysql["mysql_user"],
        config_mysql["mysql_password"].replace("@", "%40"),
        config_mysql["mysql_host"],
        config_mysql["mysql_port"],
        config_databases["mysql_db_data"],
    ),
    echo=True,
    pool_timeout=config_mysql["mysql_pool_timeout"],
    pool_size=config_mysql["mysql_pool_size"],
)

# twilio settings
account_sid = config_twilio["twilio_account_sid"]
auth_token = config_twilio["twilio_auth_token"]
twilio_phone_number = config_twilio["twilio_phone_number"]
client = Client(account_sid, auth_token)

if not os.environ.get("ENV"):
    os.environ["ENV"] = "dev"

llm = ChatOpenAI(
    model_name=config_gpt["llm_name"],
    request_timeout=config_gpt["llm_request_timeout"],
    max_tokens=config_gpt["llm_max_tokens"],
    temperature=config_gpt["llm_temperature"],
)

app = Flask(__name__)

model = whisper.load_model("base")

@app.route("/bot", methods=["POST"])
def bot():
    request_timestamp = time.time()
    print(request_timestamp)
    request_timestamp_utc = datetime.datetime.utcnow()
    print(request_timestamp_utc)

    recording_url = request.form.get("MediaUrl0")
    if recording_url:
        pass
        print("in audio")
        response = requests.get(recording_url)
        ogg_bytes = response.content
        opus_data = io.BytesIO(ogg_bytes)
        print("Audio Segment from file")
        sound = AudioSegment.from_file(opus_data, codec="opus")
        print("Finished Audio Segment from file")
        pcm_segment = (
            sound.set_sample_width(sound.sample_width)
            .set_channels(sound.channels)
            .set_frame_rate(sound.frame_rate)
        )
        print("Finished PCM Segment from file")
        print("Start Set Directory and writing to temp file")
        # Set the directory for the temporary file
        temp_dir = "temp_dir/"
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)

        # Create a temporary file in the specified directory
        with tempfile.NamedTemporaryFile(
            mode="wb", dir=temp_dir, suffix=".mp3"
        ) as temp_file:
            pcm_segment.export(temp_file.name, format="mp3")
            print("Finished exporting to temp file")
            transcript = model.transcribe(temp_file.name)
            incoming_msg = transcript["text"].strip()
            print("Finish transcribing")
        input_type = 'audio'
    else:
        print("in text")
        input_type = 'text'
        incoming_msg = request.values.get("Body", "")
    print(incoming_msg)

    phone_number = request.form.get("From").split("+")[
        1
    ]  # Specific for twilio whatsapp:+962795704964 to get the phone number only (need to validate this for US users)

    user = fetch_user(phone_number=phone_number)
    print(user)
    if user is None:
        # message = registration_process(phone_number=phone_number,
        #                      incoming_msg=incoming_msg,
        #                      redis_client=redis_client,
        #                      redis_config=redis_config)

        message = "You have reached a restricted area, please contact the administration to get access to this bot."

    else:
        username = user["name"]  # get user_name

        (
            message,
            message_type,
            error_flag,
            error_description,
            edited_intent,
            sql_cmd,
            sql_result,
            is_gpt_answer,
        ) = prepare_response(
            incoming_msg=incoming_msg,
            phone_number=phone_number,
            redis_client=redis_client,
            redis_config=redis_config,
            username=username,
            llm=llm,
            gpt_sql_engine=gpt_sql_engine,
            include_tables=config_gpt_sqlchemy["sqlchemy_include_tables"],
        )

        response_timestamp = time.time()
        print(response_timestamp)

        response_timestamp_utc = datetime.datetime.utcnow()
        print(response_timestamp_utc)
        print("is_gpt_answer", is_gpt_answer)
        if is_gpt_answer:
            log_user_message(
                username=username,
                phone_number=phone_number,
                user_intent=edited_intent,
                input=incoming_msg,
                output=message,
                message_type=message_type,
                sql_cmd=sql_cmd,
                sql_result=sql_result,
                error_flag=error_flag,
                error_description=error_description,
                request_timestamp=request_timestamp_utc,
                response_timestamp=response_timestamp_utc,
                time_taken=response_timestamp - request_timestamp,
                input_type=input_type,
            )

    if os.environ.get("ENV").lower() == "prod":
        try:
            client.messages.create(
                from_=twilio_phone_number,
                to=f"whatsapp:{phone_number}",
                # media_url='data:image/jpeg;base64,' + file_like_obj.getvalue().decode('base64'),
                body=message,
            )
        except Exception as e:
            client.messages.create(
                from_=twilio_phone_number,
                to=f"whatsapp:{phone_number}",
                body="An error has occurred in Twilios message, pleaase try again in a few minutes.",
            )

    end_time = time.time()
    elapsed_time = end_time - request_timestamp
    print("Time taken for EVERYTHING:", elapsed_time, "seconds")

    return message


if __name__ == "__main__":
    app_port = int(os.environ.get("app_port", 4000))
    print('app_port: ', app_port)
    app.run(debug=True, port=app_port)
