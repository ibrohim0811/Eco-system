import json
import os
from groq import AsyncGroq
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, Router, types, F
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext
from bot.states.state import FeedbackState
from aiogram_i18n.context import I18nContext
from aiogram.types import ReplyKeyboardRemove
from buttons.default import two_btn, ai_chat_menu, main_menu
from buttons.inline import sorov
from django.db import transaction
from app.models import User
from asgiref.sync import sync_to_async

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
CHAT_ADMIN = os.getenv("CHAT_ADMIN")
bot = Bot(token=TOKEN)
dp_oai = Router()
bot=Bot(token=TOKEN)

client = AsyncGroq(api_key=os.getenv("GROQ_API_KEY"))

async def analyze_feedback(text):
    try:
        chat_completion = await client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Sen kelib tushgan takliflarni tahlil qiluvchi yordamchisan. "
                        "Taklifni quyidagi mezonlar bo'yicha bahola: "
                        "1. Rasmiylik darajasi. 2. Ma'nosi borligi (feyk emasligi). 3. Tushunarliligi. "
                        "Javobni FAQAT JSON formatida qaytar: "
                        '{"is_valid": true/false, "reason": "sababi", "formal_text": "tahrirlangan matn"}'
                    )
                },
                {"role": "user", "content": text}
            ],
            model="llama-3.3-70b-versatile",
            response_format={"type": "json_object"} # JSON formatini majburlaymiz
        )
        return json.loads(chat_completion.choices[0].message.content)
    except Exception as e:
        print(f"Analizda xato: {e}")
        return {"is_valid": False, "reason": "Xatolik yuz berdi"}

@dp_oai.message(lambda message, i18n: message.text == i18n("off_er"))
async def start_ai(msg: types.Message, state: FSMContext, i18n: I18nContext):
    await msg.answer(i18n("savol"), reply_markup=ReplyKeyboardRemove())
    await state.set_state(FeedbackState.waiting_for_feedback)

@dp_oai.message(FeedbackState.waiting_for_feedback)
async def process_ai_and_feedback(message: types.Message, state: FSMContext, i18n: I18nContext):
    
    if message.text == i18n.get("exit_chat"):
        await state.clear()
        return await message.answer("Suhbat yakunlandi.", reply_markup=main_menu(i18n))

    
    waiting_msg = await message.answer("🔍")
    analysis = await analyze_feedback(message.text)

    if analysis.get("is_valid"):
        
        formal_text = analysis.get("formal_text")
        global user_id
        user_id = message.from_user.id
        admin_text = (
            f"✅ **Yangi rasmiy taklif!**\n\n"
            f"👤 Kimdan: {message.from_user.full_name}\n"
            f"original: {message.text}\n"
            f"✨ AI tahriri: {formal_text}"
        )
        
        await bot.send_message(CHAT_ADMIN, admin_text, reply_markup=sorov())
        
        await waiting_msg.edit_text(
            "Rahmat! Taklifingiz tahlil qilindi va adminga yuborildi. ✅\n"
            
        )
        await message.answer("Yana biror nima yozasizmi yoki suhbatni yakunlaysizmi?",
            reply_markup=ai_chat_menu(i18n))
    else:
        
        reason = analysis.get("reason")
        await waiting_msg.edit_text(
            f"Kechirasiz, taklifingiz qabul qilinmadi. ❌\n"
            f"Sabab: {reason}\n"
            "Iltimos, aniqroq va rasmiyroq shaklda yozing."
        )
        
@dp_oai.callback_query(F.data == "yes")
async def sendtogroup(callback: types.CallbackQuery, state: FSMContext, i18n: I18nContext):

    @sync_to_async
    def process_acceptance():
        try:
            with transaction.atomic():
                target_user = User.objects.select_for_update().get(telegram_id=user_id)
                target_user.balance += 2000
                target_user.save()

                return True
        except Exception as e:
            print(f"Xatolik: {e}")
            return False

    success = await process_acceptance()
    if success:
        await bot.send_message(user_id, i18n.get("amount"), reply_markup=main_menu(i18n))
        await state.clear()
    else:
        await callback.answer("Xatolik yuz berdi")
    
@dp_oai.callback_query(F.data == "no")
async def decline(callback: types.CallbackQuery, state: FSMContext, i18n: I18nContext):
    await bot.send_message(user_id, i18n("declined"), reply_markup=main_menu(i18n))