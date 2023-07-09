import openai
from src.config import config_gpt
import tiktoken


def send_to_gpt(prompt, model_name=None, temperature=None, max_tokens=None, request_timeout=None):
    try:
        openai.api_key = config_gpt["llm_api_key"]

        if model_name is None:
            model_name = config_gpt["llm_name"]
        
        if temperature is None:
            temperature = config_gpt["llm_temperature"]
        
        if max_tokens is None:
            max_tokens = config_gpt["llm_max_tokens"]

        if request_timeout is None:
            request_timeout = config_gpt["llm_request_timeout"]


        completion = openai.ChatCompletion.create(
            temperature=temperature,
            request_timeout=request_timeout,
            max_tokens=max_tokens,
            model=model_name,
            messages=[{"role": "user", "content": prompt}],
        )
        if completion.choices[0].message != None:
            return completion.choices[0].message.content

        else:
            return "Failed to Generate response!"

    except Exception as e:
        print(e)
        return "Error has occured!, please try again in a few minutes."


def num_tokens_from_messages(messages, model="gpt-3.5-turbo-0301"):
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        encoding = tiktoken.get_encoding("cl100k_base")
    if model == "gpt-3.5-turbo-0301":  # note: future models may deviate from this
        num_tokens = 0
        for message in messages:
            num_tokens += (
                4  # every message follows <im_start>{role/name}\n{content}<im_end>\n
            )
            for key, value in message.items():
                num_tokens += len(encoding.encode(value))
                if key == "name":  # if there's a name, the role is omitted
                    num_tokens += -1  # role is always required and always 1 token
        num_tokens += 2  # every reply is primed with <im_start>assistant
        return num_tokens
    else:
        raise NotImplementedError(
            f"""num_tokens_from_messages() is not presently implemented for model {model}"""
        )
