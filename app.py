import aiogram
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram import Bot, Dispatcher, executor, types
from config import api_token, admin_id, mail_to
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import sqlite3
from mail import send_email, send_email_with_photo
import random

message_delete = {}
API_TOKEN = api_token
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())
db = sqlite3.connect('giveaway.db')
cur = db.cursor()
cur.execute("CREATE TABLE IF NOT EXISTS Users (id int, username_url TEXT)")
db.commit()
db.close()


class Form(StatesGroup):
    name_state = State()
    age_state = State()
    city_state = State()
    feedback_state = State()
    from_proof_to_feedback_state = State()
    from_what_u_find_item_state = State()
    from_not_bought_to_complain = State()
    feedback_state_only_complain = State()
    take_part_in_giveaway = State()


@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message, state: FSMContext):
    current_user = message.from_user.id
    with open("admins.txt", 'r', encoding='utf-8') as file:
        if current_user in map(int, file.readlines()):
            markup = InlineKeyboardMarkup(row_width=1)
            button1 = InlineKeyboardButton("Проверить количество пользователей в розыгрышах",
                                           callback_data='check_amount')
            button2 = InlineKeyboardButton("Выбрать победителя", callback_data="choose_winner")
            button3 = InlineKeyboardButton("DEBUG BUTTON", callback_data="check_subscr")
            markup.add(button1, button2, button3)
            await message.answer(f'{message.from_user.full_name}, здравствуйте! Выбирите действие админа:',
                                 reply_markup=markup)
        else:
            channel_link = 'https://t.me/+bFibV6s-K-o3ZjZi'
            markup = InlineKeyboardMarkup(row_width=1)
            button1 = InlineKeyboardButton("Подписаться", url=channel_link)
            button2 = InlineKeyboardButton("Проверить подписку", callback_data="check_subscr")
            markup.add(button1, button2)
            await message.answer(f"Здравствуйте! Подпишитесь, пожалуйста, на наш канал", reply_markup=markup)


@dp.callback_query_handler(lambda query: query.data in {'choose_winner', 'check_amount'})
async def callback_giveaway(callback_query: types.CallbackQuery, state: FSMContext):
    if callback_query.data == 'check_amount':
        db = sqlite3.connect('giveaway.db')
        cursor = db.cursor()
        cursor.execute("SELECT * FROM Users")
        res = cursor.fetchall()
        await bot.send_message(chat_id=callback_query.message.chat.id, text=f'Сейчас участвуют {len(res)} человек!')
        db.close()
    elif callback_query.data == 'choose_winner':
        try:
            db = sqlite3.connect('giveaway.db')
            cursor = db.cursor()
            cursor.execute('SELECT * FROM Users')
            res = cursor.fetchall()
            db.close()
            winner_id, winner_url = res[random.randrange(0, len(res))]
            await bot.send_message(callback_query.from_user.id, text=f'Новый победитель - @{winner_url}')
            # for e in res:
            #     await bot.send_message(e[0], text=f'Новый победитель - @{winner_url}')
        except ValueError:
            await bot.send_message(callback_query.from_user.id, text=f'В розыгрыше ещё нет участников!')


@dp.callback_query_handler(lambda query: query.data in {'check_subscr'})
async def bought_item1(callback_query: types.CallbackQuery, state: FSMContext):
    channel_id = -1002122669585
    user = await bot.get_chat_member(chat_id=channel_id, user_id=callback_query.from_user.id)
    is_subscribed = user.status == 'member' or user.status == 'creator' or user.status == 'administrator'
    if is_subscribed:
        msg3 = await bot.edit_message_text(
            chat_id=callback_query.message.chat.id,
            message_id=callback_query.message.message_id,
            text="Здравствуйте!👋\nПросим Вас указать ваши данные. Как Вас зовут?"
        )
        message_delete[callback_query.message.chat.id] = [msg3.message_id]
        await Form.name_state.set()
    else:
        await bot.edit_message_text(
            chat_id=callback_query.message.chat.id,
            message_id=callback_query.message.message_id,
            text="Извините, Вы должны подписаться на наш канал! /start"
        )
        await state.finish()


@dp.message_handler(state=Form.name_state)
async def process_name(message: types.Message, state: FSMContext):
    name_of_user = message.text
    message_delete.get(message.chat.id, []).append(message.message_id)
    for message_id in message_delete.get(message.chat.id, []):
        try:
            await bot.delete_message(message.chat.id, message_id)
        except aiogram.utils.exceptions.MessageToDeleteNotFound:
            pass
    async with state.proxy() as data:
        data['name_of_user'] = name_of_user
    msg3 = await message.answer(f"Отлично, {name_of_user}, приятно познакомиться! Введите Ваш возраст:")
    message_delete[message.chat.id] = [msg3.message_id]
    await Form.age_state.set()


