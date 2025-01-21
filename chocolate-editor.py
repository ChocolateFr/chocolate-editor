from textual.app import App, ComposeResult
from textual.widgets import Footer, Header, TextArea, Label, Button, Input, Tree, Select
from textual.containers import (
    HorizontalGroup,
    HorizontalScroll,
    VerticalGroup,
    VerticalScroll,
)
import re
from textual.suggester import SuggestFromList
from textual import events
import utils
import os
import sys
import shutil
import watchdict

AUTO_CLOSE = {"[": "[]", "{": "{}", "(": "()", "'": "''", '"': '""'}
config = watchdict.WatchDict("config.json")


class ExtendedTextArea(TextArea):

    """A subclass of TextArea with parenthesis-closing functionality."""

    def _on_key(self, event: events.Key) -> None:
        
        if event.character in AUTO_CLOSE:
            self.insert(AUTO_CLOSE[event.character])
            self.move_cursor_relative(columns=-1)
            event.prevent_default()

        elif event.name == 'ctrl_l':
            app.action_command_line()

        elif event.name == 'enter':
            s = self.get_cursor_down_location()[0]
            s = utils.get_required_indentation(self.text,s)
            self.insert('\n'+s)
            event.prevent_default()
        
        elif event.name == 'ctrl_backspace':
            self.action_delete_word_left()
            

            
        elif event.key == 'tab':
            self.insert('   ')

        self.auto_complete()
        
        
        

    def get_offset(self):
        return self.get_cursor_down_location()
    
    def auto_complete(self):
        res = utils.get_comp(self.text, self.get_offset()[0])
        global suggestions
        suggestions = res
        app.refresh(recompose=True)

suggestions = []
            
def get_comp(code):
    comps = utils.get_comp(code)
    comps = [Label(i) for i in comps]
    return VerticalScroll(*comps)

class ExtendedInput(Input):
    def _on_key(self, event: events.Key) -> None:
        if event.name == "enter":
            app.submit_value("submit")
        elif event.name == "escape":
            app.submit_value("cancel")


def remove_path(path: str) -> bool:
    try:
        if os.path.isfile(path):
            os.remove(path)
        elif os.path.isdir(path):
            shutil.rmtree(path)
        else:
            return False
        return True
    except Exception:
        return False


def create_directory_tree(path: str) -> Tree:

    tree = Tree(f" {os.path.basename(path)}")  # Root node with the base folder name

    def populate_tree(node, current_path):
        try:
            for item in sorted(os.listdir(current_path)):
                item_path = os.path.join(current_path, item)
                if os.path.isdir(item_path):
                    folder_node = node.add(f" {item}", allow_expand=True)
                    populate_tree(folder_node, item_path)  # Recurse into subdirectories
                else:
                    node.add(f" {item}")
        except PermissionError:
            node.add("🔒 Access Denied")

    populate_tree(tree.root, path)

    return tree


class ChocolateEditor(App):
    BINDINGS = [
        ("ctrl+s", "save", "Save File"),
        ("ctrl+l", "command_line", "Command Line."),
        ("ctrl+j", "j", "Left Tab"),
        ("ctrl+i", "k", "Right Tab"),
        ("ctrl+r", "r", "Close tab"),
        ("i", "insert", "Insert Mode"),
        
    ]
    text_area = ExtendedTextArea(id="text-area", tab_behavior='indent',)
    cmd_open = False
    path = os.getcwd() if len(sys.argv) == 1 else sys.argv[1]
    path = os.path.abspath(path)
    files_list = []
    CSS_PATH = "style.css"
    file_index = 0
    action_left = lambda self: self.set_focus(self.files)
    action_right = lambda self: self.set_focus(self.text_area)
    tabs = HorizontalScroll(id="tabs")

    def action_r(self):
        self.files_list.pop(self.file_index)
        self.file_index = 0
        self.action_j()
        self.refresh(recompose=True)

    def action_insert(self):
        self.set_focus(self.text_area)

    def action_j(self):
        if len(self.files_list) == 0:
            self.text_area.text = ''
            return
        if self.file_index == 0:
            self.file_index = len(self.files_list) - 1
        else:
            self.file_index -= 1
        self.open_file(self.files_list[self.file_index])

    def action_k(self):
        if len(self.files_list) == 0:
            self.text_area.text = ''
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
            self.notify("ERROR: this file does not exists.", severity='error')
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
                self.text_area.language = "cpp"  # Assuming header files are C/C++-related
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
                if result[0] == ".n":
                    open(result[1], "+w").close()
                    self.open_file(result[1])
                    self.set_focus(self.text_area)
                elif result[0] == ".r":
                    remove_path(result[1])

                elif result[0] == ".o":
                    self.open_file(result[1])

        self.ask_box.add_class("hide")
        self.refresh(recompose=True)

    def build(self):
        self.ask = ExtendedInput(
            placeholder="Type something",
            id="ask",
            suggester=SuggestFromList(utils.prefixer([".w", ".o", ".r", ".m"])),
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
        yield Header(True,icon=' ')
        yield self.build()
        if len(suggestions):
            yield VerticalScroll(
                *[Label(i) for i in suggestions]
            )
        
        

    def action_save(self):
        try:
            with open(self.file_name, "+w") as fp:
                fp.write(self.text_area.text)
            self.notify("File saved.")
        except Exception as err:
            self.notify(str(err), severity="error")


if __name__ == "__main__":
    app = ChocolateEditor()
    app.run()
