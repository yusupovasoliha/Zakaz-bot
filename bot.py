from aiogram import Bot, Dispatcher, types
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils import executor

API_TOKEN = "TOKEN"
CHANNEL_ID = "@kanal_username"
ADMIN_ID = 123456789

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

user_data = {}
menu_items = ["🍦 Shokoladli", "🍦 Vanilli"]

def get_menu():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    for item in menu_items:
        kb.add(item)
    return kb

@dp.message_handler(commands=['start'])
async def start_handler(message: Message):
    if message.from_user.id == ADMIN_ID:
        text = "👑 Admin panel:\n/start\n/menu\n/zakaz\n/qo'shish\n/o'chirish"
    else:
        text = "👤 User panel:\n/start\n/menu\n/zakaz"
    await message.answer(text)

@dp.message_handler(commands=['menu'])
async def menu_handler(message: Message):
    await message.answer("📋 Menu:", reply_markup=get_menu())

@dp.message_handler(commands=['zakaz'])
async def zakaz_handler(message: Message):
    btn = KeyboardButton("📱 Telefon yuborish", request_contact=True)
    kb = ReplyKeyboardMarkup(resize_keyboard=True).add(btn)

    user_data[message.from_user.id] = {"step": "phone"}
    await message.answer("📞 Telefon raqamingizni yuboring:", reply_markup=kb)

@dp.message_handler(content_types=types.ContentType.CONTACT)
async def contact_handler(message: Message):
    user_id = message.from_user.id

    if user_id not in user_data or user_data[user_id]["step"] != "phone":
        return

    phone = message.contact.phone_number

    if not phone.startswith("+998"):
        await message.answer("❌ Nomer noto‘g‘ri!")
        return

    user_data[user_id]["phone"] = phone
    user_data[user_id]["step"] = "menu"

    await message.answer("🍦 Tanlang:", reply_markup=get_menu())

@dp.message_handler(lambda message: message.text in menu_items)
async def order_handler(message: Message):
    user_id = message.from_user.id

    if user_id not in user_data:
        return

    phone = user_data[user_id].get("phone")
    item = message.text

    text = f"📥 Yangi zakaz!\n\n📱 {phone}\n🍦 {item}"

    await bot.send_message(CHANNEL_ID, text)
    await message.answer("✅ Zakaz yuborildi!")

    del user_data[user_id]

@dp.message_handler(commands=["qo'shish"])
async def add_item(message: Message):
    if message.from_user.id != ADMIN_ID:
        return

    user_data[message.from_user.id] = {"step": "add"}
    await message.answer("➕ Yangi mahsulot nomini yozing:")

@dp.message_handler(lambda message: user_data.get(message.from_user.id, {}).get("step") == "add")
async def save_item(message: Message):
    menu_items.append(message.text)
    await message.answer("✅ Qo‘shildi!")
    user_data.pop(message.from_user.id)

@dp.message_handler(commands=["o'chirish"])
async def delete_item(message: Message):
    if message.from_user.id != ADMIN_ID:
        return

    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    for item in menu_items:
        kb.add(item)

    user_data[message.from_user.id] = {"step": "delete"}
    await message.answer("❌ Qaysini o‘chirasiz?", reply_markup=kb)

@dp.message_handler(lambda message: user_data.get(message.from_user.id, {}).get("step") == "delete")
async def remove_item(message: Message):
    if message.text in menu_items:
        menu_items.remove(message.text)
        await message.answer("✅ O‘chirildi!")
    else:
        await message.answer("❌ Topilmadi!")

    user_data.pop(message.from_user.id)

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
