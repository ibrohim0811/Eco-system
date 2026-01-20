from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram_i18n import I18nContext
from aiogram.utils.i18n import I18n 
from aiogram import types


def main_menu(i18n: I18nContext) -> ReplyKeyboardMarkup:
    _ = i18n
    
    
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=_("eco_alert"))
            ],
            [
                KeyboardButton(text=_("offer"))
            ],
            [
                KeyboardButton(text=_("about_us"))
            ],
            [
                KeyboardButton(text=_("settings"))
            ]
        ],
        resize_keyboard=True
    )
    
def settings(i18n: I18nContext) -> ReplyKeyboardMarkup:
    _ = i18n
    
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=_("change_lang"))
            ]
        ],
        resize_keyboard=True
        
    )
    
def contact(i18n: I18nContext) -> ReplyKeyboardMarkup:
    
    _ = i18n
    
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=_("tel"), request_contact=True)
            ]
        ],
        resize_keyboard=True
        
    )
    
def regions() -> ReplyKeyboardMarkup:
    
    return ReplyKeyboardMarkup(
        keyboard=[
        [KeyboardButton(text="Olmazor"), KeyboardButton(text="Bektemir")],
        [KeyboardButton(text="Mirobod"), KeyboardButton(text="Mirzo Ulug‘bek")],
        [KeyboardButton(text="Sergeli"), KeyboardButton(text="Yangihayot")],
        [KeyboardButton(text="Uchtepa"), KeyboardButton(text="Chilonzor")],
        [KeyboardButton(text="Shayxontohur"), KeyboardButton(text="Yunusobod")],
        [KeyboardButton(text="Yakkasaroy"), KeyboardButton(text="Yashnobod")],
        ],
        resize_keyboard=True
    )
    
    
def two_btn(i18n: I18nContext) -> ReplyKeyboardMarkup:
    
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=i18n("quest")), KeyboardButton(text=i18n("off_er"))]
        ],
        resize_keyboard=True
    )
    
def ai_chat_menu(i18n: I18nContext) -> ReplyKeyboardMarkup:
    
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=i18n("exit_chat"))]
        ],
        resize_keyboard=True
    )