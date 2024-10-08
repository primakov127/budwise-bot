import asyncio
import logging
import os.path

import aiohttp
from aiogram import Bot, Dispatcher, F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import ExceptionTypeFilter
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import ErrorEvent, Message, ReplyKeyboardRemove
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiogram_dialog import DialogManager, ShowMode, StartMode, setup_dialogs
from aiogram_dialog.api.exceptions import UnknownIntent
from aiohttp import web

from db import init_db
from dialogs import (
    add_income_dialog,
    add_transaction_dialog,
    analytics_dialog,
    edit_categories,
    edit_tags,
    main_dialog,
    states,
)

# Path to webhook route, on which Telegram will send requests
WEBHOOK_PATH = "/webhook"


async def start(message: Message, dialog_manager: DialogManager):
    # it is important to reset stack because user wants to restart everything
    await dialog_manager.start(states.Main.MAIN, mode=StartMode.RESET_STACK)


async def on_unknown_intent(event: ErrorEvent, dialog_manager: DialogManager):
    # Example of handling UnknownIntent Error and starting new dialog.
    logging.error("Restarting dialog: %s", event.exception)
    if event.update.callback_query:
        await event.update.callback_query.answer(
            "Bot process was restarted due to maintenance.\n"
            "Redirecting to main menu.",
        )
        if event.update.callback_query.message:
            try:
                await event.update.callback_query.message.delete()
            except TelegramBadRequest:
                pass  # whatever
    elif event.update.message:
        await event.update.message.answer(
            "Bot process was restarted due to maintenance.\n"
            "Redirecting to main menu.",
            reply_markup=ReplyKeyboardRemove(),
        )
    await dialog_manager.start(
        states.Main.MAIN,
        mode=StartMode.RESET_STACK,
        show_mode=ShowMode.SEND,
    )


dialog_router = Router()
dialog_router.include_routers(
    main_dialog,
    add_transaction_dialog,
    add_income_dialog,
    analytics_dialog,
    edit_categories,
    edit_tags
)


def setup_dp():
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    dp.startup.register(on_startup)
    dp.message.register(start, F.text == "/start")
    dp.errors.register(
        on_unknown_intent,
        ExceptionTypeFilter(UnknownIntent),
    )
    dp.include_router(dialog_router)
    setup_dialogs(dp)
    return dp

async def on_startup(bot: Bot) -> None:
    BASE_WEBHOOK_URL = os.getenv("BASE_WEBHOOK_URL")
    
    await bot.set_webhook(f"{BASE_WEBHOOK_URL}{WEBHOOK_PATH}")

async def health_check(request):
    return web.Response(text="OK")

async def main():
    # real main
    logging.basicConfig(level=logging.INFO)
    TOKEN = os.getenv("BOT_TOKEN")
    
    bot = Bot(TOKEN)
    await init_db()
    dp = setup_dp()
    app = web.Application()
    webhook_requests_handler = SimpleRequestHandler(
        dispatcher=dp,
        bot=bot
    )
    
    webhook_requests_handler.register(app, path=WEBHOOK_PATH)
    setup_application(app, dp, bot=bot)
    
    app.router.add_get('/health', health_check)
    
    runner = web.AppRunner(app)
    await runner.setup()
    
    WEB_HOST = os.getenv("WEB_HOST")
    WEB_PORT = int(os.getenv("WEB_PORT"))
    
    site = web.TCPSite(runner, WEB_HOST, WEB_PORT)
    
    await site.start()
    
    try:
        # Keep the application running
        while True:
            await asyncio.sleep(3600)
    except (KeyboardInterrupt, SystemExit):
        logging.info("Shutting down...")
    finally:
        await bot.session.close()
        await runner.cleanup()


if __name__ == '__main__':
    asyncio.run(main())
