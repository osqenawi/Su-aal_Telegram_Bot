"""../bot/handlers/message_handlers.py"""

from functools import partial
from types import SimpleNamespace
from typing import Type

from telethon import events
from telethon.tl.custom.message import Message

from bot.conversation_flow import ConversationFlow
from bot.services.dynamodb_constants import (
    DynamoDBAttributes,
    DynamoDBFormatter,
    DynamoDBGSI1QuestionStatusValues,
    DynamoDBKeySchema,
)
from bot.services.dynamodb_crud_manager import DynamoDBCrudManager


def initialize_text_messege_handler(
    conversation_flow: Type[ConversationFlow],
    dynamodb_crud_manager: DynamoDBCrudManager,
) -> partial:
    """Initializes the text message handler."""
    handler = partial(
        handle_text_message,
        conversation_flow=conversation_flow,
        dynamodb_crud_manager=dynamodb_crud_manager,
    )
    return events.register(events.NewMessage())(handler)


async def handle_text_message(
    event: events.NewMessage.Event,
    dynamodb_crud_manager: DynamoDBCrudManager,
    conversation_flow: Type[ConversationFlow],
):
    """Handle text messages."""

    if event.is_reply:
        dest_question_message = await event.get_reply_message()
        await handle_reply(
            event=event,
            dest_question_message=dest_question_message,
            answer=event.message,
            dynamodb_crud_manager=dynamodb_crud_manager,
        )
    else:
        if not event.is_private:
            return

        user_id = str(event.sender.id)
        async with conversation_flow(
            user_id=user_id,
            dynamodb_crud_manager=dynamodb_crud_manager,
            telethon_event=event,
        ) as conversation:
            await conversation.trigger_next_state()


# async def handle_reply(
#     event: events.NewMessage.Event,
#     dest_question_message: Message,
#     answer: Message,
#     dynamodb_crud_manager: DynamoDBCrudManager,
# ):
#     """Handle reply messages."""
#     dest_question_message_id = dest_question_message.id
#     dest_chat_id = dest_question_message.chat_id

#     source_chat_gsi1_pk = DynamoDBFormatter.prefix_dest_chat_gsi2_pk(
#         dest_chat_id=str(dest_chat_id),
#     )
#     dest_question_message_gsi2_pk = DynamoDBFormatter.prefix_dest_message_gsi2_sk(
#         dest_message_id=str(dest_question_message_id),
#     )

#     items = await dynamodb_crud_manager.get_items_from_index(
#         DynamoDBKeySchema.INDEX_GSI2_PK_GSI2_SK.value,
#         pk=source_chat_gsi1_pk,
#         sk=dest_question_message_gsi2_pk,
#     )
#     if not items:
#         return

#     question = items[0]
#     user_id = question[DynamoDBAttributes.USER_ID.value]
#     question_id = question[DynamoDBAttributes.QUESTION_ID.value]
#     dest_answer = await event.client.send_message(
#         entity=int(user_id),
#         message=answer,
#         reply_to=int(question_id),
#     )
#     question[DynamoDBAttributes.QUESTION_STATUS.value] = (
#         DynamoDBGSI1QuestionStatusValues.ANSWERED.value
#     )
#     question[DynamoDBKeySchema.GSI1_PK.value] = (
#         DynamoDBFormatter.prefix_question_status_gsi1_pk(
#             status=DynamoDBGSI1QuestionStatusValues.ANSWERED.value
#         )
#     )

#     sender = await answer.get_sender() or SimpleNamespace(
#         username="مخفي", first_name="مخفي", last_name=""
#     )

#     answer_data = {
#         "Text": answer.text,
#         "SrcMsgId": answer.id,
#         "DestMsgId": dest_answer.id,
#         "SrcChatId": answer.chat_id,
#         "SenderId": answer.sender_id,
#         "Date": answer.date.isoformat(),  # type: ignore
#         "Username": sender.username,  # type: ignore
#         "FirstName": sender.first_name,  # type: ignore
#         "LastName": sender.last_name,  # type: ignore
#         "TopicId": answer.reply_to.reply_to_top_id,  # type: ignore
#     }
#     if question.get(DynamoDBAttributes.ANSWERS.value) is None:
#         question[DynamoDBAttributes.ANSWERS.value] = [answer_data]
#     else:
#         question[DynamoDBAttributes.ANSWERS.value].append(answer_data)

