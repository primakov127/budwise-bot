from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.kbd import Start
from aiogram_dialog.widgets.text import Const, Format

from dialogs.common import MAIN_MENU_BUTTON

from . import states

personal_menu_dialog = Dialog(
    Window(
        Format(
            "👤 Personal Menu\n\n"
            "Manage your personal finances efficiently."
        ),
        Start(
            text=Const("💸 Add Expense"),
            id="transaction",
            state=states.AddTransaction.MAIN,
        ),
        Start(
            text=Const("💰 Add Income"),
            id="income",
            state=states.AddIncome.MAIN,
        ),
        Start(
            text=Const("📈 Analytics"),
            id="analytics",
            state=states.Analytics.MAIN,
        ),
        MAIN_MENU_BUTTON,
        state=states.PersonalMenu.MAIN,
    )
)
