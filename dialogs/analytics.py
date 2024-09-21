from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog.widgets.text import Const

from dialogs.states import AnalyticsStates

async def current_month_handler(c, button, manager):
    # TODO: Implement current month analytics
    await c.answer("Current Month analytics not implemented yet")

async def current_year_handler(c, button, manager):
    # TODO: Implement current year analytics
    await c.answer("Current Year analytics not implemented yet")

analytics_dialog = Dialog(
    Window(
        Const("Analytics Menu"),
        Button(Const("Current Month"), id="current_month", on_click=current_month_handler),
        Button(Const("Current Year"), id="current_year", on_click=current_year_handler),
        Button(Const("Back"), id="back", on_click=lambda c, b, m: m.dialog().back()),
        state=AnalyticsStates.menu
    )
)
