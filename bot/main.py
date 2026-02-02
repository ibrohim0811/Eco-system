import os
import sys
import django

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "root.settings")
django.setup()

import asyncio
import logging
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from pathlib import Path
from aiogram import types
from aiogram_i18n import I18nContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext

from dotenv import load_dotenv
from middleware.i18n import i18n_middleware
from aiogram_i18n.context import I18nContext
from states.state import Register
from asgiref.sync import sync_to_async
from handlers.alert import dp_a as alert
from handlers.questions import dp_ai as ai
from handlers.offer import dp_oai as oai
from handlers.about_us import dp_us 
from admin.admin import dp_admin
from handlers.forgot_password import dp_p
from app.models import User
from updates.pdf import generate_users_pdf
from updates.crud import get_all_users_from_db, get_all_tg_ids
from aiogram.exceptions import TelegramForbiddenError
from buttons.default import (
    main_menu, settings as settings_kb, 
    contact, regions
)

from buttons.inline import settings_lang

#validations

from validation.validate import validate_phone_number

#service
from app.utils import create_user_from_bot

load_dotenv()
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")
env_path = BASE_DIR / ".env"
dp = Dispatcher(storage=MemoryStorage())
i18n_middleware.setup(dispatcher=dp)
DEFAULT_LANGUAGE =  os.getenv("DEFAULT_LANGUAGE", "uz")
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMINS_RAW = os.getenv("ADMIN_ID")
ADMINS = [int(id.strip()) for id in ADMINS_RAW.split(",") if id.strip()]
CHAT_ADMIN = os.getenv("CHAT_ADMIN")


@dp.message(Command('start'))
async def start(message: types.Message, i18n: I18nContext, state: FSMContext):
    await i18n.set_locale(message.from_user.language_code)
    user_exists = sync_to_async(
    lambda: User.objects.filter(
        telegram_id=message.from_user.id
    ).exists()
)

    exists = await user_exists()
    if exists:
        await message.answer(f"{i18n('hello')} {message.from_user.first_name} {i18n('start_text')}", reply_markup=main_menu(i18n))
    else:
        await state.set_state(Register.first_name)
        await message.answer(i18n("text"))
        await message.answer(
            i18n("first_name")
        )
        
        

@dp.message(Register.first_name)
async def procees_fisrt_name(message: types.Message, i18n: I18nContext, state: FSMContext):
    first_name = message.text.strip().title()  
    await state.update_data(first_name=first_name)
    await message.answer(i18n("tel"), reply_markup=contact(i18n))
    await state.set_state(Register.phone)
    

@dp.message(Register.phone)
async def process_phone_number(message: types.Message, i18n: I18nContext, state: FSMContext):
    raw_phone = message.contact.phone_number if message.contact else message.text
    validated_phone = validate_phone_number(raw_phone)
    

    if validated_phone:
        
        await state.update_data(phone=f"+{validated_phone}") 
        await message.answer(i18n("region"), reply_markup=regions()) 
        await state.set_state(Register.region)
    else:
        
        await message.answer(i18n("err_tel"))
        
        
    
@dp.message(Register.region)
async def region_process(message: types.Message, i18n: I18nContext, state: FSMContext):
    REGIONS = ['Olmazor', 'Bektemir', 'Mirobod', 'Mirzo Ulug‘bek', 'Sergeli', 'Yangihayot', 'Uchtepa', 'Chilonzor', 'Shayxontohur', 'Yunusobod', 'Yakkasaroy', 'Yashnobod']
    
    
    balance = 0
    try:
        user = User.objects.filter(telegram_id=message.from_user.id)
        balance = user.balance
    except:
        balance += 0
    
    
    if message.text in REGIONS:
        await state.update_data(region=message.text)
        data = await state.get_data()
        name = data.get("first_name")
        tel = data.get("phone")
        region = data.get("region")
        
        create_user_async = sync_to_async(create_user_from_bot)
        
        user, username, password = await create_user_async(
        telegram_id=message.from_user.id,
        phone=tel,
        district=region,
        full_name=name,
        tg_username=message.from_user.username
        )

        if not user:
            await message.answer(i18n("err_saving"))
            return
    
        
        await message.answer(
            f"\n\n"
            f"🌐 Web login:\n"
            f"👤 {i18n('username')}: <b>{username}</b>\n"
            f"🔐 {i18n('parol')}: <b>{password}</b>\n\n"
            f" {i18n('save_password')} ",
            parse_mode="HTML"
        )
        await state.clear()
        await message.answer(i18n("alert"), reply_markup=main_menu(i18n))
    else:
        await state.set_state(Register.region)
        await message.answer(i18n("err_region"))
    

