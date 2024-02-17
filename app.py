import aiogram
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram import Bot, Dispatcher, executor, types
from config import api_token, Admin_sergo_id, Admin_electro_id
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from mail import send_email, send_email_with_photo

message_delete = {}
API_TOKEN = api_token
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())


class Form(StatesGroup):
    name_state = State()
    age_state = State()
    city_state = State()
    feedback_state = State()
    from_proof_to_feedback_state = State()
    from_what_u_find_item_state = State()


# @dp.message_handler(commands=['start'])
# async def process_start_command(message: types.Message, state: FSMContext):
#     msg3 = await message.answer("Здравствуйте!👋\nПросим Вас указать ваши данные. Как Вас зовут?")
#     message_delete[message.chat.id] = [msg3.message_id]
#     print(message.from_user.id)
#     await Form.name_state.set()
@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message, state: FSMContext):
    channel_link = 'https://t.me/+bFibV6s-K-o3ZjZi'
    markup = InlineKeyboardMarkup(row_width=1)
    button1 = InlineKeyboardButton("Подписаться", url=channel_link)
    button2 = InlineKeyboardButton("Проверить подписку", callback_data="check_subscr")
    markup.add(button1, button2)
    await message.answer(f"Здравствуйте! Подпишитесь, пожалуйста, на наш канал", reply_markup=markup)


@dp.callback_query_handler(lambda query: query.data in {'check_subscr'})
async def bought_item1(callback_query: types.CallbackQuery, state: FSMContext):
    channel_id = -1002122669585
    print(callback_query.message.from_user)
    user = await bot.get_chat_member(chat_id=channel_id, user_id=callback_query.from_user.id)
    is_subscribed = user.status == 'member' or user.status == 'creator' or user.status == 'administrator'
    print(user.status)
    if is_subscribed:
        msg3 = await bot.edit_message_text(
            chat_id=callback_query.message.chat.id,
            message_id=callback_query.message.message_id,
            text="Здравствуйте!👋\nПросим Вас указать ваши данные. Как Вас зовут?"
        )
        message_delete[callback_query.message.chat.id] = [msg3.message_id]
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
    async with state.proxy() as data:
        data['name_of_user'] = name_of_user
    msg3 = await message.answer(f"Отлично, {name_of_user}, приятно познакомиться! Введите Ваш возраст:")
    message_delete[message.chat.id] = [msg3.message_id]
    await Form.age_state.set()


@dp.message_handler(state=Form.age_state)
async def process_age(message: types.Message, state: FSMContext):
    age_of_user = message.text
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
        await bot.edit_message_text(
            chat_id=callback_query.message.chat.id,
            message_id=callback_query.message.message_id,
            text="Жаль, что вы не купили товар. Может быть в следующий раз!", reply_markup=None

        )
        await state.finish()
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
    button4 = InlineKeyboardButton("У вас есть вопросы к нам?", callback_data='questions')
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
            text="Наши специалисты готовы ответить на все ваши вопросы. Чем мы можем помочь вам?")
        await Form.feedback_state.set()
    elif callback_query.data == 'improve':
        await bot.edit_message_text(
            chat_id=callback_query.message.chat.id,
            message_id=callback_query.message.message_id,
            text="Мы готовы внимательно рассмотреть ваши предложения по совершенствованию нашего продукта и скажите, пожалуйста, как нашли наш товар:"
        )
        await Form.feedback_state.set()


@dp.message_handler(state=Form.feedback_state)
async def feedback_func(message: types.Message, state: FSMContext):
    markup = InlineKeyboardMarkup(row_width=1)
    button1 = InlineKeyboardButton("Участвовать в розыгрыше!", callback_data='drawing')
    markup.add(button1)
    await bot.send_message(message.chat.id,
                           "Благодарим вас за предоставленную информацию.С уважением команда Dave&Ante",
                           reply_markup=markup)
    feedback_from_user = message.text
    async with state.proxy() as data:
        text_to_admin = f"Name: {data['name_of_user']}\nAge: {data['age_of_user']}\nCity: {data['city_of_user']}\nКомментарий ({data['FeedbackType']}): {feedback_from_user}"
        await bot.send_photo(chat_id=Admin_sergo_id,
                             photo=data['photo'],
                             caption=text_to_admin)

    file_info = await bot.get_file(data['photo'])
    file_path = file_info.file_path

    file_url = f"https://api.telegram.org/file/bot{API_TOKEN}/{file_path}"
    print(send_email_with_photo('mishalogv@ya.ru', text_to_admin, file_url))
    await state.finish()


if __name__ == '__main__':
    executor.start_polling(dp)
