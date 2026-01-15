import pathlib

from aiogram_i18n import I18nMiddleware
from aiogram_i18n.cores.fluent_compile_core import FluentCompileCore

BASE_DIR = pathlib.Path(__file__).parent.parent

core = FluentCompileCore(
    path = BASE_DIR / 'locales' / '{locale}'
)

i18n_middleware = I18nMiddleware(core=core)