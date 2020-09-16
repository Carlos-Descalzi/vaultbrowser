import logging

logging.basicConfig(
    filename="vaultbrowser.log", format="%(message)s", level=logging.DEBUG
)
from .util import kbd, ansi
from .util.ui import Application, TextView, TreeView, Rect, TitledView, ListView, COLORS, QuestionDialog
from .vault import VaultListModel
import json
import tempfile
import subprocess
import os
import configparser
import sys


class VaultBrowser(Application):
    def __init__(self):
        super().__init__()

        COLORS["menu.bg"] = "\u001b[48;5;241m"
        COLORS["menu.fg"] = "\u001b[38;5;255m\u001b[1m"

        max_height, max_width = ansi.terminal_size()

        menu = TextView(
            rect=Rect(1,1,max_width,1),
            text="Enter: View - a: Add - e: Edit - d: Delete - TAB: cycle focus - ESC: Exit"
        )
        menu.color_key_prefix = 'menu'
        menu.focusable = False

        self.add_component(menu)

        self._list_model = VaultListModel()
        self._tree = ListView(
            rect=Rect(1,2,40,max_height-2),
            model=self._list_model
        )
        self._tree.selectable = True
        self._tree.on_select.add(self._on_select)
        self._tree_title = TitledView(
            rect=Rect(1,2,40,max_height-2),
            title=str(self._list_model.get_root()),
            inner=self._tree
        )
        self.add_component(self._tree_title)

        self._textview = TextView()
        self._textview.color_key_prefix = 'valueview'
        self._breadcrumb = TitledView(
            rect=Rect(41,2,max_width-40,max_height-2),
            title="",
            inner=self._textview
        )
        self.add_component(self._breadcrumb)

        self.set_key_handler(kbd.keystroke_from_str("a"), self._do_add)
        self.set_key_handler(kbd.keystroke_from_str("e"), self._do_edit)
        self.set_key_handler(kbd.keystroke_from_str("d"), self._do_delete)

        self._read_config()
        self.set_focused_view(self._tree_title)

    def _read_config(self):
        config_file = self.get_config_file()
        parser = configparser.ConfigParser()
        parser.read(config_file)
        self._editor = parser["DEFAULT"]["editor"]
        self._highlighter = parser["DEFAULT"].get("highlighter")
        logging.info(self._highlighter)

    def get_config_file(self):
        config_dir = os.path.join(os.environ['HOME'], ".vaultbrowser")
        if not os.path.isdir(config_dir):
            os.makedirs(config_dir)
        config_file = os.path.join(config_dir, "init.conf")
        if not os.path.isfile(config_file):
            # Write default configuration
            template=(
                "[DEFAULT]\n"
                +"editor=/usr/bin/vi\n"
            )
            # Put as default a well known json highlighter
            if os.path.isfile('/usr/bin/jq'):
                template+="highlighter=cat {file}|/usr/bin/jq -C\n"
            else:
                template+="#highlighter=/path/to/some/json/highlighter {file}"

            with open(config_file, "w") as f:
                f.write(template)
        return config_file

    def _on_select(self, tree, item):
        try:
            if item == '..':
                tree.model.go_up()
                self._set_path_title(tree.model.get_current().path)
            elif item.leaf:
                self._show_selected_item(item)
            else:
                tree.model.go_to(item)
                self._set_path_title(item.path)
        except Exception as e:
            import traceback
            logging.error(f'{e} - {traceback.format_exc()}')

    def _show_selected_item(self, item):
        value = item.value#["data"]
        self._breadcrumb.title = item.path

        if self._highlighter:
            tf = tempfile.NamedTemporaryFile(mode="w+", suffix=".json")
            json.dump(value, tf, indent=4)
            tf.flush()
            try:
                result = subprocess.check_output(
                    self._highlighter.format(file=tf.name),
                    shell=True
                )
                self._textview.text = result.decode()
            except Exception as e:
                logging.error(e)
                self._textview.text = json.dumps(value, indent=4)
        else:
            self._textview.text = json.dumps(value, indent=4)

    def _set_path_title(self, path):
        if len(path) > 40:
            path = path[-40:]
        self._tree_title.title = path


    def _do_add(self,*_):
        selected = self._tree.model.get_current()

        dummy_name = "[NAME OF THE ELEMENT]"

        tf = tempfile.NamedTemporaryFile(mode="w+", suffix=".json")
        json.dump({"name": dummy_name, "data": {"value": ""}}, tf, indent=4)
        tf.flush()

        result = subprocess.run([self._editor, tf.name])

        if result.returncode == 0:
            tf.seek(0)
            try:
                edited_stuff = json.load(tf)

                name = edited_stuff["name"]
                data = edited_stuff["data"]

                if name != dummy_name:
                    selected.add_child(name, data)
                    self._textview.text = json.dumps(data, indent=4)
            except ValueError as e:
                logging.error(e)
            except Exception as e:
                logging.error(e)
        self.refresh()

    def _do_edit(self, *_):
        selected = self._tree.current_item

        value = selected.value
        tf = tempfile.NamedTemporaryFile(mode="w+", suffix=".json")
        json.dump(value["data"], tf, indent=4)
        tf.flush()

        result = subprocess.run([self._editor, tf.name])

        if result.returncode == 0:
            tf.seek(0)
            try:
                edited_stuff = json.load(tf)
                selected.value = edited_stuff
                self._textview.text = json.dumps(selected.value, indent=4)
            except ValueError as e:
                logging.error(e)
        self.refresh()

    def _do_delete(self, *_):
        parent = self._tree.model.get_current()
        item = self._tree.current_item
        def confirm():
            item.remove()
            self._tree.model.remove_child(item)
        def cancel():
            pass

        self.show_question_dialog(
            "Warning",
            "Sure you want to delete? (y/n)",
            [('y', "Yes", confirm), ('n', "No", cancel)]
        )

    def show_question_dialog(self, title, message, options):
        def _wrap_op(f):
            def call():
                f()
                self.close_popup()

            return call

        options = [(k, l, _wrap_op(f)) for k, l, f in options]
        dialog = QuestionDialog(title, message, options)
        self.open_popup(dialog)

def main():
    if not "VAULT_ADDR" in os.environ or not "VAULT_TOKEN" in os.environ:
        print("Missing environment variables: VAULT_ADDR and/or VAULT_TOKEN")
        sys.exit(1)

    explorer = VaultBrowser()
    explorer.main_loop()

if __name__ == "__main__":
    main()
