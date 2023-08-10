from dotenv import load_dotenv
import os

load_dotenv()
TESTING=True


TOKEN = os.getenv('bot_token' if not TESTING else 'test_bot_token')
USER = os.getenv('user')
PASSWORD = os.getenv('password')
DATABASE = os.getenv('database' if not TESTING else 'test_database')
TEXTS_TABLE = os.getenv('texts_table')
MEDIA_TABLE = os.getenv('media_table')

admins = (1026133582, 5751901817, 1575767034)
TIMESTAMP_FORMAT = '%y-%m-%d %H:%M:%S'

#buttons with callbacks and callback's regimes
START_POLL = 'start_poll'
EDIT_MESSAGE = ('Редактировать ✏️', 'edit_message')
CONFIRM_EDITING = ('Сохранить ✅', 'confirm_edit')
ATTACH_PHOTOS = ('Добавить фото', 'attach_media')
DELETE_PHOTOS = ('Удалить все фото 🗑', 'del_photos')
CONFIRM_ATTACHING_PHOTOS = ('Готово ✅', 'confirm_attaching_photos')
CANCEL_ATTACHING_PHOTOS = ('Отмена ❌', 'cancel_attaching_photos')
# what ot edit
EDIT_TEXT = 0 # if there's no buttons
EDIT_BUTTON = 1
WITH_CHOICE_WHAT_TO_EDIT = 2
POLL_SALARY_TEXT = 'salary_question'
SALARY_ANSWER_PREFIX = 'salary-'
SALARY_LIST = tuple(f'{SALARY_ANSWER_PREFIX}{i}' for i in range(4))
MAIN_MENU_TEXT = 'main_menu'
ASK_A_QUESTION_INSTRUCTION = 'how_to_ask_a_question'
ASK_A_QUESTION = 'ask_a_qusetion'
ASK_A_QUSETION_URL = 'http://vk.com/id163375420/'
SEND_PAYMENT_CHEQUE = 'https://vk.com/id163375420/'
PRESENTATION = 'https://youtu.be/b7Gb503Eh3U'
TEXT_ABOUT_PAYMENT = 'text_about_payment'
TARIFS = 'tarifs'
TEXT_ABOUT_TARIFS = 'text_about_tarifs'
BACK_TO_MAIN_MENU = 'back_to_main_menu'
LIST_OF_COURSES_BUTTON = 'list_of_courses_button'
LIST_OF_COURSES = 'list_of_courses'

PATHS_OF_INCOME = 'paths_of_income'
PATHS_OF_INCOME_TEXT = 'paths_of_income_text'
REVIEWS = 'reviews'
MY_ACHIEVEMENTS = 'my_achievements'

TEXT_ABOUT_CURATOR = '''❗️Опережая вопросы, обучение - да, платное, 🔥НО🔥ОКУПАЕМОСТЬ ОБУЧЕНИЯ В ПЕРВЫЕ ДНИ ОБУЧЕНИЯ🔥

Доступ к материалам и проекту, приобретается только 1 раз💯 Информации здесь на миллион! Ежемесячных вложений и платежей нет❌

‌При этом ⬇️

✅Курсы доступны НАВСЕГДА, обновления БЕСПЛАТНЫЕ.
✅Доход СРАЗУ НА КАРТУ!!!
✅Опыт для всего этого не нужен🚀
✅Поддержка куратора 24/7 - моя личная
✅Можно совмещать с основной работой/учебой/бизнесом/декретом
✅Нет планов, начальства, графика, не нужно набирать команду и перед кем-то отчитываться. Сам себе хозяин.

💫Кстати, для любого варианта нужен только телефон💫

Все доходы, вакансии, платформу обучения, отзывы учеников - всё смогу вам показать! И это не очередные курсы как у блогеров, где сплошная вода. Это классная возможность , на которой я зарабатываю сама. И вы можете за мной наблюдать на моей страничке в Инстаграм. Я такой же человек, как и вы. И предлагаю реальную и легальную работу!
Сложного в этом ничего нет, хотя на первый взгляд работа в интернете кажется чем-то нереальным и сложным, но это не так). Нужно только сделать шаг навстречу другой реальности 🔥 Возможности открыты для всех🚀'''