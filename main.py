# main.py
import asyncio
import datetime

from beanie import init_beanie

from db import db
from models import Expense
from services import ExpenseService


async def main():
    service = ExpenseService()

    # Create an expense
    await init_beanie(db, document_models=[Expense])
    
    new_expense = Expense(
        amount=50.7,
        date=datetime.datetime.now(),
        description="Dinner",
        category="Food",
        tags=["tag1", "tag2"],
        user_id="user1"
    )
    expense_id = await service.create_expense(new_expense)
    print(f"Created Expense ID: {expense_id}")

    # Get an expense
    expense = await service.get_expense(expense_id)
    print(f"Retrieved Expense: {expense}")

    # Update an expense
    update_data = {"amount": 60.0}
    updated_count = await service.update_expense(expense, update_data)
    print(f"Updated Count: {updated_count}")

    # List expenses
    expenses = await service.list_expenses("user1")
    print(f"List of Expenses: {expenses}")

    # Delete an expense
    deleted_count = await service.delete_expense(expense)
    print(f"Deleted Count: {deleted_count}")

asyncio.run(main())