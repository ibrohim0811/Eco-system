from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram_i18n import I18nContext

def settings_lang(i18n: I18nContext) -> InlineKeyboardMarkup:
   
    _ = i18n
    
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=_("uz"), callback_data="uzbek"),
                InlineKeyboardButton(text=_("ru"), callback_data="rus"),
                InlineKeyboardButton(text=_("en"), callback_data="en")
            ]
        ]
    )
    
def sorov(activity_id) -> InlineKeyboardMarkup:
   
    
    
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Ha ✅", callback_data=f"yes_{activity_id}"),
                InlineKeyboardButton(text="Yo'q ❌", callback_data=f"no_{activity_id}"),
                
            ]
        ]
    )
    
def admin(i18n: I18nContext):
    
    _ = i18n
    
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=_("conn_admin"), url="https://web.telegram.org/a/#6794722763")
            ]
        ]
    )