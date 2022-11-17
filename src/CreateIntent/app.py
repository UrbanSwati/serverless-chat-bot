import json

from common_function import create_intent
from models import CreateIntent


def lambda_handler(event, context):
    payload = json.loads(event.get('body'))
    intent_data = CreateIntent(**payload)
    create_intent(intent_data)
    return {
        "statusCode": 200,
        "headers": {
            "content-type": "application/json",
            "Access-Control-Allow-Origin": '*'
        },
        "body": json.dumps({
            "data": "Successfully created Intent"
        }),
    }
