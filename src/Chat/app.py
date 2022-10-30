import json

from common_function import get_bot_intents, get_response_message_from_bot


def lambda_handler(event, context):
    payload = json.loads(event.get('body'))

    return {
        "statusCode": 200,
        "headers": {
            "content-type": "application/json",
        },
        "body": json.dumps({
            "data": get_response_message_from_bot(session_id=payload.get('session_id'), text=payload.get('text'))
        }),
    }
