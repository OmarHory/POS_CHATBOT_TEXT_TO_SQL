from gpt_api import send_to_gpt
from helpers.vars import (
    general_menu,
    intent_prompt,
    sorry_instruction,
    language_map,
    translate_ar_prompt_,
    sorry_words,
    farewell,
)

from helpers.utils import (
    edit_response,
    edit_prompt,
    get_formatted_intent,
    translate_message,
    strip_message,
)
from helpers.DatabaseChain import get_db_session
from langchain.prompts.prompt import PromptTemplate
from helpers.vars import gpt_sql_prompt
import time
from update_variables import update_keys


def prepare_response(
    available_client_ids,
    incoming_msg,
    username,
    phone_number,
    redis_client,
    redis_config,
    llm,
    sql_engine,
    include_tables,
    client_repo,
    config_client,
):
    if not bool(redis_client.hexists(phone_number, "context")):
        user_context = "first_time_user"


    if not bool(redis_client.hexists(phone_number, "active_client")):
        active_client_context = available_client_ids[0]
        

    if bool(redis_client.hexists(phone_number, "active_client")) and bool(redis_client.hexists(phone_number, "context")):
        user_context = redis_client.hget(phone_number, "context").decode("utf-8")
        active_client_context = redis_client.hget(phone_number, "active_client").decode("utf-8")

    (
        message,
        updated_context,
        updated_active_client,
        message_type,
        error_flag,
        error_description,
        edited_intent,
        sql_cmd,
        sql_result,
        is_gpt_answer,
    ) = process_message(
        available_client_ids=available_client_ids,
        incoming_msg=incoming_msg,
        user_context=user_context,
        active_client_context=active_client_context,
        username=username,
        llm=llm,
        sql_engine=sql_engine,
        include_tables=include_tables,
        client_repo=client_repo,
        config_client=config_client
    )

    redis_client.hset(phone_number, "context", updated_context)
    redis_client.hset(phone_number, "active_client",updated_active_client)
    redis_client.expire(phone_number, redis_config["redis_timeout"])
    print("$$$$$$$$$$$$$$$$$$$$$")
    print(active_client_context)
    print("$$$$$$$$$$$$$$$$$$$$")
    return (
        active_client_context,
        message,
        message_type,
        error_flag,
        error_description,
        edited_intent,
        sql_cmd,
        sql_result,
        is_gpt_answer,
    )


def process_message(
    available_client_ids,
    incoming_msg,
    user_context,
    active_client_context,
    username,
    llm,
    sql_engine,
    include_tables,
    client_repo,
    config_client,
):
    message_type = None
    error_flag = False
    error_description = None
    sql_cmd = None
    sql_result = None
    is_gpt_answer = False
    intent = None

    def switch_message(available_client_ids, client_repo):
        message = 'You have the following clients:\n'
        i = 1
        for client in available_client_ids:
            client_name = client_repo.fetch_client(client).name
            message += f'{i} - {client_name}\n'
            i += 1
        message += 'Please enter the number of the client you want to switch to:'
        return message

    if strip_message(incoming_msg.lower()) in ["switch", 'تغيير'] or incoming_msg.isdigit():
        intent = "user_input"

    incoming_msg, user_language = translate_message(
        incoming_msg, language_map, translate_ar_prompt_
    )
    incoming_msg = strip_message(incoming_msg)
    
    if intent is None:
        print(config_client)
        intent_prompt_ = intent_prompt(incoming_msg=incoming_msg, client_name=config_client['client_name'], client_type=config_client['client_type'])
        intent = strip_message(send_to_gpt(intent_prompt_))
        intent = intent.lower()
        print(intent_prompt_)
    print("intent is:", intent)

    edited_intent = get_formatted_intent(intent=intent)

    response = ""

    if intent == "user_input":

        if incoming_msg.lower() == 'switch':
            response = switch_message(available_client_ids, client_repo)
            user_context = 'switch_client'
    
        if incoming_msg.isdigit() and user_context == 'switch_client':
            # get the client name from the client id
            active_client_context = available_client_ids[int(incoming_msg) - 1]
            user_context = 'first_time_user'
            client_name = client_repo.fetch_client(int(incoming_msg)).name
            response = f'You have switched to {client_name}'
            

    elif "greeting" in intent:
        response = general_menu(username=username, client_name=config_client['client_name'])

    elif "farewell" in intent:
        response = farewell(username=username)

    else:
        print("FUCKING HEERE")
        (
            response,
            message_type,
            error_flag,
            error_description,
            edited_intent,
            sql_cmd,
            sql_result,
            is_gpt_answer,
        ) = process_send_gpt(
            active_client_context,
            edited_intent,
            sql_engine,
            include_tables,
            llm,
            user_language,
            incoming_msg,
            message_type,
            error_flag,
            error_description,
            sql_cmd,
            sql_result,
            is_gpt_answer,
            config_client,
        )

    print()
    print(incoming_msg)
    print(response)
    print()

    return (
        edit_response(response),
        user_context,
        active_client_context,
        message_type,
        error_flag,
        error_description,
        edited_intent,
        sql_cmd,
        sql_result,
        is_gpt_answer,
    )


