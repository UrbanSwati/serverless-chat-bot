import time
from typing import List

import boto3 as boto3

from configuration import config, engine
from models import Intent, IntentInfo, CreateIntent
from sql_queries import insert_chat_record, insert_feedback

model_client = boto3.client('lexv2-models')
bot_runtime = boto3.client('lexv2-runtime')


def version_check(data: dict, status_check: bool = False) -> bool:
    if status_check:
        return data.get('botVersion', '').isnumeric() and data.get('botStatus', 'NOPE') == "Available"
    return data.get('botVersion', '').isnumeric()


def get_bot_version_latest_version(status_check: bool = False) -> str:
    data = model_client.list_bot_versions(botId=config.bot_id)
    bot_version_summaries = data.get('botVersionSummaries')
    # print(f"Bot versions: {bot_version_summaries}")
    return sorted(list(
        filter(lambda d: version_check(d, status_check),
               bot_version_summaries)),
        key=lambda d: d.get('creationDateTime'), reverse=True)[0].get('botVersion')


def get_bot_intents() -> List[dict]:
    response = model_client.list_intents(
        botId=config.bot_id,
        botVersion=get_bot_version_latest_version(status_check=True),
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
        botVersion=get_bot_version_latest_version(status_check=True),
        localeId=config.locale_Id
    )

    utterances = list(map(lambda sample: sample.get('utterance'), data.get('sampleUtterances', [])))
    message_groups = data.get('initialResponseSetting', dict()).get('initialResponse', dict()).get('messageGroups', [])

    response_message = ""
    if len(message_groups) == 1:
        response_message = message_groups[0].get('message', dict()).get('plainTextMessage', dict()).get('value', '')

    return IntentInfo(utterances=utterances, response_message=response_message).dict()


def get_response_message_from_bot(session_id: str, text_msg: str) -> str:
    # bot_response = "Sorry, something wrong happened, can you please repeat?"
    try:
        bot_response = _recognize_text(session_id, text_msg, config.bot_alias_id)
    except Exception as ex:
        print(f"Failed to send text, sending previous version model: {ex}")
        bot_response = _recognize_text(session_id, text_msg, config.bot_previous_alias_id)

    with engine.connect() as conn:
        insert_chat_record(conn, text_msg, bot_response, session_id)

    return bot_response


def create_session_feedback(session_id: str, is_helpful: bool):
    with engine.connect() as conn:
        insert_feedback(conn, session_id, is_helpful)
    return "Feedback created."


def _recognize_text(session_id, text, bot_alias_id):
    resp = bot_runtime.recognize_text(
        botId=config.bot_id,
        botAliasId=bot_alias_id,
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


def _update_alias_version(alias_id: str, alias_name: str, bot_version: str):
    print(f"Updating bot alias, alias_name={alias_name}, bot_version={bot_version}")
    model_client.update_bot_alias(
        botAliasId=alias_id,
        botAliasName=alias_name,
        botVersion=bot_version,
        botAliasLocaleSettings={
            config.locale_Id: {
                'enabled': True
            }
        },
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
    bot_version = get_bot_version_latest_version()

    _update_alias_version(config.bot_alias_id, 'latest', bot_version)
    _update_alias_version(config.bot_previous_alias_id, 'previous', str(int(bot_version) - 1))
    time.sleep(2)


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


def update_intent(intent_info: CreateIntent, intent_id: str):
    model_client.update_intent(
        intentId=intent_id,
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
    return "Successfully deleted intent"
