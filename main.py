import logging
from config import *
from aiogram import Bot, Dispatcher
from aiogram.types import *
import utils
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.storage import FSMContext
from aiogram.utils.executor import start_polling
from aiogram.contrib.middlewares.logging import LoggingMiddleware
import sys

bot = Bot(TOKEN)
dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())
logging.basicConfig(level = logging.INFO)
dp = Dispatcher(bot, storage = MemoryStorage())


@dp.message_handler(commands='start', state='*')
async def greeting(message: Message, state: FSMContext):
    await state.finish()
    utils.saveNewUser(message.from_user.id, message.date)
    kb = InlineKeyboardMarkup()
    kb.add(utils.genInlineButtonWithCallback(START_POLL))
    addEditButtonIfItIsAdmin(kb, message.from_user, WITH_CHOICE_WHAT_TO_EDIT, 'greeting_text')
    await utils.send_message('greeting_text', bot, message.from_user.id, keyboard=kb)

def addEditButtonIfItIsAdmin(kb: InlineKeyboardMarkup, from_user: User, mode: int, variable: str):
    if from_user.id in admins:
        kb.add(InlineKeyboardButton(EDIT_MESSAGE[0], callback_data=f'{EDIT_MESSAGE[1]};{mode};{variable}'))

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

@dp.callback_query_handler(lambda call: call.data == START_POLL)
async def startPoll(callback: CallbackQuery):
    kb = InlineKeyboardMarkup()
    for s in SALARY_LIST:
        kb.add(utils.genInlineButtonWithCallback(s))
    addEditButtonIfItIsAdmin(kb, callback.from_user, WITH_CHOICE_WHAT_TO_EDIT, POLL_SALARY_TEXT)
    await utils.edit_message(bot, callback.message, POLL_SALARY_TEXT, keyboard=kb)

@dp.callback_query_handler(lambda call: call.data.startswith((SALARY_ANSWER_PREFIX, BACK_TO_MAIN_MENU)))
async def mainMenu(callback: CallbackQuery):
    kb = InlineKeyboardMarkup()
    kb.add(utils.genInlineButtonWithCallback(PATHS_OF_INCOME))
    kb.add(utils.genInlineButtonWithCallback(REVIEWS))
    kb.add(utils.genInlineButtonWithCallback(MY_ACHIEVEMENTS))
    addEditButtonIfItIsAdmin(kb, callback.from_user, WITH_CHOICE_WHAT_TO_EDIT, MAIN_MENU_TEXT)
    await utils.edit_message(bot, callback.message, MAIN_MENU_TEXT, keyboard=kb)

@dp.callback_query_handler(lambda call: call.data in  (PATHS_OF_INCOME, 'back_to_paths_of_income'))
async def pathsOfIncome(callback: CallbackQuery):
    kb = InlineKeyboardMarkup()
    kb.add(utils.genInlineButtonWithCallback('curator_of_the_project'))
    kb.add(utils.genInlineButtonWithCallback('online_profession'))
    kb.add(utils.genInlineButtonWithCallback('income_by_tasks'))
    kb.add(utils.genInlineButtonWithCallback('wildberries_manager'))
    kb.add(utils.genInlineButtonWithCallback(REVIEWS))
    kb.add(utils.genInlineButtonWithCallback(ASK_A_QUESTION))
    kb.add(utils.genInlineButtonWithCallback(BACK_TO_MAIN_MENU))
    addEditButtonIfItIsAdmin(kb, callback.from_user, WITH_CHOICE_WHAT_TO_EDIT, PATHS_OF_INCOME_TEXT)
    await utils.edit_message(bot, callback.message, PATHS_OF_INCOME_TEXT, keyboard=kb)

@dp.callback_query_handler(lambda call: call.data == MY_ACHIEVEMENTS)
async def myAchievements(callback: CallbackQuery):
    kb = InlineKeyboardMarkup()
    kb.add(utils.genInlineButtonWithCallback(PATHS_OF_INCOME))
    kb.add(utils.genInlineButtonWithCallback(BACK_TO_MAIN_MENU))
    addEditButtonIfItIsAdmin(kb, callback.from_user, WITH_CHOICE_WHAT_TO_EDIT, 'my_achievements_text')
    await utils.edit_message(bot, callback.message, 'my_achievements_text', keyboard=kb)

