from aiogram_dialog import Dialog, DialogManager, Window
from aiogram_dialog.widgets.kbd import Button, ScrollingGroup
from aiogram_dialog.widgets.text import Const

from dialogs import states
from models.expense import Expense

FIELD_CATEGORIES = "categories"

async def on_start(callback, dialog_manager: DialogManager):
    user_id = dialog_manager.event.from_user.id
    dialog_manager.current_context().widget_data[FIELD_CATEGORIES] = Expense.find_all({"user_id": user_id})
    
async def get_category_buttons(dialog_manager: DialogManager):
    categories = dialog_manager.current_context().widget_data[FIELD_CATEGORIES]
    return [Button(Const(category.amount), id=category.id) for category in categories]

edit_categories = Dialog(
    Window(
        ScrollingGroup(
            get_category_buttons,
            id="categories",
            width=1,
            height=5,
        ),
        state=states.EditCategories.MAIN
    ),
    on_start=on_start
)
