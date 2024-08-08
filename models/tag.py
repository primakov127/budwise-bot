from dataclasses import dataclass
from typing import Optional


@dataclass
class Tag:
    id: str
    name: str
    description: Optional[str]