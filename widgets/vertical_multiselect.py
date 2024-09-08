from typing import Dict

from aiogram_dialog import DialogManager
from aiogram_dialog.api.internal import RawKeyboard
from aiogram_dialog.widgets.kbd import Multiselect


class VerticalMultiselect(Multiselect):
    async def _render_keyboard(
            self,
            data: Dict,
            manager: DialogManager,
    ) -> RawKeyboard:
        keyboard = await super()._render_keyboard(data, manager)
        return [[item] for item in keyboard[0]]