from config import *
from aiogram import Bot, Dispatcher
from aiogram.types import *
import utils
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.storage import FSMContext
from aiogram.utils.executor import start_polling

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
    await message.answer(utils.getText('greeting_text'), reply_markup = kb)

@dp.message_handler(commands='cancel', state='*')
async def cancel(message: Message, state: FSMContext):
    data = await state.get_data()
    await state.finish()
    if 'what_to_edit' in data:
        msg = await bot.edit_message_text(data['message'].text, message.from_user.id, data['message'].message_id,
                                    reply_markup=data['message'].reply_markup)
        if msg.message_id not in (message.message_id-1, message.message_id-2):
            try:
                # delete message with example of edited message
                await bot.delete_message(message.from_user.id, message.message_id-1)
                await bot.delete_message(message.from_user.id, message.message_id-2)
            except:
                pass
    else:
        await message.answer('Отмена')

@dp.callback_query_handler(lambda call: call.data.startswith(f'{EDIT_MESSAGE[1]};') and call.from_user.id in admins,
                           state = '*')
async def getNewText(callback: CallbackQuery, state: FSMContext):
    _, what_to_edit, variable = callback.data.split(';')
    what_to_edit = int(what_to_edit)
    await utils.EditText.state.set()
    state = dp.current_state(user = callback.from_user.id, chat = callback.from_user.id)
    data = await state.get_data()
    if 'message' not in data:
        await state.update_data(message = callback.message)
        data['message'] = callback.message
    kb = None
    if callback.message.reply_markup:
        kb = getEditablekeyboard(callback.message.reply_markup)
    if what_to_edit == EDIT_TEXT:
        await bot.send_message(callback.from_user.id, f'Отправьте новый текст для этого сообщения'
            '\n(или /cancel для отмены):')
    elif what_to_edit == GET_CHOICE_WHAT_TO_EDIT:
        text = data['message'].text
        await callback.message.edit_text(
            f'{text}\n\nВыберите кнопку, '
            'которую хотите отредактировать либо отправьте новый текст '
            'сообщения, если хотите его изменить'
            '\n(или /cancel для отмены):',
            reply_markup = kb
        )
        what_to_edit = EDIT_TEXT # if user will send message it will automatically mean edit text
    else: # EDIT_BUTTON
        await bot.send_message(callback.from_user.id, f'Отправьте новый текст для этой кнопки'
            '\n(или /cancel для отмены):')
    if 'starting_callback_data' not in data:
        await state.update_data(starting_callback_data = callback.data)
    await state.update_data(what_to_edit = what_to_edit, variable = variable)

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
            try:
                b.text = utils.getText(callback_data) 
            except ValueError:
                pass
            callback_data = f'{EDIT_MESSAGE[1]};{EDIT_BUTTON};{callback_data}'
            r.append(InlineKeyboardButton(b.text, callback_data=callback_data))
        new_kb.row(*r)
    return new_kb

@dp.message_handler(lambda msg: msg.from_user.id in admins, state = utils.EditText.state)
async def editText(message: Message, state: FSMContext):
    data = await state.get_data()
    kb = InlineKeyboardMarkup()
    text = data['message'].text
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
        InlineKeyboardButton('⬅️ Назад', callback_data=data['starting_callback_data'])
    )
    await state.update_data(value = message.text)
    await message.answer('Новое сообщение будет выглядеть так:')
    await message.answer(text, reply_markup = kb)

def editKeyboard(kb: InlineKeyboardMarkup, callback_of_button_to_find: str, new_text: str, 
                 need_edit_button: bool = False) -> InlineKeyboardMarkup:
    new_kb = InlineKeyboardMarkup()
    for row in kb.inline_keyboard:
        r = []
        for b in row:
            c_d = b.callback_data.split(';')[0]
            if c_d != EDIT_MESSAGE[1] or need_edit_button:
                if c_d == callback_of_button_to_find:
                    b.text = new_text
                r.append(b)
        if r:
            new_kb.row(*r)
    return new_kb

@dp.callback_query_handler(lambda call: call.from_user.id in admins and 
                           call.data.split(';')[0] == CONFIRM_EDITING[1], state = utils.EditText.state)
async def confirmEditing(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    utils.setText(data['variable'], data['value'])
    data['message'].text = callback.message.text
    if data['what_to_edit'] == EDIT_BUTTON:
        data['message'].reply_markup = editKeyboard(data['message'].reply_markup, data['variable'], data['value'], True)
    await callback.message.edit_text(data['message'].text, reply_markup = data['message'].reply_markup)
    await state.finish()
    await callback.answer('Успешно отредактировано')

if __name__ == '__main__':
    start_polling(dp, skip_updates=False)