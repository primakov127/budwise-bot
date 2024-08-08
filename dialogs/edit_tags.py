from aiogram_dialog import Dialog, Window

from dialogs import states

edit_tags = Dialog(
    Window(
        state=states.EditTags.MAIN
    )
)
