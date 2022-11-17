import json

from common_function import create_session_feedback


def lambda_handler(event, context):
    payload = json.loads(event.get('body'))

    return {
        "statusCode": 200,
        "headers": {
            "content-type": "application/json",
            "Access-Control-Allow-Origin": '*'
        },
        "body": json.dumps({
            "data": create_session_feedback(session_id=payload.get('session_id'), is_helpful=payload.get('is_helpful'))
        }),
    }
