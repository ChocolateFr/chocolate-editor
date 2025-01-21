from textual.app import App, ComposeResult
from textual.widgets import Header, Label
from textual.containers import (
    HorizontalGroup,
    HorizontalScroll,
    VerticalGroup,
    VerticalScroll,
)
from textual.suggester import SuggestFromList
from textual import events
import utils
import os
import sys
import widgets
import watchdict

AUTO_CLOSE = {"[": "[]", "{": "{}", "(": "()", "'": "''", '"': '""'}
config = watchdict.WatchDict("config.json")


class ChocolateEditor(App):
    CSS_PATH = "style.css"
    BINDINGS = [
        ("ctrl+s", "save", "Save File"),
        ("ctrl+l", "command_line", "Command Line."),
        ("ctrl+j", "j", "Left Tab"),
        ("ctrl+i", "k", "Right Tab"),
        ("ctrl+r", "r", "Close tab"),
        ("i", "insert", "Insert Mode"),
    ]

    def __init__(self):
        super().__init__()
        self.text_area = widgets.ExtendedTextArea(
            self,
            config,
            id="text-area",
            tab_behavior="indent",
        )
        self.cmd_open = False
        self.files_list = []
        self.file_index = 0
        self.tabs = HorizontalScroll(id="tabs")


    def action_r(self):
        self.files_list.pop(self.file_index)
        self.file_index = 0
        self.action_j()
        self.refresh(recompose=True)

    def action_insert(self):
        self.set_focus(self.text_area)

    def action_j(self):
        if len(self.files_list) == 0:
            self.text_area.text = ""
            return
        if self.file_index == 0:
            self.file_index = len(self.files_list) - 1
        else:
            self.file_index -= 1
        self.open_file(self.files_list[self.file_index])

    def action_k(self):
        if len(self.files_list) == 0:
            self.text_area.text = ""
            return
        if self.file_index >= len(self.files_list) - 1:
            self.file_index = 0
        else:
            self.file_index += 1
        self.open_file(self.files_list[self.file_index])

    def action_command_line(self):
        if not self.cmd_open:
            self.ask_box.remove_class("hide")
            self.set_focus(self.ask)
            self.cmd_open = True
        else:

            self.ask_box.add_class("hide")
            self.cmd_open = False

    def open_file(self, file):
        if not os.path.exists(file):
            self.notify("ERROR: this file does not exists.", severity="error")
            return
        if file not in self.files_list:
            self.files_list.append(file)
            self.file_index = len(self.files_list) - 1

        try:
            self.files_list
            with open(file) as f:
                content = f.read()
            self.text_area.load_text(content)  # Load text into TextArea
            self.file_name = file

            # Update appearance and focus
            self.text_area.show_line_numbers = True
            self.set_focus(self.text_area)
            self.refresh(recompose=True)

            # Set syntax highlighting based on file type
            if file.endswith(".py") or file.endswith(".pyw"):
                self.text_area.language = "python"
            elif file.endswith(".lua"):
                self.text_area.language = "lua"
            elif file.endswith(".css"):
                self.text_area.language = "css"
            elif file.endswith(".html"):
                self.text_area.language = "html"
            elif file.endswith(".js"):
                self.text_area.language = "javascript"
            elif file.endswith(".ts"):
                self.text_area.language = "typescript"
            elif file.endswith(".java"):
                self.text_area.language = "java"
            elif file.endswith(".c"):
                self.text_area.language = "c"
            elif file.endswith(".cpp"):
                self.text_area.language = "cpp"
            elif file.endswith(".h"):
                self.text_area.language = (
                    "cpp"  # Assuming header files are C/C++-related
                )
            elif file.endswith(".json"):
                self.text_area.language = "json"
            elif file.endswith(".xml"):
                self.text_area.language = "xml"
            elif file.endswith(".yaml") or file.endswith(".yml"):
                self.text_area.language = "yaml"
            elif file.endswith(".go"):
                self.text_area.language = "go"
            elif file.endswith(".ruby"):
                self.text_area.language = "ruby"
            elif file.endswith(".php"):
                self.text_area.language = "php"
            elif file.endswith(".sql"):
                self.text_area.language = "sql"
            elif file.endswith(".bash"):
                self.text_area.language = "bash"
            elif file.endswith(".sh"):
                self.text_area.language = "bash"
            elif file.endswith(".swift"):
                self.text_area.language = "swift"
            else:
                self.text_area.language = None

        except Exception as e:
            self.notify(f"Error opening file: {e}", severity="error")

    def submit_value(self, event):
        result = self.ask.value.strip()
        if event == "submit" and result:
            if result.startswith("."):
                result = result.split(" ", 1)
                if result[0] == config["prefixes"][0]:
                    open(result[1], "+w").close()
                    self.open_file(result[1])
                    self.set_focus(self.text_area)
                elif result[0] == config["prefixes"][1]:
                    utils.remove_path(result[1])
                elif result[0] == config["prefixes"][2]:
                    self.open_file(result[1])
                elif result[0] == config["prefixes"][3]:
                    with open(result[1], "+w") as fp:
                        fp.write(self.text_area.text)

        self.ask_box.add_class("hide")

    def build(self):
        self.ask = widgets.ExtendedInput(
            self,
            placeholder=config["texts"].get("cmd_placeholder", "CMD"),
            id="ask",
            suggester=SuggestFromList(utils.prefixer(config["prefixes"])),
        )
        self.ask_box = self.ask
        self.ask_box.add_class("hide")
        tabs = []
        for i in self.files_list:
            l = Label(i)
            l.add_class("file")
            tabs.append(l)

        if len(tabs):
            tabs[self.file_index].add_class("selected")
        self.tabs._add_children(*tabs)
        return VerticalGroup(self.tabs, self.text_area, self.ask_box)

    def compose(self) -> ComposeResult:
        yield Header(config["header"]["show_time"], icon=config["header"]["logo"])
        yield self.build()

    def action_save(self):
        try:
            with open(self.file_name, "+w") as fp:
                fp.write(self.text_area.text)
            self.notify(config["texts"].get("file_saved", "File Saved."))
        except Exception as err:
            self.notify(str(err), severity="error")


if __name__ == "__main__":
    app = ChocolateEditor()
    app.run()
