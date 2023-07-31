from telethon import events
from utils.function_refs import make_ref
import boto3
import random
import time


# Obtain the handlers' references to be passed to client.add_event_handler in the main.py file.
handlers = []


@make_ref(handlers)
@events.register(events.NewMessage(pattern='/start'))
async def handle_start_command(event):
    # Respond with "bot is running" when the user sends "/start"
    result = await event.respond("bot is running")
    print(result)

# @events.register(events.Raw)
# async def handle_start_command(event):
#     # Respond with "bot is running" when the user sends "/start"
#     # await event.respond("bot is running")
#     print(event)
#id=6699

@make_ref(handlers)
@events.register(events.NewMessage)
async def handle_forwarded_messages(event):
    await event.respond(f'next number is: {random.randint(0, 99999999)}')