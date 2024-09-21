from aiogram_dialog import Dialog, LaunchMode, Window
from aiogram_dialog.widgets.kbd import Start
from aiogram_dialog.widgets.text import Const, Format

from . import states

main_dialog = Dialog(
    Window(
        Format(
            "👋 Welcome to BudWise Bot!\n\n"
            "Your personal finance assistant is here to help you manage your money smarter.\n\n"
            "What would you like to do today?"
        ),
        Start(
            text=Const("💸 Add Transaction"),
            id="transaction",
            state=states.AddTransaction.MAIN,
        ),
        Start(
            text=Const("⚙️ Settings"),
            id="settings",
            state=states.SettingsMenu.MAIN,
        ),
        Start(
            text=Const("📈 Analytics"),
            id="analytics",
            state=states.Analytics.MAIN,
        ),
        state=states.Main.MAIN,
    ),
    launch_mode=LaunchMode.ROOT,
)
