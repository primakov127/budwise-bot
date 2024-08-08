from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.kbd import Start
from aiogram_dialog.widgets.text import Const

from dialogs import states
from dialogs.common import MAIN_MENU_BUTTON

settings_menu = Dialog(
    Window(
        Const("Settings menu:"),
        Start(Const("Edit categories"), state=states.EditCategories.MAIN, id="edit_categories"),
        Start(Const("Edit tags"), state=states.EditTags.MAIN, id="edit_tags"),
        MAIN_MENU_BUTTON,
        state=states.SettingsMenu.MAIN
    )
)