@dp.callback_query_handler(lambda call: call.data == REVIEWS)
async def showReviews(callback: CallbackQuery):
    kb = InlineKeyboardMarkup()
    kb.add(utils.genInlineButtonWithCallback(PATHS_OF_INCOME))
    kb.add(utils.genInlineButtonWithCallback(BACK_TO_MAIN_MENU))
    addEditButtonIfItIsAdmin(kb, callback.from_user, WITH_CHOICE_WHAT_TO_EDIT, 'reviews_text')
    await utils.edit_message(bot, callback.message, 'reviews_text', keyboard=kb)

@dp.callback_query_handler(lambda call: call.data in ('curator_of_the_project', 'back_to_curator'))
async def curatorOfTheProject(callback: CallbackQuery):
    kb = InlineKeyboardMarkup()
    kb.add(utils.genInlineButtonWithCallback('reg_curator_of_the_project'))
    kb.add(utils.genInlineButtonWithCallback('incomes_of_curators'))
    kb.add(utils.genInlineButtonWithCallback(ASK_A_QUESTION))
    kb.add(utils.genInlineButtonWithCallback('back_to_paths_of_income'))
    addEditButtonIfItIsAdmin(kb, callback.from_user, WITH_CHOICE_WHAT_TO_EDIT, 'curator_of_the_project_text')
    await utils.edit_message(bot, callback.message, 'curator_of_the_project_text', keyboard=kb)

@dp.callback_query_handler(lambda call: call.data in ('online_profession', 'back_to_online_profession'))
async def onlineProfession(callback: CallbackQuery):
    kb = InlineKeyboardMarkup()
    kb.add(utils.genInlineButtonWithCallback('reg_online_profession'))
    kb.add(utils.genInlineButtonWithCallback(ASK_A_QUESTION))
    kb.add(utils.genInlineButtonWithCallback('back_to_paths_of_income'))
    addEditButtonIfItIsAdmin(kb, callback.from_user, WITH_CHOICE_WHAT_TO_EDIT, 'online_profession_text')
    await utils.edit_message(bot, callback.message, 'online_profession_text', keyboard=kb)

@dp.callback_query_handler(lambda call: call.data in ('wildberries_manager', 'back_to_wildberries_manager'))
async def wildberriesManager(callback: CallbackQuery):
    kb = InlineKeyboardMarkup()
    kb.add(utils.genInlineButtonWithCallback('reg_wildberries_manager'))
    kb.add(utils.genInlineButtonWithCallback(ASK_A_QUESTION))
    kb.add(utils.genInlineButtonWithCallback('back_to_paths_of_income'))
    addEditButtonIfItIsAdmin(kb, callback.from_user, WITH_CHOICE_WHAT_TO_EDIT, 'wildberries_manager_text')
    await utils.edit_message(bot, callback.message, 'wildberries_manager_text', keyboard=kb)

@dp.callback_query_handler(lambda call: call.data in \
    ('reg_curator_of_the_project', 'i_want_to_the_project', 'tarifs_of_the_project'))
async def regCuratorOfTheProject(callback: CallbackQuery):
    await callback.message.edit_text(TEXT_ABOUT_CURATOR)
    kb = InlineKeyboardMarkup()
    kb.add(utils.genInlineButtonWithUrl(SEND_PAYMENT_CHEQUE))
    kb.add(utils.genInlineButtonWithCallback('incomes_of_curators'))
    kb.add(utils.genInlineButtonWithCallback(ASK_A_QUESTION))
    kb.add(utils.genInlineButtonWithCallback('back_to_curator'))
    addEditButtonIfItIsAdmin(kb, callback.from_user, WITH_CHOICE_WHAT_TO_EDIT, 'reg_curator_of_the_project_text')
    await utils.send_message('reg_curator_of_the_project_text', bot, callback.from_user.id, keyboard=kb)

@dp.callback_query_handler(lambda call: call.data in ('incomes_of_curators', 'back_to_incomes_of_curators'))
async def incomesOfCurators(callback: CallbackQuery):
    kb = InlineKeyboardMarkup()
    kb.add(utils.genInlineButtonWithCallback('i_want_to_the_project'))
    kb.add(utils.genInlineButtonWithCallback(ASK_A_QUESTION))
    kb.add(utils.genInlineButtonWithCallback('back_to_paths_of_income'))
    addEditButtonIfItIsAdmin(kb, callback.from_user, WITH_CHOICE_WHAT_TO_EDIT, 'incomes_of_curators_text')
    await utils.edit_message(bot, callback.message, 'incomes_of_curators_text', keyboard=kb)

