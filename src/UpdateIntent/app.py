import json

from common_function import update_intent
from models import CreateIntent


def lambda_handler(event, context):
    payload = json.loads(event.get('body'))
    path_parameters = event.get("pathParameters") or dict()
    intent_id = path_parameters.get('intent_id')

    intent_data = CreateIntent(**payload)
    update_intent(intent_data, intent_id)
    return {
        "statusCode": 200,
        "headers": {
            "content-type": "application/json",
            "Access-Control-Allow-Origin": '*'
        },
        "body": json.dumps({
            "data": "Successfully updated Intent"
        }),
    }
