from aiogram_dialog import Dialog, LaunchMode, Window
from aiogram_dialog.widgets.kbd import Start
from aiogram_dialog.widgets.text import Const, Format

from . import states

main_dialog = Dialog(
    Window(
        Format(
            "👋 Welcome to BudWise Bot!\n\n"
            "Your finance assistant is here to help you manage your money smarter.\n\n"
            "What would you like to do today?"
        ),
        Start(
            text=Const("👤 Personal menu"),
            id="personal_menu",
            state=states.PersonalMenu.MAIN,
        ),
        Start(
            text=Const("👨‍👩‍👧‍👦 Family menu"),
            id="family_menu",
            state=states.FamilyMenu.MAIN,
        ),
        state=states.Main.MAIN,
    ),
    launch_mode=LaunchMode.ROOT,
)