@dp.callback_query_handler(lambda call: call.data in ('reg_online_profession', 'back_to_reg_online_profession'))
async def regForOnlineProfession(callback: CallbackQuery):
    kb = InlineKeyboardMarkup()
    kb.add(utils.genInlineButtonWithUrl(SEND_PAYMENT_CHEQUE))
    kb.add(utils.genInlineButtonWithCallback('tarifs_of_the_project'))
    kb.add(utils.genInlineButtonWithCallback(ASK_A_QUESTION))
    kb.add(utils.genInlineButtonWithCallback('back_to_paths_of_income'))
    addEditButtonIfItIsAdmin(kb, callback.from_user, WITH_CHOICE_WHAT_TO_EDIT, 'reg_online_profession_text')
    await utils.edit_message(bot, callback.message, 'reg_online_profession_text', keyboard=kb)

@dp.callback_query_handler(lambda call: call.data in ('income_by_tasks', 'back_to_income_by_tasks'))
async def incomeByTasks(callback: CallbackQuery):
    kb = InlineKeyboardMarkup()
    kb.add(utils.genInlineButtonWithCallback('i_want_tasks'))
    kb.add(utils.genInlineButtonWithCallback('reviews_of_income_by_tasks'))
    kb.add(utils.genInlineButtonWithCallback(ASK_A_QUESTION))
    kb.add(utils.genInlineButtonWithCallback('back_to_paths_of_income'))
    addEditButtonIfItIsAdmin(kb, callback.from_user, WITH_CHOICE_WHAT_TO_EDIT, 'income_by_tasks_text')
    await utils.edit_message(bot, callback.message, 'income_by_tasks_text', keyboard=kb)

@dp.callback_query_handler(lambda call: call.data in ('i_want_tasks', 'back_to_i_want_tasks'))
async def IWantTasks(callback: CallbackQuery):
    kb = InlineKeyboardMarkup()
    kb.add(utils.genInlineButtonWithCallback('reg_for_tasks'))
    kb.add(utils.genInlineButtonWithCallback(ASK_A_QUESTION))
    kb.add(utils.genInlineButtonWithCallback('back_to_income_by_tasks'))
    addEditButtonIfItIsAdmin(kb, callback.from_user, WITH_CHOICE_WHAT_TO_EDIT, 'i_want_tasks_text')
    await utils.edit_message(bot, callback.message, 'i_want_tasks_text', keyboard=kb)

@dp.callback_query_handler(lambda call: call.data in ('reg_for_tasks', 'back_to_reg_for_tasks'))
async def regForTasks(callback: CallbackQuery):
    kb = InlineKeyboardMarkup()
    kb.add(utils.genInlineButtonWithUrl(SEND_PAYMENT_CHEQUE))
    kb.add(utils.genInlineButtonWithCallback('help_me_with_choice'))
    kb.add(utils.genInlineButtonWithCallback('faq'))
    kb.add(utils.genInlineButtonWithCallback('back_to_i_want_tasks'))
    addEditButtonIfItIsAdmin(kb, callback.from_user, WITH_CHOICE_WHAT_TO_EDIT, 'reg_for_tasks_text')
    await utils.edit_message(bot, callback.message, 'reg_for_tasks_text', keyboard=kb)

@dp.callback_query_handler(lambda call: call.data == 'help_me_with_choice')
async def helpWithChoice(callback: CallbackQuery):
    kb = InlineKeyboardMarkup()
    kb.add(utils.genInlineButtonWithUrl(ASK_A_QUSETION_URL))
    kb.add(utils.genInlineButtonWithCallback('back_to_reg_for_tasks'))
    addEditButtonIfItIsAdmin(kb, callback.from_user, WITH_CHOICE_WHAT_TO_EDIT, 'help_me_with_choice_text')
    await utils.edit_message(bot, callback.message, 'help_me_with_choice_text', keyboard=kb)

@dp.callback_query_handler(lambda call: call.data == 'faq')
async def FAQ(callback: CallbackQuery):
    kb = InlineKeyboardMarkup()
    kb.add(utils.genInlineButtonWithCallback('reg_for_tasks'))
    addEditButtonIfItIsAdmin(kb, callback.from_user, WITH_CHOICE_WHAT_TO_EDIT, 'faq_text')
    await utils.send_message('faq_text', bot, callback.from_user.id, keyboard=kb)

