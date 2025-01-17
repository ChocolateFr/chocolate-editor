from textual.app import App, ComposeResult
from textual.widgets import Modal, Static, Input, Button, Label
from textual.containers import Container


class PopupApp(App):
    CSS = """
    Modal {
        width: 50%;
        height: auto;
    }
    """
    
    def compose(self) -> ComposeResult:
        yield Button("Open Popup", id="open-popup")
        yield Modal(
            Container(
                Label("Enter your name:"),
                Input(placeholder="Your name here...", id="user-input"),
                Button("Submit", id="submit"),
            ),
            id="popup",
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "open-popup":
            self.query_one("#popup", Modal).open()
        elif event.button.id == "submit":
            input_value = self.query_one("#user-input", Input).value
            self.query_one("#popup", Modal).close()
            self.notify(f"You entered: {input_value}")


if __name__ == "__main__":
    PopupApp().run()
