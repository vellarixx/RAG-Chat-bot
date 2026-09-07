import asyncio
import aiohttp
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart

# Вставьте ваши токены
TG_TOKEN = "8339710252:AAHbEKLox4bgsXtB19qvX46eC-pfoQ1TFQc"
DIFY_API_KEY = "app-tofdtfMcQR9p2ms93pxuNdqZ"
DIFY_URL = "http://localhost/v1/chat-messages"  # Если Dify на другом порту, укажите его (например, :5001)

bot = Bot(token=TG_TOKEN)
dp = Dispatcher()

# Словарь для сохранения связки чата Telegram и диалога Dify (conversation_id)
user_conversations = {}

async def ask_dify(query: str, user_id: str) -> str:
    headers = {
        "Authorization": f"Bearer {DIFY_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "inputs": {},
        "query": query,
        "response_mode": "blocking",
        "user": user_id,
        "conversation_id": user_conversations.get(user_id, "")
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post(DIFY_URL, json=payload, headers=headers) as resp:
            if resp.status == 200:
                data = await resp.json()
                # Сохраняем conversation_id, чтобы бот помнил контекст диалога
                user_conversations[user_id] = data.get("conversation_id", "")
                return data.get("answer", "Пустой ответ от модели.")
            else:
                text_error = await resp.text()
                return f"Ошибка Dify ({resp.status}): {text_error}"

@dp.message(CommandStart())
async def start_cmd(message: types.Message):
    await message.answer("Здравствуйте! Я AI-ассистент FreshFit. Задайте мне любой вопрос по доставке, меню или тарифам.")

@dp.message()
async def handle_message(message: types.Message):
    await bot.send_chat_action(message.chat.id, "typing")
    user_id = str(message.from_user.id)
    answer = await ask_dify(message.text, user_id)
    await message.answer(answer)

async def main():
    print("Бот запущен и подключен к локальному Dify!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())