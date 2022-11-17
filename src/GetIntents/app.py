import json

from common_function import get_bot_intents, get_intent_info


def lambda_handler(event, context):
    path_parameters = event.get("pathParameters") or dict()
    if intent_id := path_parameters.get('intent_id'):
        return {
            "statusCode": 200,
            "headers": {
                "content-type": "application/json",
                "Access-Control-Allow-Origin": '*'
            },
            "body": json.dumps({
                "data": get_intent_info(intent_id)
            }),
        }

    return {
        "statusCode": 200,
        "headers": {
            "content-type": "application/json",
            "Access-Control-Allow-Origin": '*'
        },
        "body": json.dumps({
            "data": get_bot_intents()
        }),
    }
