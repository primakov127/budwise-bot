import datetime
import operator
from datetime import date
from typing import Any

from aiogram import F
from aiogram.types import CallbackQuery, Message
from aiogram_dialog import Data, Dialog, DialogManager, ShowMode, StartMode, Window
from aiogram_dialog.widgets.input import TextInput
from aiogram_dialog.widgets.kbd import (
    Button,
    Calendar,
    ManagedMultiselect,
    Row,
    SwitchTo,
)
from aiogram_dialog.widgets.text import Const, Format
from bson import ObjectId

from models import Category, Expense, Tag
from widgets import Numpad, VerticalMultiselect, VerticalSelect

from . import states
from .common import CANCEL_MENU_BUTTON

TRANSACTION_CURRENCY = "zl"
ID_TRANSACTION = "transaction"
FIELD_AMOUNT = "amount"
FIELD_DATE = "date"
FIELD_SELECTED_CATEGORY = "selected_category"
FIELD_SELECTED_TAG_IDS = "selected_tag_ids"
FIELD_SELECTED_TAGS = "selected_tags"
FIELD_TAGS="tags"
FIELD_TAGS_BY_ID = "tags_by_id"
FIELD_DESCRIPTION = "description"
FIELD_CATEGORIES = "categories"
FIELD_CATEGORIES_BY_ID = "categories_by_id"
CATEGORIES = {
    "food": "Food",
    "transport": "Transport",
    "entertainment": "Entertainment",
    "health": "Health",
    "education": "Education",
    "gifts": "Gifts",
    "other": "Other"
}
tags = [
    ("Creete 2024", "0"),
    ("Berlin Conf 2024", "1"),
    ("Taxi", "2"),
]

async def on_start(callback: CallbackQuery, dialog_manager: DialogManager):
    dialog_manager.current_context().widget_data[FIELD_DATE] = datetime.date.today()
    categories = await Category.find_all().to_list()
    tags = await Tag.find_all().to_list()
    
    dialog_manager.current_context().widget_data[FIELD_CATEGORIES_BY_ID] = {category.id: category.name for category in categories}
    dialog_manager.current_context().widget_data[FIELD_CATEGORIES] = [(category.name, category.id) for category in categories]
    dialog_manager.current_context().widget_data[FIELD_TAGS_BY_ID] = {tag.id: tag.name for tag in tags}
    dialog_manager.current_context().widget_data[FIELD_TAGS] = [(tag.name, tag.id) for tag in tags]

async def getter(dialog_manager: DialogManager, **kwargs):
    amount: Data = dialog_manager.current_context().widget_data.get(FIELD_AMOUNT, "0")
    selected_category = dialog_manager.current_context().widget_data.get(FIELD_SELECTED_CATEGORY)
    selected_tag_ids = dialog_manager.current_context().widget_data.get(FIELD_SELECTED_TAG_IDS, None)
    selected_tags = dialog_manager.current_context().widget_data.get(FIELD_SELECTED_TAGS, "")
    description = dialog_manager.current_context().widget_data.get(FIELD_DESCRIPTION, "")
    date = dialog_manager.current_context().widget_data.get(FIELD_DATE, datetime.date.today())
    categories = dialog_manager.current_context().widget_data.get(FIELD_CATEGORIES, [])
    tags = dialog_manager.current_context().widget_data.get(FIELD_TAGS, [])
    
    return {
        FIELD_AMOUNT: amount,
        FIELD_DATE: date,
        FIELD_SELECTED_CATEGORY: selected_category,
        FIELD_SELECTED_TAGS: selected_tags,
        FIELD_SELECTED_TAG_IDS: selected_tag_ids,
        FIELD_DESCRIPTION: description,
        FIELD_CATEGORIES: categories,
        FIELD_TAGS: tags
    }
    
async def on_amount_changed(callback: CallbackQuery, widget: Any, manager: DialogManager, amount: str):
    manager.current_context().widget_data[FIELD_AMOUNT] = "0" if amount == "" else amount
    
async def on_category_selected(callback: CallbackQuery, widget: Any, manager: DialogManager, category_id: str):
    categories_by_id = manager.current_context().widget_data[FIELD_CATEGORIES_BY_ID]
    id = ObjectId(category_id)
    manager.current_context().widget_data[FIELD_SELECTED_CATEGORY] = (id, categories_by_id.get(id))
    await manager.switch_to(states.AddTransaction.CONFIRM)
    
