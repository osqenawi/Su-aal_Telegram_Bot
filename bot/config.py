import os
from dotenv import load_dotenv


load_dotenv()

BOT_SESSION_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "bot.session")
USER_SESSION_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "user.session")

config = {
    "api_id": int(os.environ['API_ID']),
    "api_hash": os.environ['API_HASH'],
    "bot_token": os.environ['BOT_TOKEN'],
    "phone_number": os.environ['PHONE_NUMBER'],
    "bot_session_file": BOT_SESSION_PATH,
    "user_session_file": USER_SESSION_PATH
}
