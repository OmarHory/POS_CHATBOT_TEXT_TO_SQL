import src.update_variables
from src.update_variables import update_keys

#bd
from src.DatabaseChain import get_db_session
from src.helpers.vars import gpt_sql_prompt
from langchain.prompts.prompt import PromptTemplate



import os
import logging
import warnings
import datetime
import time

from src.helpers.utils import redis_hash_get_or_create

from flask import Flask, request
import redis

# config
from src.config import (
    redis_config,
    config_mysql,
    config_gpt,
    config_twilio,
    config_client,
)

# Initialize the engines
from src.repositories.user_repository import UserRepository
from src.repositories.client_user_repository import ClientUserRepository
from src.repositories.log_repository import UserActivityRepository
from src.repositories.client_repository import ClientRepository

from src.response_builder import prepare_response

# sqlalchemy
from sqlalchemy import create_engine

# langchain
from langchain.chat_models import ChatOpenAI

# twilio
from twilio.rest import Client

# audio
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
    host=redis_config["redis_host"],
    port=redis_config["redis_port"],
    db=redis_config["redis_db"],
)

# SQL Chaining
sql_engine = create_engine(
    config_mysql["DATABASE_URI"],
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
    # max_tokens=config_gpt["llm_max_tokens"],
    temperature=config_gpt["llm_temperature"],
)

app = Flask(__name__)

model = whisper.load_model("base")

# repos

user_repo = UserRepository(sql_engine)
client_user_repo = ClientUserRepository(sql_engine)
client_repo = ClientRepository(sql_engine)
log_repo = UserActivityRepository(sql_engine)

@app.route("/test", methods=["POST"])
def test():
    incoming_msg = request.values.get("Body", "")
    client_branches = request.form.get("client_branches")
    client_type = request.form.get("client_type")
    client_name = request.form.get("client_name")
    client_currency_full = request.form.get("client_currency_full")
    client_currency_short = request.form.get("client_currency_short")
    client_country = request.form.get("client_country")
    client_timezone = request.form.get("client_timezone")
    client_categories = request.form.get("client_categories")
    client_order_types = request.form.get("client_order_types")
    client_order_sources = request.form.get("client_order_sources")
    client_order_statuses = request.form.get("client_order_statuses")
    client_id = int(request.form.get("client_id"))
    user_language = request.form.get("user_language")
    include_tables = request.form.get("include_tables")

    PROMPT_SQL = PromptTemplate(
            input_variables=["input"],
            template=gpt_sql_prompt(
                user_language=user_language,
                client_branches=client_branches,
                client_type=client_type,
                client_name=client_name,
                client_currency_full=client_currency_full,
                client_currency_short=client_currency_short,
                client_country=client_country,
                client_timezone=client_timezone,
                client_categories=client_categories,
                client_order_types=client_order_types,
                client_order_sources=client_order_sources,
                client_order_statuses=client_order_statuses,
                client_id=client_id,
            ),
        );
    db_chain_session = get_db_session(sql_engine, eval(include_tables), llm, PROMPT_SQL, {"user_question": incoming_msg, "active_client": client_id, "test":True})
    sql_cmd = db_chain_session(incoming_msg)
    sql_cmd = sql_cmd['intermediate_steps'][0]
    print("sql_cmd", sql_cmd)
    return sql_cmd


@app.route("/bot", methods=["POST"])
def bot():
    request_timestamp = time.time()
    print(request_timestamp)
    request_timestamp_utc = datetime.datetime.utcnow()
    print(request_timestamp_utc)

    phone_number = request.form.get("From").split("+")[1]

    user = user_repo.get_user_by_phone_number(phone_number)
    client_user = client_user_repo.get_by_user_id(user_id=user.id).all()

    recording_url = request.form.get("MediaUrl0")
    if recording_url:
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
        input_type = "audio"
    else:
        print("in text")
        input_type = "text"
        incoming_msg = request.values.get("Body", "")
    print(incoming_msg)

    username = user.name

    if client_user is not None:
        available_client_ids = []
        for observation in client_user:
            available_client_ids.append(observation.client_id)
        available_client_ids = sorted(available_client_ids)

        print("######################")
        print(available_client_ids)
        print("##########################")

    else:
        message = "You have reached a restricted area, please contact the administration to get access to this bot."

    if username is None:
        message = "You have reached a restricted area, please contact the administration to get access to this bot."

    else:
        if bool(redis_client.hexists(phone_number, "active_client")):
            active_client_id = int(
                redis_client.hget(phone_number, "active_client").decode("utf-8")
            )

        else:
            active_client_id = client_repo.fetch_client(available_client_ids[0]).id

        active_client = client_repo.fetch_client(active_client_id)

        config_client = redis_hash_get_or_create(
            redis_client,
            f"client_{active_client_id}",
            active_client.settings,
            redis_config["redis_timeout"],
        )
        print(config_client)
        (
            active_client_id,
            message,
            message_type,
            error_flag,
            error_description,
            edited_intent,
            sql_cmd,
            sql_result,
            is_gpt_answer,
        ) = prepare_response(
            available_client_ids=available_client_ids,
            incoming_msg=incoming_msg,
            phone_number=phone_number,
            redis_client=redis_client,
            redis_config=redis_config,
            username=username,
            llm=llm,
            sql_engine=sql_engine,
            include_tables=config_mysql["include_tables"],
            client_repo=client_repo,
            config_client=config_client,
        )

        response_timestamp = time.time()
        print(response_timestamp)

        response_timestamp_utc = datetime.datetime.utcnow()
        print(response_timestamp_utc)
        print("is_gpt_answer", is_gpt_answer)
        if is_gpt_answer:
            log_repo.insert_user_activity(
                client_id=active_client_id,
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
    print("app_port: ", app_port)
    app.run(host="0.0.0.0", debug=True, port=app_port)
