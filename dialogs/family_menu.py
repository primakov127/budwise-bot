from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.kbd import Start
from aiogram_dialog.widgets.text import Const, Format

from dialogs.common import MAIN_MENU_BUTTON

from . import states

family_menu_dialog = Dialog(
    Window(
        Format(
            "👨‍👩‍👧‍👦 Family Menu\n\n"
            "Coordinate your family’s finances with ease."
        ),
        Start(
            text=Const("💸 Add Expense"),
            id="family_transaction",
            state=states.AddFamilyTransaction.MAIN,
        ),
        Start(
            text=Const("💰 Add Income"),
            id="family_income",
            state=states.AddFamilyIncome.MAIN,
        ),
        Start(
            text=Const("📈 Analytics"),
            id="family_analytics",
            state=states.FamilyAnalytics.MAIN,
        ),
        MAIN_MENU_BUTTON,
        state=states.FamilyMenu.MAIN,
    )
)
