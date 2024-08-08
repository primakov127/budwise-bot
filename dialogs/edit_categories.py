from aiogram_dialog import Dialog, Window

from dialogs import states

edit_categories = Dialog(
    Window(
        state=states.EditCategories.MAIN
    )
)
