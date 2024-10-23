import asyncio
import io
from datetime import datetime

import plotly.graph_objects as go
from aiogram.types import BufferedInputFile, CallbackQuery, Message
from aiogram_dialog import Dialog, DialogManager, ShowMode, Window
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog.widgets.text import Const, Format
from dateutil.relativedelta import relativedelta

from dialogs import states
from dialogs.common import MAIN_MENU_BUTTON
from services.expense_service import ExpenseService
from services.income_service import IncomeService

from . import states


async def current_month_expense_handler(callback: CallbackQuery, button: Button, manager: DialogManager):
    user_id = str(callback.from_user.id)
    expenses_by_category = await ExpenseService.get_current_month_expenses(user_id)
    
    if not expenses_by_category:
        await callback.answer("No expenses found for the current month.")
        return

    fig = create_pie_chart(expenses_by_category)
    
    await send_chart(callback, fig, "current_month_expenses.png")
    await manager.start(states.Main.MAIN, show_mode=ShowMode.DELETE_AND_SEND)
    
async def last_month_expense_handler(callback: CallbackQuery, button: Button, manager: DialogManager):
    user_id = str(callback.from_user.id)
    last_month = (datetime.now() - relativedelta(months=1)).month
    expenses_by_category = await ExpenseService.get_month_expenses(user_id, last_month)
    
    if not expenses_by_category:
        await callback.answer("No expenses found for the current month.")
        return

    fig = create_pie_chart(expenses_by_category)
    
    await send_chart(callback, fig, "current_month_expenses.png")
    await manager.start(states.Main.MAIN, show_mode=ShowMode.DELETE_AND_SEND)

async def last_n_expenses_handler(callback: CallbackQuery, button: Button, manager: DialogManager):
    count = 15
    user_id = str(callback.from_user.id)
    last_n_expenses = await ExpenseService.get_last_n_expenses(user_id, count)
    last_n_expenses.reverse()
    
    if not last_n_expenses:
        await callback.answer("No expenses found.")
        return

    fig = create_expenses_table(last_n_expenses)
    
    await send_chart(callback, fig, f"last_{count}_expenses.png", width=512)
    await manager.start(states.Main.MAIN, show_mode=ShowMode.DELETE_AND_SEND)

async def last_n_incomes_handler(callback: CallbackQuery, button: Button, manager: DialogManager):
    count = 20
    user_id = str(callback.from_user.id)
    last_n_incomes = await IncomeService.get_last_n_incomes(user_id, count)
    last_n_incomes.reverse()
    
    if not last_n_incomes:
        await callback.answer("No income entries found.")
        return

    fig = create_incomes_table(last_n_incomes)
    
    await send_chart(callback, fig, f"last_{count}_incomes.png", width=512)
    await manager.start(states.Main.MAIN, show_mode=ShowMode.DELETE_AND_SEND)

async def send_chart(callback: CallbackQuery, fig, filename: str, width=1024, height=1024):
    img_bytes = io.BytesIO()
    fig.write_image(img_bytes, format="png", width=width, height=height, scale=2)
    img_bytes.seek(0)
    
    photo_message = await callback.bot.send_photo(
        callback.from_user.id,
        BufferedInputFile(img_bytes.getvalue(), filename=filename),
        caption=datetime.now().strftime("%d %B %Y %H:%M")
    )
    
    remove_message_delayed(photo_message, 10)

def remove_message_delayed(message: Message, delay_seconds: int):
    async def remove_message():
        await asyncio.sleep(delay_seconds)
        await message.delete()
    asyncio.create_task(remove_message())
    

def create_pie_chart(expenses_by_category):
    labels = [expense['category'] for expense in expenses_by_category]
    values = [expense['amount'] for expense in expenses_by_category]
    total_expenses = round(sum(values), 2)
    
    fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=0.3)])
    fig.update_layout(title_text=f"Expenses by Category - {datetime.now().strftime('%B %Y %H:%M')}",
                      annotations=[dict(text=f'{total_expenses} zl', x=0.5, y=0.5, font_size=20, showarrow=False)])
    fig.update_traces(textposition='inside', textinfo='percent+value',
                      texttemplate='%{value} zl<br>%{percent}')
    
    return fig

def create_expenses_table(transactions: list[dict]):
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
        title=f"Last {count} Expenses - {datetime.now().strftime('%B %Y %H:%M')}",
        margin=dict(l=20, r=20, t=60, b=20)
    )

    return fig

def create_incomes_table(transactions: list[dict]):
    count = len(transactions)
    headers = ['Date', 'Amount', 'Description']
    cell_values = [
        [transaction['date'].strftime('%Y-%m-%d') for transaction in transactions],
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
        title=f"Last {count} Incomes - {datetime.now().strftime('%B %Y %H:%M')}",
        margin=dict(l=20, r=20, t=60, b=20)
    )

    return fig

analytics_dialog = Dialog(
    Window(
        Format(
            "📊 Welcome to your Analytics Dashboard!\n\n"
            "Get insights into your expenses and income, and track your finances with ease.\n\n"
            "What would you like to view today?\n\n"
        ),
        Button(Const("📅 Current Month Expenses"), id="current_month_expenses", on_click=current_month_expense_handler),
        Button(Const("📆 Last Month Expenses"), id="last_month_expenses", on_click=last_month_expense_handler),
        Button(Const("📋 Last 15 Expenses"), id="last_15_expenses", on_click=last_n_expenses_handler),
        Button(Const("💼 Last 20 Income Entries"), id="last_20_incomes", on_click=last_n_incomes_handler),
        MAIN_MENU_BUTTON,
        state=states.Analytics.MAIN
    )
)