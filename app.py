from os.path import abspath, isdir
from textual.app import App, ComposeResult
from textual.widgets import Footer, Header, TextArea, Label, Button, Input, Tree
from textual.containers import HorizontalGroup, VerticalGroup, VerticalScroll
import os
import sys
from textual import on

import shutil


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


def path_finder(event: Tree.NodeSelected):
    path = [event.node]
    while path[-1].parent:
        path.append(path[-1].parent)
    path = path[:-1]
    path.reverse()
    path = [str(i.label)[2:] for i in path]
    return "/".join(path)


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
        ("d", "toggle_dark", "Toggle dark mode"),
        ("ctrl+s", "save", "Save File"),
        ("ctrl+l", "left", "Left Side Focus."),
        ("ctrl+r", "right", "Right Side Focus."),
        ("ctrl+f", "new_file", "New File."),
        ("ctrl+n", "new_dir", "New Directory."),
        ("ctrl+g", "rm", "Remove"),
    ]
    stage = "makefile"
    path = os.getcwd() if len(sys.argv) == 1 else sys.argv[1]
    path = os.path.abspath(path)

    CSS_PATH = "style.css"
    file_name = ""
    fix_path = lambda self: os.chdir(self.path)
    search = ""
    action_left = lambda self: self.set_focus(self.files)
    action_right = lambda self: self.set_focus(self.text_area)

    def action_new_dir(self):
        self.stage = "makedir"
        self.text_area.add_class("hide")
        self.ask_box.remove_class("hide")

    def action_rm(self):
        self.stage = "rm"
        self.text_area.add_class("hide")
        self.ask_box.remove_class("hide")

    def action_new_file(self):
        self.stage = "makefile"
        self.text_area.add_class("hide")
        self.ask_box.remove_class("hide")

    def on_tree_node_selected(self, event: Tree.NodeSelected):
        file = path_finder(event)

        if not file:
            return
        if not os.path.isdir(file):
            self.open_file(file)
            # elif file.encode

    def open_file(self, file):
        self.text_area.text = open(file).read()
        self.file_name = file
        self.text_area.show_line_numbers = True
        self.text_area.refresh(recompose=True)

        if file.endswith(".py") or file.endswith(".pyw"):
            self.text_area.language = "python"

    def on_button_pressed(self, event: Button.Pressed):
        result = self.ask.value.strip()
        if event.button.id == "submit" and result:
            if self.stage == "makefile":
                open(result, "+w").close()
                self.open_file(result)
            elif self.stage == "makedir":
                os.mkdir(result)
            elif self.stage == "rm":
                remove_path(result)
            self.ask_box.add_class("hide")
            self.text_area.remove_class("hide")
            self.refresh(recompose=True)

    def build(self):
        self.ask = Input(placeholder="Type something")
        self.submit = Button("Submit", id="submit", variant="success")
        self.cancel = Button("Cancel", id="cancel", variant="error")
        self.ask_box = VerticalGroup(
            self.ask, HorizontalGroup(self.submit, self.cancel)
        )
        self.ask_box.add_class("hide")
        self.text_area = TextArea()
        self.files = VerticalScroll(
            create_directory_tree(self.path), id="vertical_scroll"
        )
        return HorizontalGroup(self.files, self.text_area, self.ask_box)

    def compose(self) -> ComposeResult:
        self.fix_path()
        yield Header()
        yield self.build()
        yield Footer()

    def action_toggle_dark(self) -> None:
        self.theme = (
            "textual-dark" if self.theme == "textual-light" else "textual-light"
        )

    def action_save(self):
        try:
            with open(self.file_name, "+w") as fp:
                fp.write(self.text_area.text)
            self.notify("File saved.")
        except PermissionError:
            self.notify("Permission Error.", severity="error")


if __name__ == "__main__":
    app = ChocolateEditor()
    app.run()
