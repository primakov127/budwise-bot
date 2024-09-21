from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog.widgets.text import Const
from aiogram.types import BufferedInputFile

from dialogs.states import AnalyticsStates
from services.expense_service import ExpenseService
from datetime import datetime
import plotly.graph_objects as go
import io

async def current_month_handler(c, button, manager):
    user_id = str(c.from_user.id)
    expense_service = ExpenseService()
    expenses = await expense_service.get_current_month_expenses(user_id)
    
    if not expenses:
        await c.answer("No expenses found for the current month.")
        return

    fig = create_pie_chart(expenses)
    
    # Save the plot as a PNG image
    img_bytes = io.BytesIO()
    fig.write_image(img_bytes, format="png")
    img_bytes.seek(0)
    
    # Send the image to the user
    await c.bot.send_photo(
        c.from_user.id,
        BufferedInputFile(img_bytes.getvalue(), filename="current_month_expenses.png"),
        caption="Current Month Expenses by Category"
    )

async def current_year_handler(c, button, manager):
    # TODO: Implement current year analytics
    await c.answer("Current Year analytics not implemented yet")

def create_pie_chart(expenses):
    categories = {}
    for expense in expenses:
        category = expense.category
        amount = expense.amount
        if category in categories:
            categories[category] += amount
        else:
            categories[category] = amount
    
    labels = list(categories.keys())
    values = list(categories.values())
    
    fig = go.Figure(data=[go.Pie(labels=labels, values=values)])
    fig.update_layout(title_text=f"Expenses by Category - {datetime.now().strftime('%B %Y')}")
    return fig

analytics_dialog = Dialog(
    Window(
        Const("Analytics Menu"),
        Button(Const("Current Month"), id="current_month", on_click=current_month_handler),
        Button(Const("Current Year"), id="current_year", on_click=current_year_handler),
        Button(Const("Back"), id="back", on_click=lambda c, b, m: m.dialog().back()),
        state=AnalyticsStates.menu
    )
)
