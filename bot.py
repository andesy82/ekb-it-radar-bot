import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "YOUR_BOT_TOKEN")

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

EVENTS_DB = [
    {
        "title": "ENIGMA HACK 2026 (УрФУ / ИРИТ-РТФ)",
        "date": "5–6 декабря",
        "location": "Екатеринбург, Мира 32",
        "tags": ["Python", "Web", "AI", "Хакатон"],
        "url": "https://urfu.ru"
    },
    {
        "title": "Ural C# & .NET Meetup",
        "date": "12 декабря",
        "location": "Екатеринбург, Ельцин Центр",
        "tags": ["C#", "Backend", "Митап"],
        "url": "https://ekb-it.ru"
    },
    {
        "title": "Контур.Старт — отбор на стажировку",
        "date": "До 20 декабря",
        "location": "Екатеринбург / Онлайн",
        "tags": ["Python", "C#", "Web", "Стажировка"],
        "url": "https://kontur.ru"
    }
]

user_subscriptions: dict[int, str] = {}


def get_main_menu() -> types.ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.button(text="🔥 Все события Екб")
    builder.button(text="🎯 Выбрать стек / тег")
    builder.button(text="🔔 Моя подписка")
    builder.adjust(2, 1)
    return builder.as_markup(resize_keyboard=True)


def get_tags_keyboard() -> types.InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for tag in ["Python", "C#", "Web", "AI", "Хакатон", "Стажировка"]:
        builder.button(text=f"#{tag}", callback_data=f"tag_{tag}")
    builder.adjust(3, 3)
    return builder.as_markup()


def format_event(event: dict) -> str:
    tags_str = " ".join(f"#{t}" for t in event["tags"])
    return (
        f"📌 <b>{event['title']}</b>\n"
        f"📅 <b>Когда:</b> {event['date']}\n"
        f"📍 <b>Где:</b> {event['location']}\n"
        f"🏷 <b>Теги:</b> {tags_str}\n"
        f"🔗 <a href='{event['url']}'>Подробнее и регистрация</a>"
    )


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        f"Привет, {message.from_user.first_name}! 👋\n\n"
        f"Я <b>EKB IT Radar</b> — бот для поиска хакатонов, митапов и стажировок в Екатеринбурге.\n"
        f"Выбери действие в меню ниже:",
        reply_markup=get_main_menu(),
        parse_mode="HTML"
    )


@dp.message(F.text == "🔥 Все события Екб")
async def show_all_events(message: types.Message):
    for event in EVENTS_DB:
        await message.answer(format_event(event), parse_mode="HTML", disable_web_page_preview=True)


@dp.message(F.text == "🎯 Выбрать стек / тег")
async def choose_tag(message: types.Message):
    await message.answer(
        "Выбери направление, чтобы отфильтровать события и подписаться на уведомления:",
        reply_markup=get_tags_keyboard()
    )


@dp.callback_query(F.data.startswith("tag_"))
async def process_tag_selection(callback: types.CallbackQuery):
    selected_tag = callback.data.split("_", 1)[1]
    user_subscriptions[callback.from_user.id] = selected_tag

    filtered = [e for e in EVENTS_DB if selected_tag in e["tags"]]
    await callback.message.answer(
        f"✅ Подписка оформлена на тег <b>#{selected_tag}</b>!\n"
        f"Найдено актуальных событий: {len(filtered)}",
        parse_mode="HTML"
    )
    for event in filtered:
        await callback.message.answer(format_event(event), parse_mode="HTML", disable_web_page_preview=True)
    await callback.answer()


@dp.message(F.text == "🔔 Моя подписка")
async def my_subscription(message: types.Message):
    tag = user_subscriptions.get(message.from_user.id)
    if tag:
        await message.answer(f"Ты подписан на уведомления по тегу: <b>#{tag}</b>", parse_mode="HTML")
    else:
        await message.answer("У тебя пока нет активной подписки. Нажми «🎯 Выбрать стек / тег».")


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
