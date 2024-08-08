from abc import abstractmethod
from typing import Any, Protocol, Union

from aiogram.types import CallbackQuery, InlineKeyboardButton

from aiogram_dialog.api.internal import RawKeyboard
from aiogram_dialog.api.protocols import DialogManager, DialogProtocol
from aiogram_dialog.widgets.common import ManagedWidget, WhenCondition
from aiogram_dialog.widgets.kbd.base import Keyboard
from aiogram_dialog.widgets.text import Format
from aiogram_dialog.widgets.widget_event import (
    ensure_event_processor,
    WidgetEventProcessor,
)

DEFAULT_NUMPAD_TEXT = Format("Value: {value}")

class OnNumpadEvent(Protocol):
    @abstractmethod
    async def __call__(
        self,
        event: Any,
        widget: "ManagedNumpad",
        dialog_manager: DialogManager,
        value: str,
    ):
        raise NotImplementedError

OnNumpadEventVariant = Union[OnNumpadEvent, WidgetEventProcessor, None]

class Numpad(Keyboard):
    def __init__(
        self,
        id: str,
        default: str = "",
        on_value_changed: OnNumpadEventVariant = None,
        when: WhenCondition = None,
    ) -> None:
        super().__init__(id=id, when=when)
        self.default = default
        self.on_value_changed = ensure_event_processor(on_value_changed)
        self.text = DEFAULT_NUMPAD_TEXT
        self.keyboard_values = [
            ["1", "2", "3"],
            ["4", "5", "6"],
            ["7", "8", "9"],
            [".", "0", "<-"]
        ]
        
    def get_value(self, manager: DialogManager) -> str:
        return self.get_widget_data(manager, self.default)
        
    async def set_value(self, manager: DialogManager, value: str) -> None:
        self.set_widget_data(manager, value)
        await self.on_value_changed.process_event(
            manager.event,
            self.managed(manager),
            manager,
            value
        )
    
    async def _render_keyboard(self, data: dict, manager: DialogManager) -> RawKeyboard:
        keyboard = [
            [InlineKeyboardButton(text=value, callback_data=self._item_callback_data(value)) for value in row]
            for row in self.keyboard_values
        ]
        
        return keyboard
    
    async def _process_item_callback(
        self,
        callback: CallbackQuery,
        data: str,
        dialog: DialogProtocol,
        manager: DialogManager
    ) -> bool:
        value = self.get_value(manager)
        
        if data.isdigit() or data == ".":
            value += data
            await self.set_value(manager, value)
        elif data == "<-":
            value = value[:-1]
            await self.set_value(manager, value)
            
        return True
    
    def managed(self, manager: DialogManager):
        return ManagedNumpad(self, manager)

    
class ManagedNumpad(ManagedWidget[Numpad]):
    def get_value(self) -> str:
        return self.widget.get_value(self.manager)
    
    async def set_value(self, value: str) -> None:
        await self.widget.set_value(self.manager, value)