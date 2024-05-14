import asyncio
from aiogram import Bot, Dispatcher, types
import json
from config import token
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

bot = Bot(token=token)
dp = Dispatcher()


@dp.message(commands=['start'])
async def cmd_start(message: types.Message):
    await message.answer(f"Привет, {message.from_user.first_name}! Я бот новостей. Я могу предоставить тебе последние новости.",
                         reply_markup=types.ReplyKeyboardRemove())
    await asyncio.sleep(1)  # Чтобы дать боту немного времени на удаление клавиатуры
    await message.answer("Выберите пункт меню:", reply_markup=get_main_keyboard())


def get_main_keyboard():
    return types.ReplyKeyboardMarkup(keyboard=[
        [types.KeyboardButton(text='Все новости')]
    ],
                                     resize_keyboard=True,
                                     input_field_placeholder='Выберите пункт меню')


@dp.message(lambda message: message.text == 'Все новости')
async def send_all_news(message: types.Message, page: int = 1):
    with open("news_dict.json", "r", encoding="utf-8") as file:
        news_dict = json.load(file)

    if news_dict:
        news_per_page = 5
        start_index = (page - 1) * news_per_page
        end_index = start_index + news_per_page
        current_news = list(news_dict.values())[start_index:end_index]

        for article_info in current_news:
            news_text = (
                f"📰 <b>{article_info['article_title']}</b>\n"
                f"📝 {article_info['article_desc']}\n"
            )

            # Sending the photo
            await bot.send_photo(message.chat.id, article_info['article_img'])

            inline_button = InlineKeyboardButton(text='Читать', url=article_info['article_url'])
            inline_keyboard = InlineKeyboardMarkup(inline_keyboard=[[inline_button]])

            await message.answer(news_text, reply_markup=inline_keyboard, parse_mode='HTML')

        # Создаем InlineKeyboardMarkup с кнопками пагинации
        pagination_keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text='⬅️', callback_data=f'page_{page - 1}'),
                InlineKeyboardButton(text='➡️', callback_data=f'page_{page + 1}')
            ]
        ])

        await message.answer('Выберите действие:', reply_markup=pagination_keyboard)
    else:
        await message.answer("Нет доступных новостей.")


@dp.callback_query(lambda query: query.data.startswith('page_'))
async def handle_pagination(callback_query: types.CallbackQuery):
    page = int(callback_query.data.split('_')[1])
    await send_all_news(callback_query.message, page)



async def main():
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
