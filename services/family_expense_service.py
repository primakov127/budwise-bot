from datetime import datetime

from models import FamilyExpense


class FamilyExpenseService:
    async def get_current_month_expenses(user_id: str) -> list[dict]:
        current_month = datetime.now().month
        expenses_by_category = await FamilyExpenseService.get_month_expenses(user_id, current_month)
        
        return expenses_by_category

    async def get_month_expenses(user_id: str, month: int) -> list[dict]:
        expenses_by_category = await FamilyExpense.aggregate([
            {"$match": {
                "user_id": user_id,
                "$expr": {"$eq": [{"$month": "$date"}, month]}
            }},
            {"$lookup": {
                "from": "category",
                "localField": "category",
                "foreignField": "_id",
                "as": "category_info"
            }},
            {"$unwind": "$category_info"},
            {"$group": {
                "_id": "$category_info.name",
                "total_expenses": {"$sum": "$amount"}
            }},
            {"$project": {
                "category": "$_id",
                "amount": "$total_expenses",
            }}
        ]).to_list()
        
        return expenses_by_category
    
    async def get_last_n_expenses(user_id: str, n: int) -> list[dict]:
        expenses = await FamilyExpense.aggregate([
            {"$match": {"user_id": user_id}},
            {"$lookup": {
                "from": "category",
                "localField": "category",
                "foreignField": "_id",
                "as": "category_info"
            }},
            {"$unwind": "$category_info"},
            {"$sort": {"date": -1}},
            {"$limit": n},
            {"$project": {
                "date": 1,
                "amount": 1,
                "description": 1,
                "category": "$category_info.name"
            }}
        ]).to_list()
        
        return expenses
