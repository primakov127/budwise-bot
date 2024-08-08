from aiogram_dialog import Dialog, LaunchMode, Window
from aiogram_dialog.widgets.kbd import Start
from aiogram_dialog.widgets.text import Const

from . import states

main_dialog = Dialog(
    Window(
        Const("This is budwise application for running your finances."),
        Const("Use buttons below to see some options."),
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
        state=states.Main.MAIN,
    ),
    launch_mode=LaunchMode.ROOT,
)