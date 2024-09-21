import asyncio
import io
from datetime import datetime

import plotly.graph_objects as go
from aiogram.types import BufferedInputFile, CallbackQuery, Message
from aiogram_dialog import Dialog, DialogManager, ShowMode, Window
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog.widgets.text import Const

from dialogs import states
from dialogs.common import MAIN_MENU_BUTTON
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
    fig.write_image(img_bytes, format="png", width=1024, height=1024, scale=2)
    img_bytes.seek(0)
    
    # Send the image to the user and await the result
    photo_message = await callback.bot.send_photo(
        user_id,
        BufferedInputFile(img_bytes.getvalue(), filename="current_month_expenses.png"),
        caption=datetime.now().strftime("%d %B %Y %H:%M")
    )
    
    remove_message_delayed(photo_message, 10)
    
    # Now that the image has been sent, switch the state
    await manager.start(states.Main.MAIN, show_mode=ShowMode.DELETE_AND_SEND)

async def current_year_handler(c, button, manager):
    # TODO: Implement current year analytics
    await c.answer("Current Year analytics not implemented yet")
    
def remove_message_delayed(message: Message, delay_seconds: int):
    async def remove_message():
        await asyncio.sleep(delay_seconds)
        await message.delete()
    asyncio.create_task(remove_message())
    

def create_pie_chart(expenses_by_category):
    labels = [expense['category'] for expense in expenses_by_category]
    values = [expense['amount'] for expense in expenses_by_category]
    
    fig = go.Figure(data=[go.Pie(labels=labels, values=values)])
    fig.update_layout(title_text=f"Expenses by Category - {datetime.now().strftime('%B %Y')}")
    fig.update_traces(textposition='inside', textinfo='percent+value',
                      texttemplate='%{value} zl<br>%{percent}')
    
    return fig

analytics_dialog = Dialog(
    Window(
        Const("Analytics Menu"),
        Button(Const("Current Month"), id="current_month", on_click=current_month_handler),
        Button(Const("Current Year"), id="current_year", on_click=current_year_handler),
        MAIN_MENU_BUTTON,
        state=states.Analytics.MAIN
    )
)
