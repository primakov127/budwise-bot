import datetime
from datetime import date
from typing import Any

from aiogram.types import CallbackQuery, Message
from aiogram_dialog import Data, Dialog, DialogManager, ShowMode, StartMode, Window
from aiogram_dialog.widgets.input import TextInput
from aiogram_dialog.widgets.kbd import Button, Calendar, Row, SwitchTo
from aiogram_dialog.widgets.text import Const, Format

from models import FamilyIncome
from widgets import Numpad

from . import states
from .common import CANCEL_MENU_BUTTON

INCOME_CURRENCY = "zl"
ID_INCOME = "income"
FIELD_AMOUNT = "amount"
FIELD_DATE = "date"
FIELD_DESCRIPTION = "description"

async def on_start(callback: CallbackQuery, dialog_manager: DialogManager):
    dialog_manager.current_context().widget_data[FIELD_DATE] = datetime.date.today()

async def getter(dialog_manager: DialogManager, **kwargs):
    amount: Data = dialog_manager.current_context().widget_data.get(FIELD_AMOUNT, "0")
    description = dialog_manager.current_context().widget_data.get(FIELD_DESCRIPTION, "")
    date = dialog_manager.current_context().widget_data.get(FIELD_DATE, datetime.date.today())
    
    return {
        FIELD_AMOUNT: amount,
        FIELD_DATE: date,
        FIELD_DESCRIPTION: description,
    }
    
async def on_amount_changed(callback: CallbackQuery, widget: Any, manager: DialogManager, amount: str):
    manager.current_context().widget_data[FIELD_AMOUNT] = "0" if amount == "" else amount
    
async def on_description_changed(message: Message, textInput, manager: DialogManager, description: str):
    manager.current_context().widget_data[FIELD_DESCRIPTION] = description
    await message.delete()
    await manager.switch_to(states.AddFamilyIncome.CONFIRM, ShowMode.DELETE_AND_SEND)

async def on_income_added(callback: CallbackQuery, widget: Any, manager: DialogManager):
    income_amount = float(manager.current_context().widget_data[FIELD_AMOUNT])
    income_date = manager.current_context().widget_data[FIELD_DATE]
    income_description = manager.current_context().widget_data.get(FIELD_DESCRIPTION)
    
    income = FamilyIncome(
        amount=income_amount,
        date=income_date,
        description=income_description,
        user_id=str(manager.event.from_user.id)
    )
    
    await income.insert()
    
    await manager.start(states.Main.MAIN, mode=StartMode.RESET_STACK, show_mode=ShowMode.DELETE_AND_SEND)
    
async def on_date_changed(callback: CallbackQuery, widget, manager: DialogManager, selected_date: date):
    manager.current_context().widget_data[FIELD_DATE] = selected_date
    
add_family_income_dialog = Dialog(
    Window(
        Const("Specify income amount:"),
        Format(f"{{{FIELD_AMOUNT}}} {INCOME_CURRENCY}"),
        Numpad(
            id=ID_INCOME,
            on_value_changed=on_amount_changed,
        ),
        Row(
            SwitchTo(Const("Continue"), id="continue", state=states.AddFamilyIncome.CONFIRM),
            CANCEL_MENU_BUTTON
        ),
        state=states.AddFamilyIncome.MAIN
    ),
    Window(
        Const("Add the following income?"),
        Format(f"Amount: {{{FIELD_AMOUNT}}} {INCOME_CURRENCY}"),
        Format(f"Date: {{{FIELD_DATE}}}"),
        Format(f"Description: {{{FIELD_DESCRIPTION}}}"),
        Row(
            Button(Const("Add"), id="add", on_click=on_income_added),
            CANCEL_MENU_BUTTON
        ),
        SwitchTo(
            Const("Description"),
            id="description",
            state=states.AddFamilyIncome.SPECIFY_DESCRIPTION
        ),
        SwitchTo(
            Const("Change date"),
            id="date",
            state=states.AddFamilyIncome.CHANGE_DATE
        ),
        state=states.AddFamilyIncome.CONFIRM
    ),
    Window(
        Const("Specify description"),
        TextInput(
            id="income_description",
            on_success=on_description_changed,
        ),
        Row(
            SwitchTo(
                Const("Back"),
                id="back",
                state=states.AddFamilyIncome.CONFIRM
            ),
            CANCEL_MENU_BUTTON,
        ),
        state=states.AddFamilyIncome.SPECIFY_DESCRIPTION,
        getter=getter,
    ),
    Window(
        Format(f"Date: {{{FIELD_DATE}}}"),
        Calendar(
            id="change_date",
            on_click=on_date_changed
        ),
        Row(
            SwitchTo(
                Const("Change"),
                id="change",
                state=states.AddFamilyIncome.CONFIRM
            ),
            SwitchTo(
                Const("Back"),
                id="back",
                state=states.AddFamilyIncome.CONFIRM
            ),
        ),
        state=states.AddFamilyIncome.CHANGE_DATE
    ),
    on_start=on_start,
    getter=getter,
)