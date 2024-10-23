from datetime import datetime

from models import FamilyIncome


class FamilyIncomeService:
    async def get_current_month_incomes(user_id: str) -> list[dict]:
        month = datetime.now().month
        year = datetime.now().year
        incomes = await FamilyIncome.aggregate([
            {"$match": {
                "user_id": user_id,
                "$expr": {
                    "$and": [
                        {"$eq": [{"$month": "$date"}, month]},
                        {"$eq": [{"$year": "$date"}, year]}
                    ]
                }
            }},
            {"$group": {
                "_id": None,
                "total_income": {"$sum": "$amount"}
            }},
            {"$project": {
                "_id": 0,
                "total_income": 1
            }}
        ]).to_list()
        
        return incomes[0] if incomes else {"total_income": 0}
    
    async def get_last_n_incomes(user_id: str, n: int) -> list[dict]:
        incomes = await FamilyIncome.find(FamilyIncome.user_id == user_id).sort(-FamilyIncome.date).limit(n).to_list()
        
        return [
            {
                "date": income.date,
                "amount": income.amount,
                "description": income.description
            } for income in incomes
        ]