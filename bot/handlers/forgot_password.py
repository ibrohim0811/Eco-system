import os
import sys
import django
from pathlib import Path
from aiogram import Bot, Dispatcher, Router, types, F
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext
from dotenv import load_dotenv
from aiogram.types import ReplyKeyboardRemove
from django.db import transaction
from aiogram.types import CallbackQuery
from aiogram_i18n.context import I18nContext


from states.state import ForgotPassword



load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = os.getenv("ADMIN_ID")
GROUP_ID = os.getenv("GROUP_ID")
DEFAULT_LANGUAGE = os.getenv("DEFAULT_LANGUAGE")
print(GROUP_ID)
bot = Bot(token=TOKEN)
dp_p = Router()


    
from aiogram import F, types, Router
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from django.contrib.auth.hashers import make_password
from app.models import User 
from asgiref.sync import sync_to_async

import requests
import uuid

import re

def normalize_phone(phone: str) -> str:
    return re.sub(r"[^\d+]", "", phone)


@sync_to_async
def get_user(tg_id, phone):
    return User.objects.get(
        telegram_id=tg_id,
        phone=phone
    )

@sync_to_async
def save_user(user):
    user.save()

# SMS yuborish funksiyasi (Eskiz.uz misolida)
def send_sms_eskiz(phone, message):
    token = os.getenv("ESKIZ_TOKEN")
    url = "https://notify.eskiz.uz/api/message/sms/send"

    data = {
        "mobile_phone": phone.replace("+", ""),
        "message": message,
        "from": "4545",
    }

    headers = {
        "Authorization": f"Bearer {token}"
    }

    res = requests.post(url, headers=headers, data=data)

    print("SMS STATUS:", res.status_code)
    print("SMS RESPONSE:", res.text)

    return res.status_code == 200



@dp_p.message(lambda message, i18n: message.text == i18n("forgot_password"))
async def ask_contact(message: types.Message, i18n: I18nContext):
    kb = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=i18n("tel"), request_contact=True)]],
        resize_keyboard=True
    )
    await message.answer(i18n("send_sms"), reply_markup=kb)


@dp_p.message(F.contact)
async def process_recovery(message: types.Message, i18n: I18nContext):
    if message.contact.user_id != message.from_user.id:
        await message.answer("❌ Faqat o‘z raqamingizni yuboring")
        return

    raw_phone = message.contact.phone_number
    phone = normalize_phone(raw_phone)

    tg_id = message.from_user.id

    try:
        user = await get_user(tg_id, phone)

        new_raw_pw = uuid.uuid4().hex[:6]
        user.password = make_password(new_raw_pw)
        await save_user(user)

        sms_text = (
            f"Sizning yangi kirish ma'lumotlaringiz:\n"
            f"Login: {user.username}\n"
            f"Parol: {new_raw_pw}"
        )

        if send_sms_eskiz(phone, sms_text):
            await message.answer(
                f"✅ {i18n('info')} {phone} {i18n('sended')}",
                reply_markup=ReplyKeyboardRemove()
            )
        else:
            await message.answer(i18n("not_found"), reply_markup=ReplyKeyboardRemove())
            await message.answer(f"🌐Web login \n\n login: {user.username} \n\n password: {new_raw_pw}")

    except User.DoesNotExist:
        await message.answer(i18n("not_found"), reply_markup=ReplyKeyboardRemove())
