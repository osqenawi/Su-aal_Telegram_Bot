from telethon import events
from utils.function_refs import make_ref


handlers = []


# @make_ref(handlers)
# @events.register(events.NewMessage)
# async def handle_new_message(event):
#     # Respond with "received" when a new message is received
#     await event.respond("received")

@make_ref(handlers)
@events.register(events.NewMessage(pattern='/start'))
async def handle_start_command(event):
    # Respond with "bot is running" when the user sends "/start"
    result = await event.respond("bot is running")
    print(result)
    print(event.id)

# @events.register(events.Raw)
# async def handle_start_command(event):
#     # Respond with "bot is running" when the user sends "/start"
#     # await event.respond("bot is running")
#     print(event)
#id=6699
@make_ref(handlers)
@events.register(events.NewMessage)
async def handle_forwarded_messages(event):
        await event.respond('mohmaaaaaaaaad')