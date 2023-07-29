from bot.config import config
from telethon.sync import TelegramClient


user_client = TelegramClient(config['user_session_file'], config['api_id'], config['api_hash'])
bot_client = TelegramClient(config['bot_session_file'], config['api_id'], config['api_hash'])