@dp.message(Command("alluser"))
async def all_user_stats(message: types.Message):
    if message.from_user.id not in ADMINS:
        return await message.answer("You are not granted admin rights. ❌")

    
    users = get_all_users_from_db()
    
    if not users:
        return await message.answer("📭 Foydalanuvchilar topilmadi.")

    # 2. PDF faylni yaratish
    pdf_file_path = generate_users_pdf(users)

    # 3. Yuborish
    await message.answer_document(
        types.FSInputFile(pdf_file_path),
        caption=f"📊 Barcha foydalanuvchilar ro'yxati\nJami: {len(users)} ta"
    )   


async def send_startup_notification(bot: Bot):
    # Bazadan barcha ID larni olamiz
    users = get_all_tg_ids()
    
    text = "🚀 **Diqqat! Bot tizimi yangilandi va qayta ishga tushdi.**\n\nEndi barcha funksiyalar yanada tezroq ishlaydi!\n Adminlar ishi yanada osonlashdi 😴\n Endi statiskani botdan turib kuzating 📈 !!"
    
    success = 0
    blocked = 0
    
    for user_id in users:
        try:
            await bot.send_message(chat_id=user_id, text=text, parse_mode="Markdown")
            success += 1
            
            await asyncio.sleep(0.05) 
        except TelegramForbiddenError:
            blocked += 1
        except Exception as e:
            print(f"Xatolik {user_id}: {e}")

    # Adminga hisobot yuborish
    


@dp.message(lambda message, i18n: message.text == i18n("settings"))
async def settings_handler(message: types.Message, i18n: I18nContext):
    await message.answer(i18n("settings"), reply_markup=settings_kb(i18n))

    

@dp.message(lambda message, i18n: message.text == i18n("change_lang"))
async def change_lang(message: types.Message, i18n: I18nContext):
    await message.answer(i18n("select_lang"), reply_markup=settings_lang(i18n))


#change to uzbek
@dp.callback_query(lambda c: c.data == "uzbek")
async def uzbek(callback: types.CallbackQuery, i18n: I18nContext):
    await i18n.set_locale("uz")
    await callback.message.answer(i18n("sucsess_lang"), reply_markup=main_menu(i18n))
    await callback.answer()
    
#rus 
@dp.callback_query(lambda c: c.data == "rus")
async def rus(callback: types.CallbackQuery, i18n: I18nContext):
    await i18n.set_locale("ru")
    await callback.message.answer(i18n("sucsess_lang"), reply_markup=main_menu(i18n))
    await callback.answer()

#ingliz 
@dp.callback_query(lambda c: c.data == "en")
async def english(callback: types.CallbackQuery, i18n: I18nContext):
    await i18n.set_locale("en")
    await callback.message.answer(i18n("sucsess_lang"), reply_markup=main_menu(i18n))
    

async def main():
    bot = Bot(token=BOT_TOKEN)
    # await send_startup_notification(bot)
    dp.update.middleware(i18n_middleware)
    dp.include_router(alert)
    dp.include_router(dp_admin)
    dp.include_router(ai)
    dp.include_router(oai)
    dp.include_router(dp_us)
    dp.include_router(dp_p)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    asyncio.run(main()) 
    