@dp.callback_query_handler(lambda call: call.data == 'reg_wildberries_manager')
async def regWildberriesManager(callback: CallbackQuery):
    kb = InlineKeyboardMarkup()
    kb.add(utils.genInlineButtonWithUrl(SEND_PAYMENT_CHEQUE))
    kb.add(utils.genInlineButtonWithCallback(ASK_A_QUESTION))
    kb.add(utils.genInlineButtonWithCallback('back_to_wildberries_manager'))
    addEditButtonIfItIsAdmin(kb, callback.from_user, WITH_CHOICE_WHAT_TO_EDIT, 'reg_wildberries_manager_text')
    await utils.edit_message(bot, callback.message, 'reg_wildberries_manager_text', keyboard=kb)

@dp.callback_query_handler(lambda call: call.data == ASK_A_QUESTION)
async def askAQuestion(callback: CallbackQuery):
    kb = InlineKeyboardMarkup()
    kb.add(utils.genInlineButtonWithUrl(ASK_A_QUSETION_URL))
    kb.add(utils.genInlineButtonWithCallback(BACK_TO_MAIN_MENU))
    addEditButtonIfItIsAdmin(kb, callback.from_user, WITH_CHOICE_WHAT_TO_EDIT, ASK_A_QUESTION_INSTRUCTION)
    await utils.edit_message(bot, callback.message, ASK_A_QUESTION_INSTRUCTION, keyboard=kb)

@dp.callback_query_handler(lambda call: call.data.startswith(f'{EDIT_MESSAGE[1]};') and call.from_user.id in admins,
                           state = '*')
async def getNewText(callback: CallbackQuery, state: FSMContext):
    _, what_to_edit, variable = callback.data.split(';')
    what_to_edit = int(what_to_edit)
    await utils.EditMessage.get_text.set()
    state = dp.current_state(user = callback.from_user.id, chat = callback.from_user.id)
    data = await state.get_data()
    text = callback.message.text if callback.message.text else callback.message.caption
    if 'message' not in data:
        await state.update_data(message = callback.message)
        data['message'] = callback.message
    if 'photos' not in data:
        await state.update_data(photos = [])
    if 'keep_old_photos' not in data:
        await state.update_data(keep_old_photos = True)
    if 'value' not in data:
        await state.update_data(value = text)
    kb = None
    if callback.message.reply_markup:
        kb = utils.getEditablekeyboard(callback.message.reply_markup)
    if what_to_edit == EDIT_TEXT: # if there's no buttons
        await bot.send_message(callback.from_user.id, f'Отправьте новый текст для этого сообщения'
            '\n(или /cancel для отмены):')
    elif what_to_edit == WITH_CHOICE_WHAT_TO_EDIT:
        text = data['message'].text
        if not text:
            text = ''
        if data['message'].photo:
            try:
                await data['message'].delete()
            except: pass
            await bot.send_photo(callback.from_user.id, data['message'].photo[-1].file_id)
            new_msg = await bot.send_message(
                callback.from_user.id,
                f'{text}\n\nВыберите кнопку, '
                'которую хотите отредактировать либо отправьте новый текст '
                'сообщения, если хотите его изменить'
                '\n(или /cancel для отмены):',
                reply_markup = kb
            )
            data['message'].photo = []
            data['message'].message_id = new_msg.message_id
        else:
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

@dp.message_handler(lambda msg: msg.from_user.id in admins, state = utils.EditMessage.get_text)
async def editText(message: Message, state: FSMContext):
    data = await state.get_data()
    kb = InlineKeyboardMarkup()
    text = data['message'].text
    if data['what_to_edit'] == EDIT_TEXT:
        for row in data['message'].reply_markup.inline_keyboard:
            r = []
            for b in row:
                if not b.callback_data or b.callback_data.split(';')[0] != EDIT_MESSAGE[1]:
                    r.append(b)
            kb.row(*r)
        text = message.text
    elif data['what_to_edit'] == EDIT_BUTTON:
        kb = utils.editKeyboard(data['message'].reply_markup, data['variable'], message.text)
    kb.row(
        InlineKeyboardButton(CONFIRM_EDITING[0], callback_data=CONFIRM_EDITING[1]),
        InlineKeyboardButton('Назад↩️', callback_data=data['starting_callback_data'])
    )
    await state.update_data(value = message.text)
    await message.answer('Новое сообщение будет выглядеть так:')
    await utils.send_message(None, bot, message.from_user.id, keyboard = kb, text = text, photos = data['photos'])