#     answered_value = DynamoDBGSI1QuestionStatusValues.ANSWERED.value
#     non_answered_value = DynamoDBGSI1QuestionStatusValues.NON_ANSWERED.value
#     if answered_value in dest_question_message.text:  # type: ignore
#         dest_question_message_text = dest_question_message.text.replace(answered_value, answered_value * 2, 1)  # type: ignore
#     else:
#         dest_question_message_text = dest_question_message.text.replace(non_answered_value, answered_value)  # type: ignore
#     await event.client.edit_message(
#         entity=int(dest_chat_id),  # type: ignore
#         message=int(dest_question_message_id),
#         text=dest_question_message_text,
#     )
#     await dynamodb_crud_manager.put_item(item=question)



async def handle_reply(
    event: events.NewMessage.Event,
    dest_question_message: Message,
    answer: Message,
    dynamodb_crud_manager: DynamoDBCrudManager,
):
    """Handle reply messages."""
    dest_question_message_id = dest_question_message.id
    dest_chat_id = dest_question_message.chat_id

    source_chat_gsi1_pk = DynamoDBFormatter.prefix_dest_chat_gsi2_pk(
        dest_chat_id=str(dest_chat_id),
    )
    dest_question_message_gsi2_pk = DynamoDBFormatter.prefix_dest_message_gsi2_sk(
        dest_message_id=str(dest_question_message_id),
    )

    items = await dynamodb_crud_manager.get_items_from_index(
        DynamoDBKeySchema.INDEX_GSI2_PK_GSI2_SK.value,
        pk=source_chat_gsi1_pk,
        sk=dest_question_message_gsi2_pk,
    )
    if not items:
        return

    question = items[0]
    user_id = question[DynamoDBAttributes.USER_ID.value]
    question_id = question[DynamoDBAttributes.QUESTION_ID.value]
    dest_answer = await event.client.send_message(
        entity=int(user_id),
        message=answer,
        reply_to=int(question_id),
    )
    question[DynamoDBAttributes.QUESTION_STATUS.value] = (
        DynamoDBGSI1QuestionStatusValues.ANSWERED.value
    )
    question[DynamoDBKeySchema.GSI1_PK.value] = (
        DynamoDBFormatter.prefix_question_status_gsi1_pk(
            status=DynamoDBGSI1QuestionStatusValues.ANSWERED.value
        )
    )

    sender = await answer.get_sender() or SimpleNamespace(
        username="مخفي", first_name="مخفي", last_name=""
    )

    answer_data = {
        "Text": answer.text,
        "SrcMsgId": answer.id,
        "DestMsgId": dest_answer.id,
        "SrcChatId": answer.chat_id,
        "SenderId": answer.sender_id,
        "Date": answer.date.isoformat(),  # type: ignore
        "Username": sender.username,  # type: ignore
        "FirstName": sender.first_name,  # type: ignore
        "LastName": sender.last_name,  # type: ignore
        "TopicId": answer.reply_to.reply_to_top_id,  # type: ignore
    }
    if question.get(DynamoDBAttributes.ANSWERS.value) is None:
        question[DynamoDBAttributes.ANSWERS.value] = [answer_data]
    else:
        question[DynamoDBAttributes.ANSWERS.value].append(answer_data)

    answered_value = DynamoDBGSI1QuestionStatusValues.ANSWERED.value
    non_answered_value = DynamoDBGSI1QuestionStatusValues.NON_ANSWERED.value
    if answered_value in dest_question_message.text:  # type: ignore
        dest_question_message_text = dest_question_message.text.replace(answered_value, answered_value * 2, 1)  # type: ignore
    else:
        dest_question_message_text = dest_question_message.text.replace(non_answered_value, answered_value)  # type: ignore
    await event.client.edit_message(
        entity=int(dest_chat_id),  # type: ignore
        message=int(dest_question_message_id),
        text=dest_question_message_text,
    )
    await dynamodb_crud_manager.put_item(item=question)