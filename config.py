from dotenv import load_dotenv
import os

load_dotenv()

TOKEN = os.getenv('bot_token')
USER = os.getenv('user')
PASSWORD = os.getenv('password')
DATABASE = os.getenv('database')
TABLE = os.getenv('table')

admins = (1026133582,)
TIMESTAMP_FORMAT = '%y-%m-%d %H:%M:%S'

#buttons with callbacks and callback's regimes
START_POLL = 'start_poll'
EDIT_MESSAGE = ('Редактировать ✏️', 'edit_message')
CONFIRM_EDITING = ('Сохранить ✅', 'confirm_edit')
EDIT_TEXT = 0
EDIT_BUTTON = 1
WITH_CHOICE_WHAT_TO_EDIT = 2
POLL_SALARY_TEXT = 'salary_question'
SALARY_ANSWER_PREFIX = 'salary-'
SALARY_LIST = tuple(f'{SALARY_ANSWER_PREFIX}{i}' for i in range(4))
MAIN_MENU_TEXT = 'main_menu'
REGISTER_FOR_COURSE = 'reg_for_course_button'
REGISTER_FOR_COURSE_TEXT = 'reg_for_course_text'
ASK_A_QUESTION_INSTRUCTION = 'how_to_ask_a_question'
ASK_A_QUSETION = 'ask_a_qusetion'
ASK_A_QUSETION_URL = 'https://web.telegram.org/k/'
SEND_PAYMENT_CHEQUE = 'https://vk.com/'
TEXT_ABOUT_PAYMENT = 'text_about_payment'
TARIFS = 'tarifs'
TEXT_ABOUT_TARIFS = 'text_about_tarifs'
BACK_TO_MAIN_MENU = 'back_to_main_menu'