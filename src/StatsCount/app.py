import json

from stats import get_count_stats


def lambda_handler(event, context):

    return {
        "statusCode": 200,
        "headers": {
            "content-type": "application/json",
            "Access-Control-Allow-Origin": '*'
        },
        "body": json.dumps({
            "data": get_count_stats()
        }),
    }
