import json
from datetime import datetime

from stats import get_user_session_stats


def lambda_handler(event, context):
    try:
        year = event["queryStringParameters"]["year"]
    except Exception as ex:
        print(f"Could not get year: {ex}")
        year = datetime.now().year
    return {
        "statusCode": 200,
        "headers": {
            "content-type": "application/json",
            "Access-Control-Allow-Origin": '*'
        },
        "body": json.dumps({
            "data": get_user_session_stats(year)
        }),
    }
