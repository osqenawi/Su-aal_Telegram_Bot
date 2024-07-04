"""../bot/services/dynamodb_constants.py"""

from enum import Enum


class DynamoDBAttributes(Enum):
    """Defines attributes for the DynamoDB table."""

    USER_ID = "UserId"
    USER_STATE = "UserState"
    USER_INPUTS = "UserInputs"
    DESTINATION_CHAT = "DestinationChat"
    DESTINATION_CHAT_TOPIC = "DestinationChatTopic"
    USER_USERNAME = "UserUsername"
    USER_FIRST_NAME = "UserFirstName"
    USER_LAST_NAME = "UserLastName"
    USER_FULL_NAME = "UserFullName"
    QUESTION_ID = "QuestionId"
    QUESTION_STATUS = "QuestionStatus"
    ANSWERS = "Answers"
    ENTITY_TYPE = "EntityType"


class DynamoDBGSI1QuestionStatusValues(Enum):
    """Defines the possible values for the GSI1 PK attribute related to questions."""

    ANSWERED = "🟢"
    NON_ANSWERED = "🟡"
    DELETED = "❌"


class DynamoDBKeySchema(Enum):
    """Defines the key schema for the DynamoDB table."""

    PK = "PK"
    SK = "SK"
    GSI1_PK = "GSI1_PK"
    GSI1_SK = "GSI1_SK"
    GSI2_PK = "GSI2_PK"
    GSI2_SK = "GSI2_SK"
    INDEX_GSI1_PK_GSI1_SK = "GSI1_PK-GSI1_SK-index"
    INDEX_GSI2_PK_GSI2_SK = "GSI2_PK-GSI2_SK-index"


class DynamoDBKeySchemaPrefix(Enum):
    """Defines the key schema prefixes for the DynamoDB table."""

    USER_PK = "USER#"
    USER_SK = "#USER#"
    QUESTION_SK = "QUESTION#"
    DEST_CHAT_GSI2_PK = "DEST_CHAT#"
    DEST_MESSAGE_GSI2_SK = "DEST_MESSAGE#"
    QUESTION_STATUS_GSI1 = "STATUS#"
    QUESTION_ANSWER_SK = "QUESTION_ANSWER#"
    ANSWER_DEST_MSG_ID_GSI1_PK = "ANSWER_DEST_MSG_ID#"


class DynamoDBFormatter:
    """Provides methods for formatting DynamoDB keys."""

    @staticmethod
    def prefix_user_pk(pk: str) -> str:
        """Adds a prefix to the user primary key."""
        return f"{DynamoDBKeySchemaPrefix.USER_PK.value}{pk}"

    @staticmethod
    def prefix_user_sk(sk: str) -> str:
        """Adds a prefix to the user sort key."""
        return f"{DynamoDBKeySchemaPrefix.USER_SK.value}{sk}"

    @staticmethod
    def prefix_question_sk(question_id: str) -> str:
        """Adds a prefix to the question's sort key."""
        return f"{DynamoDBKeySchemaPrefix.QUESTION_SK.value}{question_id}"

    @staticmethod
    def prefix_dest_chat_gsi2_pk(dest_chat_id: str) -> str:
        """Adds a prefix to the destination chat's GSI2 PK."""
        return f"{DynamoDBKeySchemaPrefix.DEST_CHAT_GSI2_PK.value}{dest_chat_id}"

    @staticmethod
    def prefix_dest_message_gsi2_sk(dest_message_id: str) -> str:
        """Adds a prefix to the destination question message's GSI1 PK."""
        return f"{DynamoDBKeySchemaPrefix.DEST_MESSAGE_GSI2_SK.value}{dest_message_id}"

    @staticmethod
    def prefix_question_status_gsi1_pk(status: str) -> str:
        """Adds a prefix to the question's status GSI1 PK."""
        return f"{DynamoDBKeySchemaPrefix.QUESTION_STATUS_GSI1.value}{status}"

    @staticmethod
    def remove_prefix_question_status_gsi1_pk(text: str) -> str:
        """Removes the prefix from the question's status GSI1 PK."""
        return text.replace(DynamoDBKeySchemaPrefix.QUESTION_STATUS_GSI1.value, "")

    @staticmethod
    def prefix_question_answer_sk(answer_id: str) -> str:
        """Adds a prefix to the question's answer sort key."""
        return f"{DynamoDBKeySchemaPrefix.QUESTION_ANSWER_SK.value}{answer_id}"

    @staticmethod
    def prefix_answer_dest_msg_id_gsi1_pk(dest_message_id: str) -> str:
        """Adds a prefix to the answer's destination message ID GSI1 PK."""
        return f"{DynamoDBKeySchemaPrefix.ANSWER_DEST_MSG_ID_GSI1_PK.value}{dest_message_id}"
