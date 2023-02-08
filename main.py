from config import *
from aiogram import Bot, Dispatcher
from aiogram.types import *
import utils
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.storage import FSMContext

bot = Bot(TOKEN)
dp = Dispatcher(bot)
dp = Dispatcher(bot, storage = MemoryStorage())

@dp.message_handler(commands='start', state='*')
async def greeting(message: Message, state: FSMContext):
    await state.finish()
    kb = InlineKeyboardMarkup()
    kb.add(utils.genInlineButtonWithCallback(START_POLL))
    if message.from_user.id in admins:
        kb.add(InlineKeyboardButton(EDIT_MESSAGE[0], callback_data=f'{EDIT_MESSAGE[1]};{GET_CHOICE_WHAT_TO_EDIT};greeting_text'))
    await message.answer(utils.getText('greeting_text'), kb)

@dp.message_handler(commands='cancel', state='*')
async def cancel(message: Message, state: FSMContext):
    data = await state.get_data()
    await state.finish()
    if 'what_to_edit' in data:
        await bot.edit_message_text(data['message'].text, message.from_user.id, data['message'].message_id)
    else:
        await message.answer('Отмена')

@dp.callback_query_handler(lambda call: call.data.startswith(f'{EDIT_MESSAGE[1]};') and call.from_user.id in admins,
                           state = '*')
async def getNewText(callback: CallbackQuery, state: FSMContext):
    await state.finish()
    _, what_to_edit, variable = callback.data.split(';')
    what_to_edit = int(what_to_edit)
    utils.EditText.state.set()
    state = dp.current_state(user = callback.from_user.id, chat = callback.from_user.id)
    kb = None
    if callback.message.reply_markup:
        kb = getEditablekeyboard(callback.message.reply_markup)
    if what_to_edit == EDIT_TEXT:
        await bot.send_message(callback.from_user.id, f'Отправьте новый текст для этого сообщения'
            '\n(или /cancel для отмены):')
        await state.update_data(message = callback.message)
    elif what_to_edit == GET_CHOICE_WHAT_TO_EDIT:
        message = await callback.message.edit_text(
            f'{callback.message}\n\nВыберите кнопку, '
            'которую хотите отредактировать либо отправьте новый текст '
            'сообщения, если хотите его изменить'
            '\n(или /cancel для отмены):',
            reply_markup = kb
        )
        await state.update_data(message = message)
        what_to_edit = EDIT_TEXT # if user will send message it will automatically mean edit text
    else: # EDIT_BUTTON
        await bot.send_message(callback.from_user.id, f'Отправьте новый текст для этой кнопки'
            '\n(или /cancel для отмены):')
        await state.update_data(message = callback.message)
    await state.update_data(mode = what_to_edit, variable = variable, starting_callback_data = callback.data)

def getEditablekeyboard(kb: InlineKeyboardMarkup) -> InlineKeyboardButton:
    new_kb = InlineKeyboardMarkup()
    for row in kb.inline_keyboard:
        r = []
        for b in row:
            if b.callback_data:
                if b.callback_data.startswith(f'{EDIT_MESSAGE[1]};'):
                    r.append(b)
                    continue
                callback_data = b.callback_data
            else:
                callback_data = b.url
            callback_data = f'{EDIT_MESSAGE[1]};{EDIT_BUTTON};{callback_data}'
            r.append(InlineKeyboardButton(b.text, callback_data=callback_data))
        new_kb.row(*r)
    return new_kb

@dp.message_handler(lambda msg: msg.from_user.id in admins, state = utils.EditText.state)
async def editText(message: Message, state: FSMContext):
    data = await state.get_data()
    kb = InlineKeyboardMarkup()
    text = ''
    if data['what_to_edit'] == EDIT_TEXT:
        for row in data['message'].reply_markup.inline_keyboard:
            r = []
            for b in row:
                if b.callback_data.split(';')[0] != EDIT_MESSAGE[1]:
                    r.append(b)
            kb.row(*r)
        text = message.text
    elif data['what_to_edit'] == EDIT_BUTTON:
        kb = editKeyboard(data['message'].reply_markup, data['variable'], message.text)
        kb.row(
            InlineKeyboardButton(CONFIRM_EDITING[0], callback_data=CONFIRM_EDITING[1]),
            InlineKeyboardButton('⬅️ Назад⬅', callback_data=data['starting_callback_data'])
        )
        text = data['message'].text
    kb.row(
        InlineKeyboardButton(CONFIRM_EDITING[0], callback_data=CONFIRM_EDITING[1]),
        InlineKeyboardButton('⬅️ Назад', callback_data=data['starting_callback_data'])
    )
    await state.update_data(value = message.text)
    await message.answer('Новое сообщение будет выглядеть так:')
    await message.answer(text, kb)

def editKeyboard(kb: InlineKeyboardMarkup, callback_of_button_to_find: str, new_text: str) -> InlineKeyboardMarkup:
    for row in kb.inline_keyboard:
        r = []
        for b in row:
            c_d = b.callback_data.split(';')[0]
            if c_d != EDIT_MESSAGE[1]:
                if c_d == callback_of_button_to_find:
                    b.text = new_text
                r.append(b)
        kb.row(*r)

@dp.callback_query_handler(lambda call: call.from_user.id in admins and 
                           call.data.split(';')[0] == CONFIRM_EDITING, state = utils.EditText.state)
async def confirmEditing(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    utils.setText(data['variable'], data['value'])
    data['message'].text = callback.message.text
    if data['what_to_edit'] == EDIT_BUTTON:
        data['message'].reply_markup = editKeyboard(data['message'].reply_markup, data['variable'], data['value'])
    await callback.message.edit_text(data['message'].text, data['message'].reply_markup)
    await state.finish()
    await callback.answer('Успешно отредактировано')