from aiogram_dialog import Dialog, LaunchMode, Window
from aiogram_dialog.widgets.kbd import Start
from aiogram_dialog.widgets.text import Const

from . import states

main_dialog = Dialog(
    Window(
        Start(
            text=Const("Add Transaction"),
            id="transaction",
            state=states.AddTransaction.MAIN,
        ),
        Start(
            text=Const("Settings"),
            id="settings",
            state=states.SettingsMenu.MAIN,
        ),
        Start(
            text=Const("Analytics"),
            id="analytics",
            state=states.Analytics.MAIN,
        ),
        state=states.Main.MAIN,
    ),
    launch_mode=LaunchMode.ROOT,
)
