from gpt_api import send_to_gpt
from helpers.vars import (
    general_menu,
    intent_prompt,
    sorry_instruction,
    language_map,
    translate_ar_prompt_,
    sorry_words,
)

from helpers.utils import edit_response, edit_prompt, get_formatted_intent, translate_message
from helpers.DatabaseChain import get_db_session
from langchain.prompts.prompt import PromptTemplate
from helpers.vars import gpt_sql_prompt
import time


def prepare_response(
    incoming_msg,
    username,
    phone_number,
    redis_client,
    redis_config,
    llm,
    gpt_sql_engine,
    include_tables,
):
    if not bool(redis_client.hexists(phone_number, "context")):
        user_context = "first_time_user"
    else:
        user_context = redis_client.hget(phone_number, "context").decode("utf-8")

    (
        message,
        updated_context,
        message_type,
        error_flag,
        error_description,
        edited_intent,
        sql_cmd,
        sql_result,
        is_gpt_answer,
    ) = process_message(
        incoming_msg=incoming_msg,
        user_context=user_context,
        username=username,
        llm=llm,
        gpt_sql_engine=gpt_sql_engine,
        include_tables=include_tables,
    )

    redis_client.hset(phone_number, "context", updated_context)
    redis_client.expire(phone_number, redis_config["redis_timeout"])

    return (
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
    incoming_msg,
    user_context,
    username,
    llm,
    gpt_sql_engine,
    include_tables,
):
    message_type = None
    error_flag = False
    error_description = None
    sql_cmd = None
    sql_result = None
    is_gpt_answer = False

    incoming_msg, user_language = translate_message(incoming_msg, language_map, translate_ar_prompt_)
    incoming_msg = incoming_msg.strip(".").strip('"').strip("'").strip(" ")

    if incoming_msg.lower() in ["menu", "exit"] or incoming_msg.isdigit():
        intent = "user_input"
    else:
        intent_prompt_ = intent_prompt.replace("{prompt}", incoming_msg)
        intent = send_to_gpt(intent_prompt_).strip(".").strip('"').strip("'").strip(" ")
        intent = intent.lower()
    print("intent is:", intent)

    edited_intent = get_formatted_intent(intent=intent)

    response = ""
    if "greeting" in intent:
        response = general_menu.format(username)

    elif "farewell" in intent:
        response = "Thank you {username}! Have a nice day! \U0001F44B \U0001F44B\n"

    else:
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
                edited_intent,
                gpt_sql_engine,
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
            )

    print()
    print(incoming_msg)
    print(response)
    print()

    return (
        edit_response(response),
        user_context,
        message_type,
        error_flag,
        error_description,
        edited_intent,
        sql_cmd,
        sql_result,
        is_gpt_answer,
    )


def process_send_gpt(
    edited_intent,
    gpt_sql_engine,
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
        input_variables=["input"],
        template=gpt_sql_prompt(user_language))
        db_chain_session = get_db_session(
            gpt_sql_engine, include_tables, llm, PROMPT_SQL
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

        # response_with_context = f'\n\nUser Question: {incoming_msg}\n\nResponse: {response}'

        # second_response = get_general_report()

        # final_response = predefined_report_prompt + '\n\nFirst Text:'+ response_with_context + '\nSecond Text:\n' + second_response
        # print('final_response: ', final_response)

        # response = f'\nIntent: {edited_intent}\n\n' + send_to_gpt(edit_prompt(final_response) + '\n')
        # print(final_response)

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