@dp.callback_query_handler(lambda callback: callback.data == ATTACH_PHOTOS[1] and callback.from_user.id in admins, 
                           state = '*')
async def attach_photos(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await state.finish()
    await utils.EditMessage.get_media.set()
    state = dp.current_state(chat = callback.from_user.id, user = callback.from_user.id)
    await state.set_data(data)
    kb = InlineKeyboardMarkup()
    kb.row(
        InlineKeyboardButton(CONFIRM_ATTACHING_PHOTOS[0], callback_data=CONFIRM_ATTACHING_PHOTOS[1]),
        InlineKeyboardButton(CANCEL_ATTACHING_PHOTOS[0], callback_data=CANCEL_ATTACHING_PHOTOS[1])
    )
    await bot.send_message(callback.from_user.id, f'Отправьте фотографии', reply_markup=kb)

@dp.message_handler(lambda message: message.from_user.id in admins, content_types='photo', 
                    state = utils.EditMessage.get_media)
async def attach_photo(message: Message, state: FSMContext):
    data = await state.get_data()
    if 'photos' not in data:
        data['photos'] = [message.photo[0].file_id]
    else:
        data['photos'].append([message.photo[0].file_id])
    await state.set_data(data)

@dp.callback_query_handler(lambda callback: callback.data == CONFIRM_ATTACHING_PHOTOS[1] and \
                           callback.from_user.id in admins, state = utils.EditMessage.get_media)
async def confirm_attaching_photos(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await state.finish()
    data['keep_old_photos'] = False
    await utils.EditMessage.get_text.set()
    state = dp.current_state(chat = callback.from_user.id, user = callback.from_user.id)
    await state.set_data(data)
    try:
        await callback.message.delete()
    except: pass
    await callback.answer('Фотографии добавлены')
    kb = data['message'].reply_markup
    kb.add(InlineKeyboardButton(CONFIRM_EDITING[0], 
        callback_data=CONFIRM_EDITING[1]))
    await data['message'].edit_reply_markup(kb)

@dp.callback_query_handler(lambda callback: callback.data == CANCEL_ATTACHING_PHOTOS[1] and \
                           callback.from_user.id in admins, state = utils.EditMessage.get_media)
async def cancel_attaching_photos(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await state.finish()
    await utils.EditMessage.get_text.set()
    data['photos'] = []
    state = dp.current_state(chat = callback.from_user.id, user = callback.from_user.id)
    await state.set_data(data)
    try:
        await callback.message.delete()
    except: pass
    await callback.answer('Действие отменено')

@dp.callback_query_handler(lambda callback: callback.data == DELETE_PHOTOS[1] and \
                           callback.from_user.id in admins, state = utils.EditMessage.get_text)
async def delete_photos(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await state.update_data(photos = [], keep_old_photos = False)
    await callback.answer('Фотографии будут удалены')
    kb = data['message'].reply_markup
    kb.add(InlineKeyboardButton(CONFIRM_EDITING[0], 
        callback_data = CONFIRM_EDITING[1]))
    await bot.edit_message_reply_markup(data['message'].chat.id, data['message'].message_id, reply_markup = kb)

@dp.callback_query_handler(lambda call: call.from_user.id in admins and 
                           call.data.split(';')[0] == CONFIRM_EDITING[1], state = utils.EditMessage.get_text)
async def confirmEditing(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    try:
        utils.setMessage(data['variable'], data['value'], data['photos'], data['keep_old_photos'])
    except ValueError:
        await callback.message.edit_text('Вы не прикрепили фотографии и удалили текст!')
    data['message'].text = callback.message.text
    if data['what_to_edit'] == EDIT_BUTTON:
        data['message'].reply_markup = utils.editKeyboard(data['message'].reply_markup, data['variable'], data['value'], True)
    await callback.message.edit_text(data['message'].text, reply_markup = data['message'].reply_markup)
    await state.finish()
    await callback.answer('Успешно отредактировано')

if __name__ == '__main__':
    start_polling(dp, skip_updates=False)