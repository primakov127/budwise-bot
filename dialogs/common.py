from aiogram_dialog.widgets.kbd import Start
from aiogram_dialog.widgets.text import Const
from . import states

MAIN_MENU_BUTTON = Start(
    text=Const("☰ Main menu"),
    id="__main__",
    state=states.Main.MAIN,
)

CANCEL_MENU_BUTTON = Start(
    text=Const("Cancel"),
    id="__cancel__",
    state=states.Main.MAIN,
)