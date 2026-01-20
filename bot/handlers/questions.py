import os
from groq import AsyncGroq
from dotenv import load_dotenv
from buttons.default import main_menu
from aiogram import Bot, Dispatcher, Router, types, F
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext
from states.state import Questions
from aiogram_i18n.context import I18nContext
from aiogram.types import ReplyKeyboardRemove
from buttons.default import two_btn, ai_chat_menu

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=TOKEN)
dp_ai = Router()
bot=Bot(token=TOKEN)



client = AsyncGroq(api_key=os.getenv("GROQ_API_KEY"))

async def get_ai_response(prompt):
    try:
        chat_completion = await client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "Sen ekologiya va chiqindilarni qayta ishlash bo'yicha mutaxassis yordamchisan. Foydalanuvchi savollariga aniq va qisqa javob ber.Bir narsani esingdan chiqarma Seni Botga qo'shgan inson bu Ibrohim u Backend daturchi va aqllidir "
                },
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model="llama-3.3-70b-versatile", 
            temperature=0.7,
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        print(f"Groq Error: {e}")
        return "Kechirasiz, hozirda savolingizga javob bera olmayman."
    
@dp_ai.message(lambda message, i18n: message.text == i18n("offer"))
async def choose_ai(msg: types.Message, state: FSMContext, i18n: I18nContext):
    await msg.answer(i18n("choose"), reply_markup=two_btn(i18n))
    
@dp_ai.message(lambda message, i18n: message.text == i18n("quest"))
async def start_ai(msg: types.Message, state: FSMContext, i18n: I18nContext):
    await msg.answer(i18n("savol"), reply_markup=ReplyKeyboardRemove())
    await state.set_state(Questions.feedback)
    
@dp_ai.message(Questions.feedback)
async def process_ai_question(message: types.Message, state: FSMContext, i18n: I18nContext):
    user_question = message.text
    if message.text == i18n.get("exit_chat"):
        await state.clear()
        return await message.answer(
            "Bye.", 
            reply_markup=main_menu(i18n) 
        )
    # "Bot yozmoqda..." statusini chiqarish
    await bot.send_chat_action(chat_id=message.chat.id, action="typing")
    
    # AI dan javob olish
    ai_answer = await get_ai_response(user_question)
    
    # Javobni yuborish
    await message.answer(ai_answer, reply_markup=ai_chat_menu(i18n))
    
    