def process_send_gpt(
    active_client_context,
    edited_intent,
    sql_engine,
    include_tables,
    llm,
    user_language,
    incoming_msg,
    message_type,
    error_flag,
    error_description,
    sql_cmd,
    sql_result,
    is_gpt_answer,
    config_client
):
    is_gpt_answer = True

    response = send_to_gpt(
        "\nIntent: {edited_intent}\n\n"
        + edit_prompt(sorry_instruction.format(user_language, incoming_msg))
        + "\n"
    )
    print("First GPT response: ", response)

    if (
        any(item in response.lower() for item in sorry_words)
        and "undefined" not in edited_intent.lower()
    ):
        # if "undefined" not in edited_intent.lower():
        print("Go to SQL GPT")
        incoming_msg = edit_prompt(incoming_msg)

        # Record the start time
        start_time = time.time()
        PROMPT_SQL = PromptTemplate(
            input_variables=["input"], template=gpt_sql_prompt(user_language=user_language,client_branches=config_client['client_branches'], client_type=config_client['client_type'], 
                                                               client_name=config_client['client_name'], client_currency_full=config_client['client_currency_full'], 
                                                               client_currency_short=config_client['client_currency_short'], 
                                                               client_country=config_client['client_country'], client_timezone=config_client['client_timezone'],
                                                               client_categories=config_client['client_categories'], client_order_types=config_client['client_order_types'], 
                                                               client_order_sources=config_client['client_order_sources'], client_order_statuses=config_client['client_order_statuses'], 
                                                               client_id=active_client_context))
        db_chain_session = get_db_session(
            sql_engine, include_tables, llm, PROMPT_SQL
        )
        end_time = time.time()
        elapsed_time = end_time - start_time
        print("Time taken for db_session:", elapsed_time, "seconds")
        try:
            dict_response = db_chain_session(incoming_msg)
            response = dict_response["result"]
            sql_dict = dict_response["intermediate_steps"]
            sql_cmd = sql_dict[0]
            sql_result = sql_dict[1]

            message_type = "main_response"

        except Exception as e:
            error_flag = True
            error_description = e

            print("Exception in db_chain_session.run: ", e)
            response = "Thank you for taking the time to ask this question, can you be specific? I am not able to answer your question."
            if "MySQLdb.ProgrammingError" in str(e):
                message_type = "SQL_Syntax_Error"
            elif "MySQLdb.OperationalError" in str(e):
                message_type = "SQL_Operational_Error"
            elif "maximum context length" in str(e):
                message_type = "GPT_Max_Tokens_Error"
            else:
                message_type = "Unrecognized_Error"

    else:
        message_type = "general_gpt_response"

    return (
        response,
        message_type,
        error_flag,
        error_description,
        edited_intent,
        sql_cmd,
        sql_result,
        is_gpt_answer,
    )
