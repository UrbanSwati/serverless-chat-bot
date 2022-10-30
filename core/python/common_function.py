import time
from typing import List

import boto3 as boto3

from configuration import config
from models import Intent, IntentInfo, CreateIntent

model_client = boto3.client('lexv2-models')
bot_runtime = boto3.client('lexv2-runtime')


def get_bot_version_latest_version() -> str:
    data = model_client.list_bot_versions(botId=config.bot_id)
    bot_version_summaries = data.get('botVersionSummaries')
    return sorted(list(
        filter(lambda d: d.get('botVersion', '').isnumeric() and d.get('botSatus', 'NOPE') == "Available",
               bot_version_summaries)),
        key=lambda d: d.get('creationDateTime'), reverse=True)[0].get('botVersion')


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


def _build_bot_locale():
    resp = model_client.build_bot_locale(
        botId=config.bot_id,
        botVersion='DRAFT',
        localeId=config.locale_Id
    )
    return resp


def _create_bot_version():
    resp = model_client.create_bot_version(
        botId=config.bot_id,
        description='Version update',
        botVersionLocaleSpecification={
            config.locale_Id: {
                'sourceBotVersion': "DRAFT"
            }
        }
    )
    # print("_create_bot_version")
    # print(resp)
    return resp


def _update_to_latest_alias():
    model_client.update_bot_alias(
        botAliasId=config.bot_alias_id,
        botAliasName='latest',
        botVersion=get_bot_version_latest_version(),
        sentimentAnalysisSettings={
            'detectSentiment': False
        },
        botId=config.bot_id
    )


def build_and_deploy():
    # FIXME: update to handle events or move to hidden lambda functions :(
    _build_bot_locale()
    time.sleep(1.5)
    _create_bot_version()
    time.sleep(1.5)
    _update_to_latest_alias()
    time.sleep(1.5)


def create_intent(intent_info: CreateIntent):
    create_intent_response = model_client.create_intent(
        intentName=intent_info.name,
        description=intent_info.description,
        botId=config.bot_id,
        botVersion='DRAFT',
        localeId=config.locale_Id,
        sampleUtterances=[{'utterance': utterance_text} for utterance_text in intent_info.utterances],
        initialResponseSetting={
            'initialResponse': {
                'messageGroups': [
                    {
                        'message': {
                            'plainTextMessage': {
                                'value': intent_info.response_message
                            }
                        }
                    },
                ],
                'allowInterrupt': True
            }
        }
    )
    build_and_deploy()


def delete_intent(intent_id: str):
    model_client.delete_intent(
        intentId=intent_id,
        botId=config.bot_id,
        botVersion='DRAFT',
        localeId=config.locale_Id
    )
    build_and_deploy()
