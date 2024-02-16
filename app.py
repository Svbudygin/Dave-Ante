from aiogram import Bot, Dispatcher, types
from aiogram import executor

from config import api_token

API_TOKEN = api_token
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)





@dp.message_handler(commands=['start'])
async def info(message: types.Message):
    if message.chat.type != "private":
        chat_member = await bot.get_chat_member(message.chat.id, message.from_user.id)
        if chat_member.status in ['administrator', 'creator']:
            markup = types.InlineKeyboardMarkup()
            btm1 = types.InlineKeyboardButton('LAaG', callback_data='LAaG')
            btm2 = types.InlineKeyboardButton('DM', callback_data='DM')
            btm3 = types.InlineKeyboardButton('Calculus',
                                              url='https://drive.google.com/drive/u/0/folders/1VRz-N8Nz4B_QEi0aXKz0556NX4gxwV6Q')
            btm4 = types.InlineKeyboardButton('C++', callback_data='Cpp')
            markup.row(btm1, btm3)
            markup.row(btm2, btm4)
            await message.answer('Choose a subject:', reply_markup=markup)
    else:
        markup = types.InlineKeyboardMarkup()
        btm1 = types.InlineKeyboardButton('LAaG', callback_data='LAaG')
        btm2 = types.InlineKeyboardButton('DM', callback_data='DM')
        btm3 = types.InlineKeyboardButton('Calculus',
                                          url='https://drive.google.com/drive/u/0/folders/1VRz-N8Nz4B_QEi0aXKz0556NX4gxwV6Q')
        btm4 = types.InlineKeyboardButton('C++', callback_data='Cpp')
        markup.row(btm1, btm3)
        markup.row(btm2, btm4)
        await message.answer('Choose a subject:', reply_markup=markup)




if __name__ == '__main__':
    executor.start_polling(dp)
