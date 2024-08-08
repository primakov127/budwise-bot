from datetime import date
from typing import List, Optional

from beanie import Document


class Expense(Document):
    amount: float
    date: date
    description: Optional[str] = None
    category: str
    tags: Optional[List[str]] = None
    user_id: str
    
    class Settings:
        name = "expense"