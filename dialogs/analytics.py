import io
from datetime import datetime

import plotly.graph_objects as go
from aiogram.types import BufferedInputFile, CallbackQuery
from aiogram_dialog import Dialog, DialogManager, Window
from aiogram_dialog.widgets.kbd import Button, SwitchTo
from aiogram_dialog.widgets.text import Const

from dialogs.states import AnalyticsStates
from services.expense_service import ExpenseService

from . import states


async def current_month_handler(callback: CallbackQuery, button: Button, manager: DialogManager):
    user_id = str(callback.from_user.id)
    expense_service = ExpenseService()
    expenses_by_category = await expense_service.get_current_month_expenses(user_id)
    
    if not expenses_by_category:
        await callback.answer("No expenses found for the current month.")
        return

    fig = create_pie_chart(expenses_by_category)
    
    # Save the plot as a PNG image
    img_bytes = io.BytesIO()
    fig.write_image(img_bytes, format="png")
    img_bytes.seek(0)
    
    # Send the image to the user
    await callback.bot.send_photo(
        callback.from_user.id,
        BufferedInputFile(img_bytes.getvalue(), filename="current_month_expenses.png"),
        caption="Current Month Expenses by Category"
    )

async def current_year_handler(c, button, manager):
    # TODO: Implement current year analytics
    await c.answer("Current Year analytics not implemented yet")

def create_pie_chart(expenses_by_category):
    labels = [expense['category'] for expense in expenses_by_category]
    values = [expense['amount'] for expense in expenses_by_category]
    
    fig = go.Figure(data=[go.Pie(labels=labels, values=values)])
    fig.update_layout(title_text=f"Expenses by Category - {datetime.now().strftime('%B %Y')}")
    return fig

analytics_dialog = Dialog(
    Window(
        Const("Analytics Menu"),
        Button(Const("Current Month"), id="current_month", on_click=current_month_handler),
        Button(Const("Current Year"), id="current_year", on_click=current_year_handler),
        SwitchTo(Const("Back"), id="back", state=states.Main.MAIN),
        state=AnalyticsStates.MAIN
    )
)
