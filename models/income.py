from datetime import date
from typing import Optional

from beanie import Document


class Income(Document):
    amount: float
    date: date
    description: Optional[str] = None
    user_id: str
    
    class Settings:
        name = "income"