import datetime
import operator
from datetime import date
from typing import Any

from aiogram import F
from aiogram.types import CallbackQuery, ReplyKeyboardRemove
from aiogram_dialog import Data, Dialog, DialogManager, Window
from aiogram_dialog.widgets.kbd import Back, Button, Calendar, Radio, Row, SwitchTo
from aiogram_dialog.widgets.text import Const, Format

from models.expense import Expense
from widgets.numpad import Numpad
from widgets.vertical_select import VerticalSelect

from . import states
from .common import CANCEL_MENU_BUTTON

TRANSACTION_CURRENCY = "zl"
ID_TRANSACTION = "transaction"
FIELD_AMOUNT = "amount"
FIELD_DATE = "date"
FIELD_SELECTED_CATEGORY = "selected_category"
FIELD_CATEGORIES = "categories"
# CATEGORIES = [
#     ("Food", "food"),
#     ("Transport", "transport"),
#     ("Entertainment", "entertainment"),
#     ("Health", "health"),
#     ("Education", "education"),
#     ("Gifts", "gifts"),
#     ("Other", "other"),
# ]
CATEGORIES = {
    "food": "Food",
    "transport": "Transport",
    "entertainment": "Entertainment",
    "health": "Health",
    "education": "Education",
    "gifts": "Gifts",
    "other": "Other"
}

async def on_start(callback: CallbackQuery, dialog_manager: DialogManager):
    dialog_manager.current_context().widget_data[FIELD_DATE] = datetime.date.today()

async def getter(dialog_manager: DialogManager, **kwargs):
    amount: Data = dialog_manager.current_context().widget_data.get(FIELD_AMOUNT, "0")
    selected_category = dialog_manager.current_context().widget_data.get(FIELD_SELECTED_CATEGORY)
    date = dialog_manager.current_context().widget_data.get(FIELD_DATE, datetime.date.today())
    return {
        FIELD_AMOUNT: amount,
        FIELD_DATE: date,
        FIELD_SELECTED_CATEGORY: selected_category,
        FIELD_CATEGORIES: [(category, id) for id, category in CATEGORIES.items()],
    }
    
async def on_amount_changed(callback: CallbackQuery, widget: Any, manager: DialogManager, amount: str):
    manager.current_context().widget_data[FIELD_AMOUNT] = "0" if amount == "" else amount
    
async def on_category_selected(callback: CallbackQuery, widget: Any, manager: DialogManager, item_id: str):
    manager.current_context().widget_data[FIELD_SELECTED_CATEGORY] = (item_id, CATEGORIES[item_id])
    await manager.switch_to(states.AddTransaction.CONFIRM)

async def on_transaction_added(callback: CallbackQuery, widget: Any, manager: DialogManager):
    transaction_amount = float(manager.current_context().widget_data[FIELD_AMOUNT])
    transaction_category = manager.current_context().widget_data[FIELD_SELECTED_CATEGORY][0]
    transaction_date = manager.current_context().widget_data[FIELD_DATE]
    
    transaction = Expense(
        amount=transaction_amount,
        category=transaction_category,
        date=transaction_date,
        user_id=str(manager.event.from_user.id)
    )
    
    await transaction.insert()
    
    await manager.start(states.Main.MAIN)
    
async def on_date_changed(callback: CallbackQuery, widget, manager: DialogManager, selected_date: date):
    print(manager.current_context().widget_data[FIELD_DATE])
    manager.current_context().widget_data[FIELD_DATE] = selected_date
    print(manager.current_context().widget_data[FIELD_DATE])
    
    
add_transaction_dialog = Dialog(
    Window(
        Const("Specify transaction amount:"),
        Format(f"{{{FIELD_AMOUNT}}} {TRANSACTION_CURRENCY}"),
        Numpad(
            id=ID_TRANSACTION,
            on_value_changed=on_amount_changed,
        ),
        Row(
            SwitchTo(Const("Category"), id="category", state=states.AddTransaction.SPECIFY_CATEGORY),
            CANCEL_MENU_BUTTON
        ),
        state=states.AddTransaction.MAIN
    ),
    Window(
        Const("Specify transaction category:"),
        VerticalSelect(
            Format("{item[0]}"),
            id="transaction_category",
            item_id_getter=operator.itemgetter(1),
            items="categories",
            on_click=on_category_selected,
        ),
        state=states.AddTransaction.SPECIFY_CATEGORY,
        getter=getter,
    ),
    Window(
        Const("Add the following transaction?"),
        Format(f"Amount: {{{FIELD_AMOUNT}}} {TRANSACTION_CURRENCY}"),
        Format(f"Category: {{{FIELD_SELECTED_CATEGORY}[1]}}"),
        Format(f"Date: {{{FIELD_DATE}}}"),
        Row(
            Button(Const("Add"), id="add", on_click=on_transaction_added),
            CANCEL_MENU_BUTTON
        ),
        SwitchTo(
            Const("Change date"),
            id="date",
            state=states.AddTransaction.CHANGE_DATE
        ),
        state=states.AddTransaction.CONFIRM
    ),
    Window(
        Format(f"Date: {{{FIELD_DATE}}}"),
        Calendar(
            id="change_date",
            on_click=on_date_changed
        ),
        Row(
            Back(Const("Change")),
            Back(Const("Back")),
        ),
        state=states.AddTransaction.CHANGE_DATE
    ),
    on_start=on_start,
    getter=getter,
)