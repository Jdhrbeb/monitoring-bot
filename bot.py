import asyncio
import database
from openpyxl import Workbook
from aiogram.types import FSInputFile

from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import Command

from config import BOT_TOKEN

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

ADMIN_ID = 6997621411

def is_admin(user_id):
    return user_id == ADMIN_ID

with open("bad_words.txt", "r", encoding="utf-8") as file:
    BAD_WORDS = [
        line.strip().lower()
        for line in file
        if line.strip()
    ]


@dp.message(Command("stats"))
async def stats_command(message: Message):

    if not is_admin(message.from_user.id):
        await message.answer(
            "⛔ Sizda ushbu buyruqni ishlatish huquqi yo‘q."
        )
        return

    total, normal, bad = database.get_statistics()

    await message.answer(
        f"📊 Statistika\n\n"
        f"Jami xabarlar: {total}\n"
        f"Normal xabarlar: {normal}\n"
        f"Nomaqbul xabarlar: {bad}"
    )

@dp.message(Command("risk"))
async def risk_command(message: Message):

    if not is_admin(message.from_user.id):
        await message.answer(
            "⛔ Sizda ushbu buyruqni ishlatish huquqi yo‘q."
        )
        return

    risk = database.get_risk_score()

    if risk < 20:
        level = "🟢 Past"

    elif risk < 50:
        level = "🟡 O‘rta"

    else:
        level = "🔴 Yuqori"

    await message.answer(
        f"⚠️ Risk tahlili\n\n"
        f"Risk Score: {risk}/100\n"
        f"Daraja: {level}"
    )



@dp.message(Command("topusers"))
async def top_users_command(message: Message):

    if not is_admin(message.from_user.id):
        await message.answer(
            "⛔ Sizda ushbu buyruqni ishlatish huquqi yo‘q."
        )
        return

    users = database.get_top_users()

    if not users:
        await message.answer("Ma'lumot topilmadi.")
        return

    text = "🏆 Eng faol foydalanuvchilar\n\n"

    for i, (username, count) in enumerate(users, start=1):
        text += f"{i}. {username} — {count} ta xabar\n"

    await message.answer(text)

@dp.message(Command("report"))
async def report_command(message: Message):

    if not is_admin(message.from_user.id):
        await message.answer(
            "⛔ Sizda ushbu buyruqni ishlatish huquqi yo‘q."
        )
        return

    rows = database.get_last_messages()

    if not rows:
        await message.answer("Ma'lumot topilmadi.")
        return

    text = "📋 Oxirgi xabarlar\n\n"

    for username, status, msg in rows:

        text += (
            f"👤 {username}\n"
            f"📌 {status}\n"
            f"💬 {msg[:30]}\n\n"
        )

    await message.answer(text)

@dp.message(Command("export"))
async def export_command(message: Message):

    if not is_admin(message.from_user.id):
        await message.answer(
            "⛔ Sizda ushbu buyruqni ishlatish huquqi yo‘q."
        )
        return

    rows = database.get_all_messages()

    wb = Workbook()
    ws = wb.active

    ws.title = "Monitoring"

    ws.append([
        "Foydalanuvchi",
        "Xabar",
        "Status",
    ])

    for row in rows:
        ws.append(row)

    file_name = "monitoring_report.xlsx"
    wb.save(file_name)

    document = FSInputFile(file_name)

    await message.answer_document(
        document,
        caption="📊 Monitoring hisoboti"
    )

@dp.message(Command("addword"))
async def add_word(message: Message):

    if not is_admin(message.from_user.id):
        await message.answer(
            "⛔ Sizda ushbu buyruqni ishlatish huquqi yo‘q."
        )
        return

    parts = message.text.split(maxsplit=1)

    if len(parts) < 2:
        await message.answer(
            "Foydalanish:\n/addword so'z"
        )
        return

    new_word = parts[1].strip().lower()

    with open("bad_words.txt", "a", encoding="utf-8") as file:
        file.write(f"\n{new_word}")

    BAD_WORDS.append(new_word)

    await message.answer(
        f"✅ '{new_word}' so‘zi qo‘shildi."
    )

@dp.message(Command("delword"))
async def delete_word(message: Message):

    if not is_admin(message.from_user.id):
        await message.answer(
            "⛔ Sizda ushbu buyruqni ishlatish huquqi yo‘q."
        )
        return

    parts = message.text.split(maxsplit=1)

    if len(parts) < 2:
        await message.answer(
            "Foydalanish:\n/delword so'z"
        )
        return

    word = parts[1].strip().lower()

    if word not in BAD_WORDS:
        await message.answer(
            "❌ Bu so‘z bazada topilmadi."
        )
        return

    BAD_WORDS.remove(word)

    with open("bad_words.txt", "w", encoding="utf-8") as file:
        for item in BAD_WORDS:
            file.write(item + "\n")

    await message.answer(
        f"🗑 '{word}' so‘zi o‘chirildi."
    )
    
@dp.message(Command("myid"))
async def my_id(message: Message):
    await message.answer(
        f"Sizning ID: {message.from_user.id}"
    )

@dp.message()
async def monitor_message(message: Message):

    text = (message.text or "").lower()

    if text.startswith("/"):
        return

    for word in BAD_WORDS:

        if word in text:

            database.save_message(
                message.from_user.full_name,
                text,
                "bad"
            )
            print("BAN BAJARILDI")

            await bot.ban_chat_member(
                chat_id=message.chat.id,
                user_id=message.from_user.id
            )
            print("BAN BAJARILDI")

            await message.answer(
                f"⛔ {message.from_user.full_name} nomaqbul so‘z ishlatgani uchun guruhdan chiqarildi."
            )

            return

    database.save_message(
        message.from_user.full_name,
        text,
        "normal"
    )


async def main():
    print("Bot ishga tushdi...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