async def on_tags_changed(callback: CallbackQuery, widget: ManagedMultiselect[str], manager: DialogManager, data):
    selected_tag_ids = widget.get_checked()
    tags_by_id = manager.current_context().widget_data[FIELD_TAGS_BY_ID]
    tag_names = ", ".join([tags_by_id.get(ObjectId(tag_id)) for tag_id in selected_tag_ids])
    
    manager.current_context().widget_data[FIELD_SELECTED_TAGS] = tag_names
    manager.current_context().widget_data[FIELD_SELECTED_TAG_IDS] = [ObjectId(tag_id) for tag_id in selected_tag_ids]
    
async def on_description_changed(message: Message, textInput, manager: DialogManager, description: str):
    manager.current_context().widget_data[FIELD_DESCRIPTION] = description
    await message.delete()
    await manager.switch_to(states.AddTransaction.CONFIRM, ShowMode.DELETE_AND_SEND)

async def on_transaction_added(callback: CallbackQuery, widget: Any, manager: DialogManager):
    transaction_amount = float(manager.current_context().widget_data[FIELD_AMOUNT])
    transaction_category = manager.current_context().widget_data[FIELD_SELECTED_CATEGORY][0]
    transaction_date = manager.current_context().widget_data[FIELD_DATE]
    transaction_description = manager.current_context().widget_data.get(FIELD_DESCRIPTION)
    transaction_tag_ids = manager.current_context().widget_data.get(FIELD_SELECTED_TAG_IDS, None)
    
    transaction = Expense(
        amount=transaction_amount,
        category=transaction_category,
        date=transaction_date,
        description=transaction_description,
        tags=transaction_tag_ids if transaction_tag_ids else None,
        user_id=str(manager.event.from_user.id)
    )
    
    await transaction.insert()
    
    await manager.start(states.Main.MAIN, mode=StartMode.RESET_STACK, show_mode=ShowMode.DELETE_AND_SEND)
    
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
        Const("Specify transaction category"),
        VerticalSelect(
            Format("{item[0]}"),
            id="transaction_category",
            item_id_getter=operator.itemgetter(1),
            items=FIELD_CATEGORIES,
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
        Format(f"Tags: {{{FIELD_SELECTED_TAGS}}}"),
        Format(f"Description: {{{FIELD_DESCRIPTION}}}"),
        Row(
            Button(Const("Add"), id="add", on_click=on_transaction_added),
            CANCEL_MENU_BUTTON
        ),
        SwitchTo(
            Const("Description"),
            id="description",
            state=states.AddTransaction.SPECIFY_DESCRIPTION
        ),
        SwitchTo(
            Const("Tags"),
            id="tags",
            state=states.AddTransaction.SPECIFY_TAGS
        ),
        SwitchTo(
            Const("Change date"),
            id="date",
            state=states.AddTransaction.CHANGE_DATE
        ),
        state=states.AddTransaction.CONFIRM
    ),
    Window(
        Const("Specify description"),
        TextInput(
            id="transaction_description",
            on_success=on_description_changed,
        ),
        Row(
            SwitchTo(
                Const("Back"),
                id="back",
                state=states.AddTransaction.CONFIRM
            ),
            CANCEL_MENU_BUTTON,
        ),
        state=states.AddTransaction.SPECIFY_DESCRIPTION,
        getter=getter,
    ),
    Window(
        Const("Select tags"),
        VerticalMultiselect(
            Format("✓ {item[0]}"),
            Format("{item[0]}"),
            id="transaction_tags",
            item_id_getter=operator.itemgetter(1),
            items=FIELD_TAGS,
            on_state_changed=on_tags_changed,
        ),
        Row(
            SwitchTo(
                Const("Change"),
                id="change",
                state=states.AddTransaction.CONFIRM
            ),
            SwitchTo(
                Const("Back"),
                id="back",
                state=states.AddTransaction.CONFIRM
            ),
        ),
        state=states.AddTransaction.SPECIFY_TAGS,
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
                state=states.AddTransaction.CONFIRM
            ),
            SwitchTo(
                Const("Back"),
                id="back",
                state=states.AddTransaction.CONFIRM
            ),
        ),
        state=states.AddTransaction.CHANGE_DATE
    ),
    on_start=on_start,
    getter=getter,
)