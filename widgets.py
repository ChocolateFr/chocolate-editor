from textual.widgets import Input, TextArea
from textual import events
from textual.app import App
import utils


class ExtendedInput(Input):
    def __init__(self, app: App, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._app = app

    def _on_key(self, event: events.Key) -> None:
        if event.name == "enter":
            self._app.submit_value("submit")
        elif event.name == "escape":
            self._app.submit_value("cancel")


class ExtendedTextArea(TextArea):
    def __init__(self, app, config, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.auto_close = config["auto_close"]
        self.config = config
        self._app = app

    def _on_key(self, event: events.Key) -> None:
        if event.character in self.auto_close:
            self.insert(self.auto_close[event.character])
            self.move_cursor_relative(columns=-1)
            event.prevent_default()

        elif event.name == "ctrl_l":
            self._app.action_command_line()

        elif event.name == "enter":
            s = self.get_cursor_down_location()[0]
            s = utils.get_required_indentation(self.text, s)
            self.insert("\n" + s)
            event.prevent_default()

        elif event.name == "ctrl_backspace":
            self.action_delete_word_left()

        elif event.key == "tab":
            self.insert("   ")

    def get_offset(self):
        return self.get_cursor_down_location()
