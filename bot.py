import asyncio
import random
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.enums import ParseMode

# Токен вашего бота
TOKEN = "8174958630:AAEL17sRy6mOBweFUa9WRpVYCcbRiuj4fow"

# Хранилище данных
data = {}

bot = Bot(token=TOKEN)
dp = Dispatcher()

def get_top(chat_users):
    """Возвращает отсортированный список пользователей по глубине"""
    sorted_users = sorted(chat_users.items(), key=lambda x: x[1]["depth"], reverse=True)
    return [(user_id, info) for user_id, info in sorted_users]

def format_user_name(user: types.User) -> str:
    """Форматирует имя пользователя"""
    if user.username:
        return f"@{user.username}"
    return user.full_name

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.reply("Я бот для измерения 📏\nИспользуй команду:\n/pizda - измерить глубину\n/top_pizda - рейтинг")

@dp.message(Command("pizda"))
async def cmd_pizda(message: types.Message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    user_name = format_user_name(message.from_user)
    now = datetime.now()

    # Инициализация чата
    if chat_id not in data:
        data[chat_id] = {}

    # Инициализация пользователя
    if user_id not in data[chat_id]:
        data[chat_id][user_id] = {
            "depth": 0,
            "last_try": None,
            "name": user_name
        }

    user_data = data[chat_id][user_id]

    # Проверка на попытку завтра
    if user_data["last_try"] and now < user_data["last_try"]:
        wait_until = user_data["last_try"].strftime("%H:%M:%S")
        await message.reply(f"⏰ Следующая попытка завтра в {wait_until}!")
        return

    # Генерация глубины: от 1 до 15 см
    growth = random.randint(1, 15)
    user_data["depth"] += growth
    user_data["last_try"] = now + timedelta(days=1)
    user_data["name"] = user_name

    # Получаем топ
    top_list = get_top(data[chat_id])
    
    # Находим место пользователя
    place = 1
    for pos, (uid, info) in enumerate(top_list, 1):
        if uid == user_id:
            place = pos
            break

    # Формируем ответ
    response = (
        f"📏 *{user_name}, твоя пизда углубилась на {growth} см.*\n"
        f"🕳️ *Теперь её глубина составляет {user_data['depth']} см.*\n"
        f"🏆 *Ты занимаешь {place} место в топе*\n"
        f"⏳ *Следующая попытка завтра!*"
    )

    await message.reply(response, parse_mode=ParseMode.MARKDOWN)

@dp.message(Command("top_pizda"))
async def cmd_top_pizda(message: types.Message):
    chat_id = message.chat.id
    
    if chat_id not in data or not data[chat_id]:
        await message.reply("📊 Топ пока пуст. Используй /pizda чтобы начать!")
        return
    
    top_list = get_top(data[chat_id])[:10]
    
    text = "*🏆 ТОП ГЛУБИНЫ ПИЗДЫ 🏆*\n\n"
    for i, (user_id, info) in enumerate(top_list, 1):
        name = info.get("name", f"User {user_id}")
        depth = info["depth"]
        text += f"{i}. {name} — {depth} см\n"
    
    await message.reply(text, parse_mode=ParseMode.MARKDOWN)

async def main():
    print("🤖 Бот запущен...")
    print("Доступные команды: /pizda, /top_pizda, /start")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())