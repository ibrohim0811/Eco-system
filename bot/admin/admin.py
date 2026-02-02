import asyncio
import logging
import os
from aiogram import Router, Bot, F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.exceptions import TelegramRetryAfter, TelegramForbiddenError, TelegramBadRequest
from aiogram.types import FSInputFile
from dotenv import load_dotenv


from updates.crud import get_all_tg_ids 
from updates.pdf import terminal_logs, save_terminal_to_pdf

load_dotenv()

dp_admin = Router()

class AdminStates(StatesGroup):
    waiting_broadcast_type = State()
    waiting_broadcast_content = State() 

ADMIN_IDS = [int(os.getenv("ADMIN_ID", 0))]
TOKEN = os.getenv("BOT_TOKEN")

def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS

@dp_admin.message(Command("send_message"))
async def cmd_send_message(message: types.Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        await message.answer("❌ Bu buyruq faqat admin uchun!")
        return

    await state.clear()
    await state.set_state(AdminStates.waiting_broadcast_type)

    kb = InlineKeyboardBuilder()
    kb.button(text="📝 Matn", callback_data="broadcast:text")
    kb.button(text="🖼 Rasm", callback_data="broadcast:photo")
    kb.button(text="🎞 Video", callback_data="broadcast:video")
    kb.adjust(1)

    await message.answer(
        "Qaysi turdagi xabar yuborasiz?\n\nBekor qilish uchun /cancel",
        reply_markup=kb.as_markup(),
    )

@dp_admin.callback_query(AdminStates.waiting_broadcast_type, F.data.startswith("broadcast:"))
async def cb_broadcast_type(callback: types.CallbackQuery, state: FSMContext):
    kind = callback.data.split(":")[1]
    await state.update_data(broadcast_kind=kind)
    
    await state.set_state(AdminStates.waiting_broadcast_content)
    
    texts = {
        "text": "📝 Matn yuboring.",
        "photo": "🖼 Rasm yuboring (izoh bilan bo'lishi mumkin).",
        "video": "🎞 Video yuboring (izoh bilan bo'lishi mumkin)."
    }
    
    await callback.message.edit_text(texts.get(kind, "Xabarni yuboring"))
    await callback.answer()

@dp_admin.message(Command("cancel"))
async def cmd_cancel_broadcast(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.clear()
    await message.answer("❌ Amaliyot bekor qilindi.")

async def _broadcast_send(bot: Bot, kind: str, message: types.Message) -> tuple[int, int]:
    user_ids = get_all_tg_ids()
    ok, fail = 0, 0
    
    for uid in user_ids:
        try:
            if kind == "text":
                await bot.send_message(uid, message.text)
            elif kind == "photo":
                await bot.send_photo(uid, photo=message.photo[-1].file_id, caption=message.caption)
            elif kind == "video":
                await bot.send_video(uid, video=message.video.file_id, caption=message.caption)
            
            ok += 1
            await asyncio.sleep(0.05) #
        except TelegramRetryAfter as e:
            await asyncio.sleep(e.retry_after)
        except (TelegramForbiddenError, TelegramBadRequest):
            fail += 1
        except Exception as e:
            logging.error(f"Xato {uid}: {e}")
            fail += 1
    return ok, fail

@dp_admin.message(AdminStates.waiting_broadcast_content)
async def handle_broadcast_content(message: types.Message, state: FSMContext, bot: Bot):
    if not is_admin(message.from_user.id):
        return

    data = await state.get_data()
    kind = data.get("broadcast_kind")

    # To'g'ri format yuborilganini tekshirish
    if kind == "text" and not message.text:
        return await message.answer("Iltimos, faqat matn yuboring.")
    if kind == "photo" and not message.photo:
        return await message.answer("Iltimos, rasm yuboring.")
    if kind == "video" and not message.video:
        return await message.answer("Iltimos, video yuboring.")

    sent_msg = await message.answer("⏳ Tarqatish boshlandi...")
    ok, fail = await _broadcast_send(bot, kind, message)
    
    await state.clear()
    await sent_msg.edit_text(f"✅ Yakunlandi!\n\nmuvaffaqiyatli: {ok}\nXato: {fail}")
    
    
# --- 4. HANDLERLAR ---

import datetime

@dp_admin.message(Command("log"))
async def cmd_get_terminal_log(message: types.Message):
    """Terminal loglarini PDF ko'rinishida yuboradi"""
    if not is_admin(message.from_user.id):
        return

    # Tekshiruv uchun bitta log yozamiz
    print(f"Admin {message.from_user.id} log so'radi.")
    
    status_msg = await message.answer("🔄 PDF tayyorlanmoqda...")
    
    try:
        pdf_path = save_terminal_to_pdf()
        if pdf_path:
            document = FSInputFile(pdf_path)
            await message.answer_document(
                document, 
                caption=f"📄 Terminal loglari\nVaqt: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}"
            )
            await status_msg.delete()
        else:
            await status_msg.edit_text("📭 Terminal xotirasi bo'sh.")
    except Exception as e:
        logging.error(f"PDF xatosi: {e}")
        await status_msg.edit_text(f"❌ Xatolik yuz berdi: {e}")

@dp_admin.message(Command("clear_logs"))
async def cmd_clear_logs(message: types.Message):
    """Xotiradagi loglarni tozalaydi"""
    if not is_admin(message.from_user.id):
        return
    terminal_logs.clear()
    await message.answer("🧹 Terminal xotirasi tozalandi.")

# --- TEST PRINT ---
print(">>> SYSTEM: Terminal monitoring v2.0 activated.")
print(f">>> ADMINS: {ADMIN_IDS}")