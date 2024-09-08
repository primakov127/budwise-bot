from datetime import date
from typing import List, Optional

from beanie import Document
from bson import ObjectId


class Expense(Document):
    amount: float
    date: date
    description: Optional[str] = None
    category: ObjectId
    tags: Optional[List[ObjectId]] = None
    user_id: str
    
    class Settings:
        name = "expense"
        
    class Config:
        arbitrary_types_allowed = True