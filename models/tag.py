from typing import Optional

from beanie import Document


class Tag(Document):
    name: str
    description: Optional[str]
    
    class Settings:
        name = "tag"