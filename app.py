import sqlite3
import aiogram
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram import Bot, Dispatcher, executor, types
from config import api_token
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

message_delete = {}
API_TOKEN = api_token
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())


class Form(StatesGroup):
    name_state = State()
    age_state = State()
    city_state = State()
    feedback_state = State()


@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message, state: FSMContext):
    # conn = sqlite3.connect("data/tokens.sql")
    # cursor = conn.cursor()
    # cursor.execute(
    #     'CREATE TABLE IF NOT EXISTS tokens_tbl (id int name primary key, userid varchar(200), NotionToken varchar(200), DBToken varchar(1000))')
    # conn.commit()
    # cursor.close()
    # conn.close()
    msg3 = await message.answer("Здравствуйте!👋\nПросим Вас указать ваши данные. Как Вас зовут?")
    message_delete[message.chat.id] = [msg3.message_id]
    await Form.name_state.set()


@dp.message_handler(state=Form.name_state)
async def process_name(message: types.Message, state: FSMContext):
    name_of_user = message.text
    message_delete.get(message.chat.id, []).append(message.message_id)
    for message_id in message_delete.get(message.chat.id, []):
        try:
            await bot.delete_message(message.chat.id, message_id)
        except aiogram.utils.exceptions.MessageToDeleteNotFound:
            pass

    # conn = sqlite3.connect("data/tokens.sql")
    # cursor = conn.cursor()
    # cursor.execute(
    #     f'INSERT INTO tokens_tbl (userid, NotionToken) VALUES ("%s", "%s")' % (str(message['from']['id']), user_token))
    # cursor.execute('UPDATE tokens_tbl SET NotionToken=? WHERE userid=?', (user_token, (str(message['from']['id']))))
    # conn.commit()
    # cursor.close()
    # conn.close()
    msg3 = await message.answer(f"Отлично, {name_of_user}, приятно познакомиться! Введите Ваш возраст:")
    message_delete[message.chat.id] = [msg3.message_id]
    await Form.age_state.set()


@dp.message_handler(state=Form.age_state)
async def process_name(message: types.Message, state: FSMContext):
    age_of_user = message.text
    print(age_of_user)
    message_delete.get(message.chat.id, []).append(message.message_id)
    for message_id in message_delete.get(message.chat.id, []):
        try:
            await bot.delete_message(message.chat.id, message_id)
        except aiogram.utils.exceptions.MessageToDeleteNotFound:
            pass
    msg3 = await message.answer(f"Отлично! Из какого Вы города?")
    message_delete[message.chat.id] = [msg3.message_id]
    await Form.city_state.set()


@dp.message_handler(state=Form.city_state)
async def process_name(message: types.Message, state: FSMContext):
    city_of_user = message.text
    message_delete.get(message.chat.id, []).append(message.message_id)
    for message_id in message_delete.get(message.chat.id, []):
        try:
            await bot.delete_message(message.chat.id, message_id)
        except aiogram.utils.exceptions.MessageToDeleteNotFound:
            pass
    await state.finish()
    user_name = message.from_user.first_name
    markup = InlineKeyboardMarkup(row_width=1)
    button1 = InlineKeyboardButton("Я купил(а) товар", callback_data='bought')
    button2 = InlineKeyboardButton("Я не купил(а) товар", callback_data='not_bought')
    markup.add(button1, button2)

    await message.answer(
        f"Здравствуйте, {user_name}! Бренд Dave&Ante рада вашему присутствию в нашем чат-боте.\n"
        "Подтвердите пожалуйста покупку товара, сделав фотографию товара (не в пункте выдачи заказов).",
        reply_markup=markup
    )


@dp.callback_query_handler(lambda query: query.data == 'bought')
async def bought_item(callback_query: types.CallbackQuery):
    await bot.edit_message_text(
        chat_id=callback_query.message.chat.id,
        message_id=callback_query.message.message_id,
        text="Пожалуйста, отправьте фото купленного товара."
    )


