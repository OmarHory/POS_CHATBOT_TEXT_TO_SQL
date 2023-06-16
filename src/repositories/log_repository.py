from sqlalchemy.orm import sessionmaker
import os, sys, datetime
#import models from models/models.py
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(parent_dir)
from models.models import MessageLog

class UserActivityRepository:
    def __init__(self, session):
        self.session = session

    def close_session(self):
        self.session.close()

    def insert_user_activity(self,
    client_id, 
    username,
    phone_number,
    user_intent,
    input,
    output,
    message_type,
    sql_cmd,
    sql_result,
    error_flag,
    error_description,
    request_timestamp,
    response_timestamp,
    time_taken,
    input_type):
        message_log = MessageLog(
            username=username,
            phone_number=phone_number,
            user_intent=user_intent,
            input=input,
            output=output,
            message_type=message_type,
            sql_cmd=sql_cmd,
            sql_result=sql_result,
            error_flag=error_flag,
            error_description=error_description,
            request_timestamp=request_timestamp,
            response_timestamp=response_timestamp,
            time_taken=time_taken,
            input_type=input_type,
            client_id = client_id,
            created_at = datetime.datetime.now()
        )

        self.session.add(message_log)
        self.session.commit()
        self.session.close()
