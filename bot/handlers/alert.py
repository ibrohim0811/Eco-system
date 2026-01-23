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
 

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "root.settings")
django.setup()


from app.models import User, UserActivities 

from asgiref.sync import sync_to_async
from middleware.i18n import i18n_middleware 
from aiogram_i18n.context import I18nContext
from buttons.default import regions
from states.state import EcoAlert
from buttons.inline import sorov
from buttons.default import main_menu

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = os.getenv("ADMIN_ID")
GROUP_ID = os.getenv("GROUP_ID")
DEFAULT_LANGUAGE = os.getenv("DEFAULT_LANGUAGE")
print(GROUP_ID)
bot = Bot(token=TOKEN)
dp_a = Router()



@dp_a.message(lambda message, i18n: message.text == i18n("eco_alert"))
async def alert_start(msg: types.Message, i18n: I18nContext, state:FSMContext):
    await msg.answer(i18n("alert_info"))
    await msg.answer(i18n("alert_button"), reply_markup=regions())
    await state.set_state(EcoAlert.district)
    
@dp_a.message(EcoAlert.district)
async def alert_process1(msg: types.Message, i18n: I18nContext, state:FSMContext):
    REGIONS = ['Olmazor', 'Bektemir', 'Mirobod', 'Mirzo Ulug‘bek', 'Sergeli', 'Yangihayot', 'Uchtepa', 'Chilonzor', 'Shayxontohur', 'Yunusobod', 'Yakkasaroy', 'Yashnobod']
    
    if msg.text in REGIONS:
        await state.update_data(district=msg.text)
        await msg.answer(i18n("attend"), reply_markup=ReplyKeyboardRemove())
        await state.set_state(EcoAlert.video)
        
    else:
        await state.set_state(EcoAlert.district)
        await msg.answer(i18n("alert_button"), reply_markup=regions())
        
@dp_a.message(EcoAlert.video, F.video_note)
async def vide_process(msg: types.Message, i18n: I18nContext, state: FSMContext):
    video = msg.video_note
    if video.file_size > 10 * 1024 * 1024:
        return await msg.answer("Video 10 MB dan katta!")

    # Userni bazadan olamiz
    user_obj = await sync_to_async(User.objects.get)(telegram_id=msg.from_user.id)
    
    # FAQAT BIR MARTA yaratamiz
    activity = await sync_to_async(UserActivities.objects.create)(
        user=user_obj,
        amount=5000,
        region=user_obj.district,
        status="pending",
        video_file_id=video.file_id
    )
    
    # State'ni yangilaymiz
    await state.update_data(
        video=video.file_id, 
        user_id=msg.from_user.id,
        district=user_obj.district
    )

    await msg.answer(i18n("accepted"), reply_markup=main_menu(i18n))

    # Adminga yuboramiz
    await bot.send_video_note(
        ADMIN_ID, 
        video_note=video.file_id, 
        reply_markup=sorov(activity.id)
    )

    await bot.send_message(
        ADMIN_ID, 
        f"Foydalanuvchi: @{msg.from_user.username} (ID: {msg.from_user.id})\nTumani: {user_obj.district}"
    )
        
@dp_a.callback_query(F.data.startswith("yes_"))
async def sendtogroup(callback: types.CallbackQuery, i18n: I18nContext):
   
    activity_id = callback.data.split("_")[1]

    @sync_to_async
    def process_acceptance():
        try:
            with transaction.atomic():
                
                activity = UserActivities.objects.select_related('user').select_for_update().get(id=activity_id)

                if activity.status == "accepted":
                    return "already_done", None

                
                target_user = activity.user
                target_user.balance += 5000
                target_user.save()

                
                activity.status = "accepted"
                activity.amount = 5000
                activity.save()

                return "success", activity
        except UserActivities.DoesNotExist:
            return "not_found", None
        except Exception as e:
            print(f"Xatolik: {e}")
            return "error", None

    
    result, activity = await process_acceptance()

    if result == "success":
       
        if activity.video_file_id:
            try:
                await bot.send_video_note(GROUP_ID, activity.video_file_id)
            except Exception as e:
                print(f"Video yuborishda xato: {e}")

        
        await callback.message.delete()
        
        
        u_id = activity.user.telegram_id 
        
        await bot.send_message(u_id, i18n.get("amount"), reply_markup=main_menu(i18n))
        await callback.answer("Tasdiqlandi!")

    elif result == "already_done":
        await callback.answer("Bu ariza allaqachon tasdiqlangan!")
    else:
        await callback.answer("Ma'lumot topilmadi yoki xatolik yuz berdi!")
    
@dp_a.callback_query(F.data.startswith("no_"))
async def decline(callback: CallbackQuery, i18n: I18nContext):
    await i18n.set_locale(DEFAULT_LANGUAGE)
    activity_id = callback.data.split("_")[1]

    
    activity = await sync_to_async(
        lambda: UserActivities.objects.select_related('user').select_for_update().get(id=activity_id)
    )()

    
    chat_id = activity.user.id  

    
    await bot.send_message(chat_id, i18n("declined"), reply_markup=main_menu(i18n))