@dp.message_handler(state=Form.age_state)
async def process_age(message: types.Message, state: FSMContext):
    age_of_user = message.text
    if age_of_user.isdigit():
        message_delete.get(message.chat.id, []).append(message.message_id)
        for message_id in message_delete.get(message.chat.id, []):
            try:
                await bot.delete_message(message.chat.id, message_id)
            except aiogram.utils.exceptions.MessageToDeleteNotFound:
                pass
        async with state.proxy() as data:
            data['age_of_user'] = age_of_user
        msg3 = await message.answer(f"Отлично! Из какого Вы города?")
        message_delete[message.chat.id] = [msg3.message_id]
        await Form.city_state.set()
    else:
        await message.answer(text=f"{message.text} - это не цифра! /start")
        await state.finish()


@dp.message_handler(state=Form.city_state)
async def process_city(message: types.Message, state: FSMContext):
    city_of_user = message.text
    message_delete.get(message.chat.id, []).append(message.message_id)
    for message_id in message_delete.get(message.chat.id, []):
        try:
            await bot.delete_message(message.chat.id, message_id)
        except aiogram.utils.exceptions.MessageToDeleteNotFound:
            pass
    async with state.proxy() as data:
        data['city_of_user'] = city_of_user
    markup = InlineKeyboardMarkup(row_width=1)
    button1 = InlineKeyboardButton("Я купил(а) товар", callback_data='bought')
    button2 = InlineKeyboardButton("Я не купил(а) товар", callback_data='not_bought')
    markup.add(button1, button2)
    await message.answer(
        f"Здравствуйте, {data['name_of_user']}! Бренд Dave&Ante рада вашему присутствию в нашем чат-боте.\n"
        "Подтвердите пожалуйста покупку товара, сделав фотографию товара (не в пункте выдачи заказов).",
        reply_markup=markup
    )


@dp.callback_query_handler(lambda query: query.data in {'bought', 'not_bought'}, state=Form.city_state)
async def bought_item(callback_query: types.CallbackQuery, state: FSMContext):
    if callback_query.data == 'not_bought':
        message_delete.get(callback_query.message.chat.id, []).append(callback_query.message.message_id)
        for message_id in message_delete.get(callback_query.message.chat.id, []):
            try:
                await bot.delete_message(callback_query.message.chat.id, message_id)
            except aiogram.utils.exceptions.MessageToDeleteNotFound:
                pass

        await bot.send_message(callback_query.message.chat.id,
                               text='Ваше мнение для нас очень важно, pасскажите, что не устроило вас в нашем товаре?')
        await state.update_data(FeedbackType=callback_query.data)
        await Form.feedback_state_only_complain.set()
    else:
        await bot.edit_message_text(
            chat_id=callback_query.message.chat.id,
            message_id=callback_query.message.message_id,
            text="Пожалуйста, отправьте фото купленного товара.", reply_markup=None

        )
        await Form.from_proof_to_feedback_state.set()


@dp.message_handler(lambda message: not message.photo, state=Form.from_proof_to_feedback_state)
async def check_photo(message: types.Message, state: FSMContext):
    await message.reply('Это не фотография!, попробуйте снова /start')
    await state.finish()


