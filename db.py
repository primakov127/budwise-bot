import os

import motor.motor_asyncio
from beanie import init_beanie
from dotenv import load_dotenv

from models import Expense

# Load environment variables from .env file
load_dotenv()

password = os.getenv("MONGODB_PASSWORD")
connection_string = f"mongodb+srv://admin:{password}@primarycluster.3lfoyaq.mongodb.net/?retryWrites=true&w=majority&appName=PrimaryCluster"

client = motor.motor_asyncio.AsyncIOMotorClient(connection_string)
db = client['budwise']

async def init_db():
    await init_beanie(database=db, document_models=[Expense])