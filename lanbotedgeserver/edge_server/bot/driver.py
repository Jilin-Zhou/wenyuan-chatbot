from bot.model import BotNav
from bot import smart

from config import conf
from config.conf import BotEnum


class NavAgilex(BotNav):
    pass


nav = BotNav()

if conf.BOT_TYPE == BotEnum.AGILEX:
    nav = NavAgilex()
elif conf.BOT_TYPE == BotEnum.SMART:
    nav = smart.nav


def enable_ws_client():
    if conf.BOT_TYPE == BotEnum.AGILEX:
        pass
    elif conf.BOT_TYPE == BotEnum.SMART:
        smart.enable_ws()


def disable_ws_client():
    if conf.BOT_TYPE == BotEnum.AGILEX:
        pass
    elif conf.BOT_TYPE == BotEnum.SMART:
        smart.disable_ws()
