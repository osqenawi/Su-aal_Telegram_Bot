
from bot import user_client, bot_client, bot_token
from bot.handlers import handlers
from utils.configure_logging import configure_logging
import traceback


# Configure logging
configure_logging()


async def main():
    # Start the client
    await bot_client.start(bot_token=bot_token)
    for handler in handlers:
        bot_client.add_event_handler(handler)
    # Listen for events
    await bot_client.run_until_disconnected()


if __name__ == "__main__":
    try:
        bot_client.loop.run_until_complete(main())
    except (ConnectionError, KeyboardInterrupt):
        print("Client disconnected or user interrupted the execution.")
    except Exception:
        print("An unexpected error occurred:")
        traceback.print_exc()
    finally:
        bot_client.disconnect()