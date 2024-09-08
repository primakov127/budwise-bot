from beanie import Document


class Category(Document):
    name: str
    
    class Settings:
        name = "category"