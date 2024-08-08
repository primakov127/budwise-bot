from aiogram.fsm.state import State, StatesGroup


class Main(StatesGroup):
    MAIN = State()

class SettingsMenu(StatesGroup):
    MAIN = State()
    
class EditCategories(StatesGroup):
    MAIN = State()
    
class EditTags(StatesGroup):
    MAIN = State()

class AddTransaction(StatesGroup):
    MAIN = State()
    SPECIFY_CATEGORY = State()
    CONFIRM = State()
    CHANGE_DATE = State()