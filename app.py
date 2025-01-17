from os.path import isdir
from textual.app import App, ComposeResult
from textual.widgets import Footer, Header, TextArea, Label, Button
from textual.containers import HorizontalGroup, VerticalScroll
import os



class ChocolateEditor(App):
    BINDINGS = [
        ("d", "toggle_dark", "Toggle dark mode"),
        ("ctrl+s", "save", "Save File")
        ]
    path = os.getcwd()
    files = []
    CSS_PATH='style.css'
    file_name = ''

    def get_files(self):
        files = os.listdir(self.path)
        result = []
        
        for file in files:
            if isdir(file):
                result.append(Button(f' {file}', classes='dirs'))
            else:
                result.append(Button(f' {file}', classes='files'))
        return result

    def on_button_pressed(self,event:Button.Pressed):
        if 'files' in event.button.classes:
            self.file_name = str(event.button.label[2:])
            self.text_area.text = open(self.file_name).read()
            self.text_area.refresh(recompose=True)
            self.notify(f'File {self.file_name} loaded.')

    

    def build(self):
        self.text_area = TextArea()
        self.files = VerticalScroll(*self.get_files(), id='vertical_scroll')
        return HorizontalGroup(self.files,self.text_area)


    def compose(self) -> ComposeResult:

        yield Header()
        yield self.build()
        yield Footer()

    def action_toggle_dark(self) -> None:
        self.theme = (
            "textual-dark" if self.theme == "textual-light" else "textual-light"
        )

    def action_save(self):
        with open(self.file_name, '+w') as fp:
            fp.write(self.text_area.text)
        self.notify('File saved.')

if __name__ == "__main__":
    app = ChocolateEditor()
    app.run()
