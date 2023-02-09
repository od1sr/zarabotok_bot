from datetime import datetime
from mysql.connector import MySQLConnection
from config import *
from aiogram.types import InlineKeyboardButton
from aiogram.dispatcher.filters.state import State, StatesGroup

class EditText(StatesGroup):
    state = State()

def getText(text_name: str) -> str:
    with MySQLConnection(user = USER, password = PASSWORD, database = DATABASE) as conn:
        with conn.cursor() as cursor:
            cursor.execute(f'SELECT value FROM {TABLE} WHERE variable = "{text_name}"')
            result =  cursor.fetchall()
            if not result:
                return text_name
            return result[0][0]
        
def setText(text_name: str, text: str):
    with MySQLConnection(user = USER, password = PASSWORD, database = DATABASE) as conn:
        with conn.cursor() as cursor:
            cursor.execute(f'SELECT COUNT(variable) FROM {TABLE} WHERE variable = "{text_name}"')
            text = __getValidText(text)
            if cursor.fetchall()[0][0]:
                cursor.execute(f'UPDATE {TABLE} SET value = "{text}" WHERE variable = "{text_name}"')
            else:
                cursor.execute(f'INSERT INTO {TABLE} VALUES("{text_name}","{text}")')
            conn.commit()
def genInlineButtonWithCallback(button: str, extra_callback: str = '') -> InlineKeyboardButton:
    return InlineKeyboardButton(getText(button), 
                                callback_data = button if not extra_callback else f'{button};{extra_callback}')
    
def genInlineButtonWithUrl(url: str) -> InlineKeyboardButton:
    return InlineKeyboardButton(getText(url), url)


def __getValidText(text: str) -> str:
    text = list(text)
    for i in range(len(text)):
        if text[i] in '"\'\\':
            text[i] = '\\' + text[i]
    return ''.join(text)

def saveNewUser(user_id: int, time: datetime):
    with MySQLConnection(user = USER, password = PASSWORD, database = DATABASE) as conn:
        with conn.cursor() as cursor:
            cursor.execute(F'SELECT COUNT(id) FROM users WHERE id = {user_id}')
            if not cursor.fetchall()[0][0]:
                cursor.execute(f'INSERT INTO users VALUES ({user_id}, "{time.strftime(TIMESTAMP_FORMAT)}")')
                conn.commit()