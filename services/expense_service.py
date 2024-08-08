from typing import Any

from beanie import PydanticObjectId

from db import db
from models import Expense


class ExpenseService:
    def __init__(self):
        self.collection = db["expenses"]
        
    async def create_expense(self, expense: Expense) -> PydanticObjectId | None:
        await expense.insert()
        return expense.id
    
    async def get_expense(self, expense_id: Any) -> Expense | None:
        expense = await Expense.get(expense_id)
        return expense
    
    async def update_expense(self, expense: Expense, update_data: dict) -> int:
        updated_count = await expense.update({"$set": update_data})
        return updated_count
    
    async def list_expenses(self, user_id: str) -> list[Expense]:
        expenses = await Expense.find({"user_id": user_id}).to_list()
        return expenses
    
    async def delete_expense(self, expense: Expense) -> int:
        delete_result = await expense.delete()
        return delete_result.deleted_count