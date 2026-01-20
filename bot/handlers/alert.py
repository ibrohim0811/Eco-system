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
async def vide_process(msg: types.Message, i18n: I18nContext, state:FSMContext):
    
    video = msg.video_note
    if video.file_size > 10 * 1024 * 1024:
        return await msg.answer("Video 10 MB dan katta!")

   
    video_ = msg.video_note
    user_obj = await sync_to_async(User.objects.get)(telegram_id=msg.from_user.id)
    
    activity = await sync_to_async(UserActivities.objects.create)(
        user=user_obj,
        amount=5000,
        region=user_obj.district,
        status="pending",
        video_file_id=video.file_id  # Modeldagi maydon nomi
    )
    
    global user_id
    user_id = msg.from_user.id
    
    user_obj = await sync_to_async(User.objects.get)(telegram_id=msg.from_user.id)

    await sync_to_async(UserActivities.objects.create)(
    user=user_obj,          
    amount=5000,
    region=user_obj.district,
    status="pending"
)
    await state.update_data(
        video=video.file_id, 
        user_id=msg.from_user.id,
        district=user_obj.district
    )

    await msg.answer(i18n("accepted"), reply_markup=main_menu(i18n))

    await bot.send_video_note(
    ADMIN_ID, 
    video_note=video.file_id, 
    reply_markup=sorov(activity.id)
)

    data = await state.get_data()
    reg = data.get("district")
    await bot.send_message(
    ADMIN_ID, 
    f"Foydalanuvchi: @{msg.from_user.username} (ID: {msg.from_user.id})\nTomonidan video \n\n {reg}"
)
        
@dp_a.callback_query(F.data.startswith("yes_"))
async def sendtogroup(callback: types.CallbackQuery, state: FSMContext, i18n: I18nContext):
    data = await state.get_data()
    video_id = data.get('video')
    u_id = data.get('user_id')      
    region = data.get('district')

    if not video_id:
        return await callback.answer("Video ma'lumotlari topilmadi!")

    
    await bot.send_video_note(GROUP_ID, video_id)
    await callback.message.delete()

    @sync_to_async
    def process_acceptance():
        try:
            with transaction.atomic():
                target_user = User.objects.select_for_update().get(telegram_id=u_id)
                target_user.balance += 5000
                target_user.save()

                UserActivities.objects.create(
                    user=target_user, 
                    amount=5000,
                    region=region,
                    status="accepted"
                )
                return True
        except Exception as e:
            print(f"Xatolik: {e}")
            return False

    success = await process_acceptance()
    if success:
        await bot.send_message(u_id, i18n.get("amount"), reply_markup=main_menu(i18n))
        await state.clear()
    else:
        await callback.answer("Xatolik yuz berdi")
    
@dp_a.callback_query(F.data.startswith("no_"))
async def decline(i18n: I18nContext):
    await i18n.set_locale(DEFAULT_LANGUAGE)
    await bot.send_message(user_id, i18n("declined"), reply_markup=main_menu(i18n))