import asyncio
import io
from datetime import datetime

import plotly.graph_objects as go
from aiogram.types import BufferedInputFile, CallbackQuery, Message
from aiogram_dialog import Dialog, DialogManager, ShowMode, Window
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog.widgets.text import Const, Format

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
    
async def last_n_transactions_handler(callback: CallbackQuery, button: Button, manager: DialogManager):
    count = 20
    user_id = str(callback.from_user.id)
    expense_service = ExpenseService()
    last_n_transactions = await expense_service.get_last_n_expenses(user_id, count)
    last_n_transactions.reverse()
    
    if not last_n_transactions:
        await callback.answer("No transactions found.")
        return

    fig = create_expense_table(last_n_transactions)
    
    # Save the plot as a PNG image
    img_bytes = io.BytesIO()
    fig.write_image(img_bytes, format="png", width=512, height=1024, scale=2)
    img_bytes.seek(0)
    
    # Send the image to the user and await the result
    photo_message = await callback.bot.send_photo(
        user_id,
        BufferedInputFile(img_bytes.getvalue(), filename=f"last_{count}_transactions.png"),
        caption=f"Last {count} Transactions - {datetime.now().strftime('%d %B %Y %H:%M')}"
    )
    
    remove_message_delayed(photo_message, 10)
    
    # Now that the image has been sent, switch the state
    await manager.start(states.Main.MAIN, show_mode=ShowMode.DELETE_AND_SEND)
    
def remove_message_delayed(message: Message, delay_seconds: int):
    async def remove_message():
        await asyncio.sleep(delay_seconds)
        await message.delete()
    asyncio.create_task(remove_message())
    

def create_pie_chart(expenses_by_category):
    labels = [expense['category'] for expense in expenses_by_category]
    values = [expense['amount'] for expense in expenses_by_category]
    total_expenses = sum(values)
    
    fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=0.3)])
    fig.update_layout(title_text=f"Expenses by Category - {datetime.now().strftime('%B %Y %H:%M')}",
                      annotations=[dict(text=f'{total_expenses} zl', x=0.5, y=0.5, font_size=20, showarrow=False)])
    fig.update_traces(textposition='inside', textinfo='percent+value',
                      texttemplate='%{value} zl<br>%{percent}')
    
    return fig

def create_expense_table(transactions: list[dict]):
    count = len(transactions)
    headers = ['Date', 'Category', 'Amount', 'Description']
    cell_values = [
        [transaction['date'].strftime('%Y-%m-%d') for transaction in transactions],
        [transaction['category'] for transaction in transactions],
        [f"{transaction['amount']:.2f} zl" for transaction in transactions],
        [transaction['description'] for transaction in transactions]
    ]

    fig = go.Figure(data=[go.Table(
        header=dict(values=headers,
                    fill_color='royalblue',
                    align='left',
                    font=dict(color='white', size=12)),
        cells=dict(values=cell_values,
                   fill_color='lavender',
                   align='left',
                   font=dict(color='darkslate gray', size=11))
    )])

    fig.update_layout(
        title=f"Last {count} Transactions - {datetime.now().strftime('%B %Y %H:%M')}",
        margin=dict(l=20, r=20, t=60, b=20)
    )

    return fig

analytics_dialog = Dialog(
    Window(
        Format(
            "📊 Welcome to your Analytics Dashboard!\n\n"
            "Get insights into your expenses and track your spending with ease.\n\n"
            "What would you like to view today?\n\n"
        ),
        Button(Const("📅 Current Month"), id="current_month", on_click=current_month_handler),
        # Button(Const("📆 Current Year"), id="current_year", on_click=current_year_handler),
        Button(Const("📋 Last 20 Transactions"), id="last_20_transactions", on_click=last_n_transactions_handler),
        MAIN_MENU_BUTTON,
        state=states.Analytics.MAIN
    )
)
