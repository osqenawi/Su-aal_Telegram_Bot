from enum import Enum


class Student:
    def __init__(self, id: int, name: str, user_name: str, batch: str, current_flow_step: Enum) -> None:
        """
        Initialize a Student object.

        Parameters:
            id (int): The unique identifier for the student.
            name (str): The name of the student.
            user_name (str): The telegram username of the student.
            batch (int): The batch or group to which the student belongs.
            current_flow_step (Enum): The current conversation flow step for the student.

        Returns:
            None

        Example:
            # Create a Student object
            student = Student(id=400, name="Osama Gamal", user_name="@OsamaIs", batch="الدفعة الثالثة", current_flow_step=1)
        """
        self.id = id
        self.name = name
        self.user_name = user_name
        self.batch = batch
        self.current_flow_step = current_flow_step

    def __repr__(self) -> str:
        return f"Student(id={self.id}, name='{self.name}', user_name='{self.user_name}', batch='{self.batch}', state={self.state})"


# Define the conversation flow steps using a dictionary
flow_steps = {
    'START_AND_CHOOSE_BATCH': {
        'input_type': 'button',
        'message': "حيَّ الله من استقى من ينابيع العلم هُدى،\nمن فضلك قم بتحديد الدفعة الخاصة بك",
        'buttons': ['الدفعة الأولى', 'الدفعة الثانية', 'الدفعة الثالثة', 'الدفعة الرابعة']
    },
    'CHOOSE_SECTION': {
        'input_type': 'button',
        'message': "لا تبرح عن ثغرك! واصل على جادة الطريق،\nمن فضلك قم باختيار القسم التي يتعلق به السؤال",
        'buttons': ['القسم الشرعي', ('القسم الثقافي', 'CHOOSE_MATERIAL_TYPE')]
    },
    'CHOOSE_SUBJECT': {
        'input_type': 'button',
        'message': "حاذر من سلب علمك فوتًا ولا تعدلن به ذهبًا🍃\nمن فضلك قم باختيار المادة التي يتعلق بها السؤال.",
        'conditional_buttons': {
            'القسم الشرعي': ['العقيدة', 'علوم القرآن', 'الحديث', 'أصول الفقه', 'الفقه', 'للغة العربية']
        }
    },
    'CHOOSE_MATERIAL_TYPE': {
        'input_type': 'button',
        'message': "عينُ الفلاح في درر العزم والثبات فاثبت!🍃\nمن فضلك قم باختيار نوع المادة العلمية.",
        'buttons': [('كتاب', 'BOOK_NAME'), ('سلسلة محاضرات', 'SERIES_NAME')]
    },
    'SERIES_NAME': {
        'input_type': 'text',
        'message': "لا تطلب العلم رياء، ولا تتركه حياء🍃\nمن فضلك قم بإرسال اسم السلسلة",
    },
    'LECTURE_NAME_OR_NUMBER': {
        'input_type': 'text',
        'message': "يضيع العلم بين اثنين: الحياء والكبر.\nمن فضلك قم بإرسال اسم المحاضرة كاملًا",
        'next': 'QUESTION'
    },
    'BOOK_NAME': {
        'input_type': 'text',
        'message': "إن الجمال جمال العلم والأدب🍃\nمن فضلك قم بإرسال اسم الكتاب",
        'next': 'BOOK_PAGE_NUMBER'
    },
    'BOOK_PAGE_NUMBER': {
        'input_type': 'text',
        'message': "العلم أفضل خلف، والعمل به أكمل شرف🍃\nمن فضلك قم بإرسال رقم الصفحة",
        'next': 'QUESTION'
    },
    'QUESTION': {
        'input_type': 'text',
        'message': "العلوم أقفال وحسن السؤال مفاتحها🍃\nتفضل بالسؤال",
        'next': 'QUESTION_RECEIVED'
    },
    'QUESTION_RECEIVED': {
        'input_type': 'text',
        'message': "شكرا الله لكم وزادكم حرصا🍃\nسنوافيكم بالرد قريبًا إن شاء الله"
    }
}