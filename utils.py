from datetime import datetime
from mysql.connector import MySQLConnection
from config import *
from aiogram.types import InlineKeyboardButton
from aiogram.dispatcher.filters.state import State, StatesGroup
import typing
from aiogram.types import *
from aiogram import Bot

class EditMessage(StatesGroup):
    get_text = State()
    get_media = State()

def getMessage(text_name: str) -> typing.Tuple[str, typing.List[str]]:
    '''returns text of the message and it's pinned photos' ids'''
    with MySQLConnection(user = USER, password = PASSWORD, database = DATABASE) as conn:
        with conn.cursor() as cursor:
            cursor.execute(f'SELECT id, value FROM {TEXTS_TABLE} WHERE variable = "{text_name}"')
            result =  cursor.fetchall()
            if not result:
                return text_name, []
            id, text = result[0]
            cursor.execute(f'SElECT photo_id FROM {MEDIA_TABLE} WHERE text_id = {id}')
            result = cursor.fetchall()
            if not result:
                return text, []
            return text, [i[0] for i in result]

        
def setMessage(text_name: str, text: str, photos: typing.List[str] = [], keep_old_photos: bool = True):
    with MySQLConnection(user = USER, password = PASSWORD, database = DATABASE) as conn:
        with conn.cursor() as cursor:
            cursor.execute(f'SELECT id FROM {TEXTS_TABLE} WHERE variable = "{text_name}"')
            text = __getValidText(text)
            id = cursor.fetchall()
            id = None if not id else id[0][0] 
            if not text and not photos and not id:
                raise ValueError('Message can not be empty')
            if id and not text and not photos:
                cursor.execute(f'SELECT COUNT(text_id) FROM {MEDIA_TABLE} WHERE text_id = {id}')
                if not cursor.fetchall()[0][0]:
                    raise ValueError('Message can not be empty')
                if not keep_old_photos:
                    raise ValueError('Message can not be empty')
            if id and text:
                cursor.execute(f'UPDATE {TEXTS_TABLE} SET value = "{text}" WHERE variable = "{text_name}"')
            elif not id:
                cursor.execute(f'INSERT INTO {TEXTS_TABLE} VALUES(DEFAULT, "{text_name}","{text}")')
            if not keep_old_photos:
                cursor.execute(f'DELETE FROM {MEDIA_TABLE} WHERE text_id = {id}')
            if photos:
                for photo in photos:
                    cursor.execute(f'INSERT INTO {MEDIA_TABLE} VALUES ({id}, "{__getValidText(photo)}")')
            conn.commit()
def __getValidText(text: str) -> str:
    text = list(text)
    for i in range(len(text)):
        if text[i] in '"\'\\':
            text[i] = '\\' + text[i]
    return ''.join(text)

def genInlineButtonWithCallback(button: str, extra_callback: str = '') -> InlineKeyboardButton:
    return InlineKeyboardButton(getMessage(button)[0], 
                                callback_data = button if not extra_callback else f'{button};{extra_callback}')
def genInlineButtonWithUrl(url: str) -> InlineKeyboardButton:
    return InlineKeyboardButton(getMessage(url)[0], url)

def saveNewUser(user_id: int, time: datetime):
    with MySQLConnection(user = USER, password = PASSWORD, database = DATABASE) as conn:
        with conn.cursor() as cursor:
            cursor.execute(F'SELECT COUNT(id) FROM users WHERE id = {user_id}')
            if not cursor.fetchall()[0][0]:
                cursor.execute(f'INSERT INTO users VALUES ({user_id}, "{time.strftime(TIMESTAMP_FORMAT)}")')
                conn.commit()

async def send_message(name_of_the_message: typing.Union[str, None], bot: Bot, chat_id: int, 
                       parse_mode: typing.Union[str, None] = None,
                       keyboard: typing.Union[InlineKeyboardMarkup, ReplyKeyboardMarkup, None] = None,
                       text: typing.Union[str, None] = None,
                       photos: typing.Union[typing.List[str], None] = None) -> Message:
    '''if name_of_the_message is None and text is not None bot will send the text.
    Otherwise he will get the text of a message by the name_of_the_message and then send it'''
    if name_of_the_message is not None:
        text, photos = getMessage(name_of_the_message)
    if photos:
        media_group = MediaGroup()
        for p in photos:
            media_group.attach_photo(p)
        await bot.send_media_group(chat_id, media_group)
    return await bot.send_message(chat_id, text, reply_markup=keyboard, parse_mode=parse_mode)
    
async def edit_message(bot: Bot, orig_message: Message, name_of_the_new_msg: str, 
                       parse_mode: typing.Union[str, None] = None,
                       keyboard: typing.Union[InlineKeyboardMarkup, ReplyKeyboardMarkup, None] = None
) -> typing.Union[Message, None]:
    text, photos = getMessage(name_of_the_new_msg)
    Bot.set_current(bot)
    new_msg = None
    if photos:
        media_group = MediaGroup()
        for p in photos: 
            media_group.attach_photo(p)
        try:
            await orig_message.delete()
        except: pass
        new_msg = await bot.send_media_group(orig_message.chat.id, media_group)
    if text:
        if not photos:
            new_msg = await orig_message.edit_text(text, reply_markup = keyboard, parse_mode = parse_mode)
        else:
            new_msg = await bot.send_message(
                orig_message.chat.id, text, reply_markup = keyboard, parse_mode = parse_mode)
    return new_msg

def getEditablekeyboard(kb: InlineKeyboardMarkup) -> InlineKeyboardButton:
    new_kb = InlineKeyboardMarkup()
    for row in kb.inline_keyboard:
        r = []
        for b in row:
            if b.callback_data:
                if b.callback_data.startswith((f'{EDIT_MESSAGE[1]};', CONFIRM_EDITING[1])):
                    continue
                callback_data = b.callback_data
            else:
                callback_data = b.url
            # restore true text of button if there was canceled editing recently 
            temp_, _ = getMessage(callback_data) 
            if temp_ != callback_data:
                b.text = temp_
            callback_data = f'{EDIT_MESSAGE[1]};{EDIT_BUTTON};{callback_data}'
            r.append(InlineKeyboardButton(b.text, callback_data=callback_data))
        new_kb.row(*r)
    new_kb.row(
        InlineKeyboardButton(ATTACH_PHOTOS[0], callback_data=ATTACH_PHOTOS[1]),
        InlineKeyboardButton(DELETE_PHOTOS[0], callback_data=DELETE_PHOTOS[1])
    )
    return new_kb

def editKeyboard(kb: InlineKeyboardMarkup, callback_of_button_to_find: str, new_text: str, 
                 need_edit_button: bool = False) -> InlineKeyboardMarkup:
    new_kb = InlineKeyboardMarkup()
    for row in kb.inline_keyboard:
        r = []
        for b in row:
            c_d = b.url if not b.callback_data else b.callback_data.split(';')[0]
            if c_d != EDIT_MESSAGE[1] or need_edit_button:
                if c_d == callback_of_button_to_find:
                    b.text = new_text
                r.append(b)
        if r:
            new_kb.row(*r)
    return new_kb