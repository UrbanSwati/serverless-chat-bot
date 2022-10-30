from typing import List

import boto3 as boto3

from configuration import config
from models import Intent, IntentInfo

model_client = boto3.client('lexv2-models')
bot_runtime = boto3.client('lexv2-runtime')


def get_bot_version_latest_version() -> str:
    data = model_client.list_bot_versions(botId=config.bot_id)
    return sorted(data.get('botVersionSummaries'), key=lambda d: d.get('creationDateTime'), reverse=True)[
        0].get('botVersion')


def get_bot_intents() -> List[dict]:
    response = model_client.list_intents(
        botId=config.bot_id,
        botVersion=get_bot_version_latest_version(),
        localeId=config.locale_Id
    )

    return [Intent(**intent).dict() for intent in
            response.get('intentSummaries')]


def get_intent_info(intent_id: str) -> dict:
    """
    Returns sampleUtterances and responses data of intent
    """
    data = model_client.describe_intent(
        intentId=intent_id,
        botId=config.bot_id,
        botVersion=get_bot_version_latest_version(),
        localeId=config.locale_Id
    )

    utterances = list(map(lambda sample: sample.get('utterance'), data.get('sampleUtterances', [])))
    message_groups = data.get('initialResponseSetting', dict()).get('initialResponse', dict()).get('messageGroups', [])

    response_message = ""
    if len(message_groups) == 1:
        response_message = message_groups[0].get('message', dict()).get('plainTextMessage', dict()).get('value', '')

    return IntentInfo(utterances=utterances, response_message=response_message).dict()


def get_response_message_from_bot(session_id: str, text: str) -> str:
    resp = bot_runtime.recognize_text(
        botId=config.bot_id,
        botAliasId=config.bot_alias_id,
        localeId=config.locale_Id,
        sessionId=session_id,
        text=text
    )

    # FIXME: proper dict access and check
    return resp.get('messages')[0]['content']