@dp.callback_query_handler(lambda query: query.data == 'not_bought')
async def not_bought_item(callback_query: types.CallbackQuery):
    await bot.edit_message_text(
        chat_id=callback_query.message.chat.id,
        message_id=callback_query.message.message_id,
        text="Жаль, что вы не купили товар. Может быть в следующий раз!"
    )


@dp.message_handler(commands=['feedback'])
async def feedback(message: types.Message):
    markup = InlineKeyboardMarkup(row_width=1)
    button1 = InlineKeyboardButton("Хочу похвалить вас", callback_data='praise')
    button2 = InlineKeyboardButton("Хочу предложить вам улучшить свой продукт", callback_data='improve')
    button3 = InlineKeyboardButton("Хочу пожаловаться на ваш товар", callback_data='complain')
    button4 = InlineKeyboardButton("У вас есть вопросы к нам?", callback_data='questions')
    markup.add(button1, button2, button3, button4)

    await message.answer(
        "Мы очень ценим наших покупателей, в рамках нашего возрастающего бренда, мы будем проводить розыгрыши (Профессиональная фотосессия, билеты на выставки, Stand-up концерты, экскурсии). Для того чтобы ознакомиться с условиями розыгрыша - просим подписаться на наш телеграмм-канал.\n\nС радостью готовы услышать ваши похвалы и жалобы по нашему товару",
        reply_markup=markup
    )






@dp.callback_query_handler(lambda query: query.data in {'praise', 'questions', 'complain', 'improve'})
async def bought_item(callback_query: types.CallbackQuery):
    print("in")
    if callback_query.data == 'praise':
        print("in")
        await bot.edit_message_text(
            chat_id=callback_query.message.chat.id,
            message_id=callback_query.message.message_id,
            text="Готовы выслушать вас:"
        )
    elif callback_query.data == 'complain':
        await bot.edit_message_text(
            chat_id=callback_query.message.chat.id,
            message_id=callback_query.message.message_id,
            text="Ваше мнение для нас очень важно. Расскажите, что не устроило вас в нашем товаре."
        )
    elif callback_query.data == 'questions':
        await bot.edit_message_text(
            chat_id=callback_query.message.chat.id,
            message_id=callback_query.message.message_id,
            text="Наши специалисты готовы ответить на все ваши вопросы. Чем мы можем помочь вам?")
    elif callback_query.data == 'improve':
        await bot.edit_message_text(
            chat_id=callback_query.message.chat.id,
            message_id=callback_query.message.message_id,
            text="Мы готовы внимательно рассмотреть ваши предложения по совершенствованию нашего продукта:"
        )
    await Form.feedback_state.set()

@dp.message_handler(state=Form.feedback_state)
async def process_name(message: types.Message, state: FSMContext):
    feedback = message.text

@dp.message_handler(state=Form.feedback_state)
async def process_name(message: types.Message, state: FSMContext):
    feedback_from_user = message.text
    message_delete.get(message.chat.id, []).append(message.message_id)
    for message_id in message_delete.get(message.chat.id, []):
        try:
            await bot.delete_message(message.chat.id, message_id)
        except aiogram.utils.exceptions.MessageToDeleteNotFound:
            pass
    await state.finish()
    user_name = message.from_user.first_name
    markup = InlineKeyboardMarkup(row_width=1)
    button1 = InlineKeyboardButton("Я купил(а) товар", callback_data='bought')
    button2 = InlineKeyboardButton("Я не купил(а) товар", callback_data='not_bought')
    markup.add(button1, button2)

    await message.answer(
        f"Здравствуйте, {user_name}! Бренд Dave&Ante рада вашему присутствию в нашем чат-боте.\n"
        "Подтвердите пожалуйста покупку товара, сделав фотографию товара (не в пункте выдачи заказов).",
        reply_markup=markup
    )


if __name__ == '__main__':
    executor.start_polling(dp)
