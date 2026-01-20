from aiogram import Router, types

from aiogram_i18n.context import I18nContext
from buttons.inline import admin


dp_us = Router()

@dp_us.message(lambda message, i18n: message.text == i18n("about_us"))
async def about_us(msg: types.Message, i18n: I18nContext):
    await msg.answer(i18n("info_admin"), reply_markup=admin(i18n))
    


