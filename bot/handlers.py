from enum import Enum, auto

from telethon import events, Button

from utils.function_refs import make_ref
from .models import flow_steps, Student
from .enums import States


# Obtain the handlers' references to be passed to client.add_event_handler in the main.py file.
handlers = []



@make_ref(handlers)
@events.register(events.NewMessage(pattern='/start'))
async def start_handler(event):
    user_id = event.sender_id
    
    # await event.respond(
    #     "حياكم الله، يمكنكم إرسال الأسئلة إلى اللجنة العلمية عن طريق هذا البوت، تفضل باختيار القسم الذي يتعلق به السؤال.",
    #     buttons=[
    #         [create_inline_button("القسم الشرعي", "option_1"), create_inline_button("القسم الثقافي", "option_2")]
    #     ]
    # )



@make_ref(handlers)
@events.register(events.NewMessage(incoming=True))
async def message_handler(event):
    pass


@make_ref(handlers)
@events.register(events.CallbackQuery(pattern=b"sub_sub_option_\d"))
async def sub_sub_option_handler(event):
    user_id = event.sender_id
    selected_option = event.data.decode()

    # if selected_option == 'sub_sub_option_1':
    #     await event.edit(
    #         "من فضلك قم بإرسال اسم السلسلة"
    #     )
    #     user_states[user_id] = 4
    # elif selected_option == 'sub_sub_option_2':
    #     await event.edit(
    #         "من فضلك قم بإرسال اسم الكتاب"
    #     )
    #     user_states[user_id] = 5
    # raise events.StopPropagation