@dp.message_handler(content_types=['photo'], state=Form.from_proof_to_feedback_state)
async def feedback(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['photo'] = message.photo[0].file_id
    markup = InlineKeyboardMarkup(row_width=1)
    button1 = InlineKeyboardButton("Хочу похвалить вас", callback_data='praise')
    button2 = InlineKeyboardButton("Хочу предложить вам улучшить продукт", callback_data='improve')
    button3 = InlineKeyboardButton("Хочу пожаловаться на ваш товар", callback_data='complain')
    button4 = InlineKeyboardButton("У меня есть вопросы", callback_data='questions')
    markup.add(button1, button2, button3, button4)

    await message.answer(
        "Мы очень ценим наших покупателей, в рамках нашего возрастающего бренда, мы будем проводить розыгрыши (Профессиональная фотосессия, билеты на выставки, Stand-up концерты, экскурсии). Для того чтобы ознакомиться с условиями розыгрыша - просим подписаться на наш телеграмм-канал.\n\nС радостью готовы услышать ваши похвалы и жалобы по нашему товару",
        reply_markup=markup
    )


@dp.callback_query_handler(lambda query: query.data in {'praise', 'questions', 'complain', 'improve'},
                           state=Form.from_proof_to_feedback_state)
async def bought_item2(callback_query: types.CallbackQuery, state: FSMContext):
    await state.update_data(FeedbackType=callback_query.data)
    if callback_query.data == 'praise':
        await bot.edit_message_text(
            chat_id=callback_query.message.chat.id,
            message_id=callback_query.message.message_id,
            text="Ваше мнение для нас очень важно, расскажите, пожалуйста, что вам понравилось и скажите, пожалуйста, как нашли наш товар?"
        )
        await Form.feedback_state.set()
    elif callback_query.data == 'complain':
        await bot.edit_message_text(
            chat_id=callback_query.message.chat.id,
            message_id=callback_query.message.message_id,
            text="Ваше мнение для нас очень важно, pасскажите, что не устроило вас в нашем товаре и скажите, пожалуйста, как нашли наш товар?"
        )
        await Form.feedback_state.set()
    elif callback_query.data == 'questions':
        await bot.edit_message_text(
            chat_id=callback_query.message.chat.id,
            message_id=callback_query.message.message_id,
            text="Наши специалисты готовы ответить на все ваши вопросы. Чем мы можем помочь вам?\nПожалуйста, расскажите, как вы нашли наш товар.\nИ не забудьте указать в сообщении ваши контактные данные - почту или телефон. Наш менеджер свяжется с вами."
        )
        await Form.feedback_state.set()
    elif callback_query.data == 'improve':
        await bot.edit_message_text(
            chat_id=callback_query.message.chat.id,
            message_id=callback_query.message.message_id,
            text="Мы готовы внимательно рассмотреть ваши предложения по совершенствованию нашего продукта и скажите, пожалуйста, как нашли наш товар:"
        )
        await Form.feedback_state.set()


@dp.message_handler(state=Form.feedback_state_only_complain)
async def feedback_complain_func(message: types.Message, state: FSMContext):
    markup = InlineKeyboardMarkup(row_width=1)
    button1 = InlineKeyboardButton("Участвовать в розыгрыше!", callback_data='drawing')
    markup.add(button1)
    await bot.send_message(message.chat.id,
                           "Благодарим вас за предоставленную информацию.С уважением команда Dave&Ante"
                           , reply_markup=markup
                           )
    feedback_from_user = message.text
    async with state.proxy() as data:
        text_to_admin = f"Name: {data['name_of_user']}\nAge: {data['age_of_user']}\nCity: {data['city_of_user']}\nКомментарий ({data['FeedbackType']}): {feedback_from_user}"
        await bot.send_message(chat_id=admin_id, text=text_to_admin)

    send_email(mail_to, text_to_admin)
    await state.finish()


@dp.message_handler(state=Form.feedback_state)
async def feedback_func(message: types.Message, state: FSMContext):
    markup = InlineKeyboardMarkup(row_width=1)
    button1 = InlineKeyboardButton("Участвовать в розыгрыше!", callback_data='drawing')
    markup.add(button1)
    await bot.send_message(message.chat.id,
                           "Благодарим вас за предоставленную информацию. С уважением команда Dave&Ante",
                           reply_markup=markup)
    feedback_from_user = message.text
    async with state.proxy() as data:
        text_to_admin = f"Name: {data['name_of_user']}\nAge: {data['age_of_user']}\nCity: {data['city_of_user']}\nКомментарий ({data['FeedbackType']}): {feedback_from_user}"
        await bot.send_photo(chat_id=admin_id,
                             photo=data['photo'],
                             caption=text_to_admin)

    file_info = await bot.get_file(data['photo'])
    file_path = file_info.file_path

    file_url = f"https://api.telegram.org/file/bot{API_TOKEN}/{file_path}"
    send_email_with_photo(mail_to, text_to_admin, file_url)
    await state.finish()


@dp.callback_query_handler(lambda query: query.data in {'drawing'})
async def giveaway_func(callback_query: types.CallbackQuery, state: FSMContext):
    db = sqlite3.connect('giveaway.db')
    cur = db.cursor()
    cur.execute("SELECT * FROM Users WHERE id=?", (callback_query.from_user.id,))
    res = cur.fetchone()
    if res is None:
        await bot.edit_message_text(
            chat_id=callback_query.message.chat.id,
            message_id=callback_query.message.message_id,
            text="Спасибо за участие! Результаты розыгрышей будут приходить сюда."
        )
        user_url = callback_query.from_user.username
        cur.execute('INSERT INTO Users (id, username_url) VALUES (?,?)',
                    (callback_query.from_user.id, user_url))
        db.commit()
        db.close()
        await state.finish()
    else:
        await bot.edit_message_text(
            chat_id=callback_query.message.chat.id,
            message_id=callback_query.message.message_id,
            text="Вы уже принимаете участие в розыгрышах."
        )
        await state.finish()


if __name__ == '__main__':
    executor.start_polling(dp)
