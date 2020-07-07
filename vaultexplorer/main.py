import logging

logging.basicConfig(
    filename="vaultexplorer.log", format="%(message)s", level=logging.DEBUG
)
from .tui import Screen, TreeView, TextView, Label
from .vault import VaultTreeModel
import curses
import json
import tempfile
import subprocess
import os
import configparser
import sys


class VaultExplorer:
    def __init__(self):
        self.read_config()
        self.screen = Screen()
        h, w = self.screen.get_size()

        menu = Label(
            "Enter: View - A: Add - E: Edit - D: Delete - TAB: cycle focus - q: Exit"
        )
        menu.set_bounds(0, 0, w - 1, 1)
        menu.attr = curses.A_REVERSE
        self.screen.add(menu)

        self.tree = TreeView()
        self.tree.model = VaultTreeModel()
        self.tree.set_bounds(0, 1, 40, h - 2)
        self.tree.add_select_listener(self.on_select)
        self.screen.add(self.tree)
        self.screen.focus(self.tree)

        self.textview = TextView()
        self.textview.set_bounds(41, 2, w - 42, h - 3)
        self.screen.add(self.textview)

        self.breadcrumb = Label("")
        self.breadcrumb.attr = curses.A_REVERSE
        self.breadcrumb.set_bounds(41, 1, w - 42, 1)
        self.screen.add(self.breadcrumb)

        self.screen.add_keybinding("A", self.do_add)
        self.screen.add_keybinding("E", self.do_edit)
        self.screen.add_keybinding("D", self.do_delete)

        self.screen.refresh()

    def read_config(self):
        config_file = self.get_config_file()
        parser = configparser.ConfigParser()
        parser.read(config_file)
        self._editor = parser["DEFAULT"]["editor"]

    def get_config_file(self):
        config_dir = os.path.join(os.environ['HOME'], ".config/vaultbrowser")
        if not os.path.isdir(config_dir):
            os.makedirs(config_dir)
        config_file = os.path.join(config_dir, "init.conf")
        if not os.path.isfile(config_file):
            with open(config_file, "w") as f:
                f.write("[DEFAULT]\neditor=/usr/bin/vi\n")
        return config_file

    def run(self):
        self.screen.run()

    def on_select(self, tree, path):
        selected = tree.model.get_item_at(path)
        value = selected.value()

        if value:
            path_str = self.convert_path(path)
            self.breadcrumb.set_text(path_str)
            self.textview.text = json.dumps(value["data"], indent=4)
        else:
            self.breadcrumb.set_text("")
            self.textview.set_text("")

    def convert_path(self, path):
        model = self.tree.model

        path_items = [str(model.get_root())]

        subpath = []
        for item in path:
            subpath.append(item)
            path_items.append(str(model.get_item_at(subpath)))

        return "/".join(path_items)

    def do_add(self):
        path = self.tree.current_path

        dummy_name = "[NAME OF THE ELEMENT]"

        tf = tempfile.NamedTemporaryFile(mode="w+", suffix=".json")
        json.dump({"name": dummy_name, "data": {"value": ""}}, tf, indent=4)
        tf.flush()

        self.screen.drop_window()

        result = subprocess.run([self._editor, tf.name])

        self.screen.restart()

        if result.returncode == 0:
            self.screen.refresh()
            tf.seek(0)
            try:
                edited_stuff = json.load(tf)

                name = edited_stuff["name"]
                data = edited_stuff["data"]

                if name != dummy_name:
                    self.tree.add_child(path, name=name, data=data)
                    self.textview.text = json.dumps(data, indent=4)
            except ValueError:
                pass  # todo handle bad format

    def do_edit(self):
        path = self.tree.current_path
        selected = self.tree.model.get_item_at(path)
        value = selected.value()
        tf = tempfile.NamedTemporaryFile(mode="w+", suffix=".json")
        json.dump(value["data"], tf, indent=4)
        tf.flush()

        self.screen.drop_window()

        result = subprocess.run([self._editor, tf.name])

        self.screen.restart()

        if result.returncode == 0:
            self.screen.refresh()
            tf.seek(0)
            try:
                edited_stuff = json.load(tf)
                selected.set_value(edited_stuff)
                self.textview.text = json.dumps(edited_stuff, indent=4)
            except ValueError:
                pass  # todo handle bad format

    def do_delete(self):

        text = self.breadcrumb.text
        self.breadcrumb.text = "Sure you want to delete? (y/n)"

        def forget_delete():
            self.screen.delete_keybinding("y")
            self.screen.delete_keybinding("n")
            self.breadcrumb.text = text
            self.screen.focus(self.tree)

        def confirm_delete():
            self.screen.delete_keybinding("y")
            self.screen.delete_keybinding("n")
            self.breadcrumb.text = text
            self.screen.focus(self.tree)
            path = self.tree.current_path
            self.tree.remove(path)

        self.screen.add_keybinding("y", confirm_delete)
        self.screen.add_keybinding("n", forget_delete)

def main():
    if not "VAULT_ADDR" in os.environ or not "VAULT_TOKEN" in os.environ:
        print("Missing environment variables: VAULT_ADDR and/or VAULT_TOKEN")
        sys.exit(1)

    explorer = VaultExplorer()
    explorer.run()
    logging.shutdown()

if __name__ == "__main__":
    main()
