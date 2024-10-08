from aiogram.fsm.state import State, StatesGroup


class Main(StatesGroup):
    MAIN = State()
    
class PersonalMenu(StatesGroup):
    MAIN = State()
    
class FamilyMenu(StatesGroup):
    MAIN = State()

class AddTransaction(StatesGroup):
    MAIN = State()
    SPECIFY_CATEGORY = State()
    SPECIFY_DESCRIPTION=State()
    SPECIFY_TAGS = State()
    CONFIRM = State()
    CHANGE_DATE = State()
    
class AddFamilyTransaction(StatesGroup):
    MAIN = State()
    SPECIFY_CATEGORY = State()
    SPECIFY_DESCRIPTION=State()
    SPECIFY_TAGS = State()
    CONFIRM = State()
    CHANGE_DATE = State()
    
class AddIncome(StatesGroup):
    MAIN = State()
    CONFIRM = State()
    SPECIFY_DESCRIPTION = State()
    CHANGE_DATE = State()
    
class AddFamilyIncome(StatesGroup):
    MAIN = State()
    CONFIRM = State()
    SPECIFY_DESCRIPTION = State()
    CHANGE_DATE = State()

class Analytics(StatesGroup):
    MAIN = State()
    
class FamilyAnalytics(StatesGroup):
    MAIN = State()
