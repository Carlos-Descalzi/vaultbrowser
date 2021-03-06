import logging

logging.basicConfig(
    filename="vaultbrowser.log", format="%(message)s", level=logging.DEBUG
)
from cdtui import (
    ansi,
    kbd,
    Application,
    TextView,
    TreeView,
    Rect,
    TitledView,
    ListView,
    COLORS,
    QuestionDialog,
    InputDialog,
)
from . import misc, texts
from .vault import VaultListModel, ServicesListModel, BackendListModel
from .service import Service
import json
import tempfile
import subprocess
import configparser
import traceback
import sys
import os


class VaultBrowser(Application):
    def __init__(self):
        super().__init__()

        # COLORS["menu.bg"] = "\u001b[48;5;241m"
        # COLORS["menu.fg"] = "\u001b[38;5;255m\u001b[1m"

        max_height, max_width = ansi.terminal_size()

        self._services_model = ServicesListModel()
        self._services_list = ListView(model=self._services_model, selectable=True)
        self._services_list.item_renderer = self._render_service
        self._services_list.on_select.add(self._on_service_selected)

        self._backends_model = BackendListModel()
        self._backends_list = ListView(model=self._backends_model, selectable=True)
        self._backends_list.on_select.add(self._on_backend_selected)
        self._backends_list.item_renderer = self._render_backend

        self._vault_model = VaultListModel()
        self._tree = ListView(model=self._vault_model, selectable=True)
        self._tree.on_select.add(self._on_select)

        h1 = int((max_height - 1) / 4)
        w1 = int(max_width / 3)

        services_title = TitledView(
            rect=Rect(1, 1, w1, h1), title="Services", inner=self._services_list
        )
        self.add_component(services_title)
        self._backends_title = TitledView(
            rect=Rect(1, h1 + 1, w1, h1), title="Backends", inner=self._backends_list
        )
        self.add_component(self._backends_title)
        self._tree_title = TitledView(
            rect=Rect(1, h1 * 2 + 1, w1, max_height - (h1 * 2 + 2)),
            title="",
            inner=self._tree,
        )
        self.add_component(self._tree_title)

        self._textview = TextView()
        self._textview.color_key_prefix = "valueview"
        self._breadcrumb = TitledView(
            rect=Rect(w1 + 1, 1, max_width - (w1 + 1), max_height - 2),
            title="",
            inner=self._textview,
        )
        self.add_component(self._breadcrumb)

        self.set_key_handler(kbd.keystroke_from_str("a"), self._do_add, False)
        self.set_key_handler(kbd.keystroke_from_str("e"), self._do_edit, False)
        self.set_key_handler(kbd.keystroke_from_str("d"), self._do_delete, False)
        self.set_key_handler(kbd.keystroke_from_str("D"), self._do_delete_recursively, False)
        self.set_key_handler(kbd.keystroke_from_str("E"), self._do_export, False)
        self.set_key_handler(kbd.keystroke_from_str("h"), self._show_help, False)

        self._read_config()
        self.set_focused_view(services_title)

    def show_question_dialog(self, title, message, options):
        def _wrap_op(f):
            def call():
                f()
                self.close_popup()

            return call

        options = [(k, l, _wrap_op(f)) for k, l, f in options]
        dialog = QuestionDialog(title, message, options)
        self.open_popup(dialog)

    def show_input_dialog(self, title, on_confirm):
        def _wrap_op(f):
            def call(input_str):
                f(input_str)
                self.close_popup()

            return call

        dialog = InputDialog(title, _wrap_op(on_confirm), disallowed_chars=" /\\&%")
        self.open_popup(dialog)

    def _read_config(self):
        config_dir = os.path.join(os.environ["HOME"], ".vaultbrowser")
        if not os.path.isdir(config_dir):
            os.makedirs(config_dir)
        self._read_general_config(config_dir)
        self._read_services_config(config_dir)

    def _read_general_config(self, config_dir):
        config_file = os.path.join(config_dir, "vaultbrowser.ini")
        if not os.path.isfile(config_file):
            self._create_default_general_config(config_file)
        parser = configparser.ConfigParser()
        parser.read(config_file)
        self._editor = parser["DEFAULT"]["editor"]
        self._highlighter = parser["DEFAULT"].get("highlighter")
        logging.info(self._highlighter)

    def _read_services_config(self, config_dir):

        config_file = os.path.join(config_dir, "services.ini")

        if not os.path.isfile(config_file):
            self._create_default_services_file(config_file)

        parser = configparser.ConfigParser()
        parser.read(config_file)

        services = []

        for service_name in parser.sections():
            config = parser[service_name]
            service = Service(
                service_name,
                config["url"],
                config["token"],
                config.get("verify", "false").lower() == "true",
            )
            service.connect()
            services.append(service)

        self._services_model.services = services

    def _create_default_general_config(self, config_file):
        template = "[DEFAULT]\n" + "editor=/usr/bin/vi\n"
        # Put as default a well known json highlighter
        if os.path.isfile("/usr/bin/jq"):
            template += "highlighter=cat {file}|/usr/bin/jq -C\n"
        else:
            template += "#highlighter=/path/to/some/json/highlighter {file}"

        with open(config_file, "w") as f:
            f.write(template)

    def _create_default_services_file(self, config_file):
        vault_url = os.environ.get("VAULT_ADDR")
        vault_token = os.environ.get("VAULT_ADDR")
        vault_verify = "false"
        with open(config_file, "w") as f:
            if vault_url and vault_token:
                f.write(
                    f"[Local service]\nurl={vault_url}\ntoken={vault_token}\nverify={vault_verify}\n"
                )
            else:
                f.write(
                    f"[Service name here]\nurl=service url here\ntoken=Token goes here\nverify=false\n"
                )

    def _render_service(self, view, item):
        status = ansi.begin()
        if item.connected:
            status.fg(2).write("(C)").reset()
        elif item.connecting:
            status.fg(3).write("...").reset()
        elif item.error:
            status.fg(1).write("<X>").reset()
        status = str(status)
        
        return (
            item.name
            + (" "* (view.rect.width - (len(item.name)+3)))
            + status
        )

    def _render_backend(self, view, item):
        backend_type = f"({item.type_str})"
        return (
            item.name
            + (" " * (view.rect.width - (len(backend_type) + len(item.name))))
            + backend_type
        )

    def _on_service_selected(self, view, item):
        if not item.error:
            self._backends_model.client = item.client
            self._vault_model.client = item.client
            self._vault_model.backend = None
            self._textview.text = ""
            self.set_focused_view(self._backends_title)
        else:
            self._show_error(item.error)

    def _on_backend_selected(self, view, item):
        self._vault_model.backend = item
        self._textview.text = ""
        self.set_focused_view(self._tree_title)

    def _on_select(self, tree, item):
        try:
            if item == "..":
                tree.model.go_up()
                self._set_path_title(tree.model.get_current().path)
            elif item.leaf:
                self._show_selected_item(item)
            else:
                tree.model.go_to(item)
                self._set_path_title(item.path)
        except Exception as e:
            self._show_error(e) 
            logging.error(f"{e} - {traceback.format_exc()}")

    def _show_selected_item(self, item):
        value = item.value
        self._breadcrumb.title = item.path

        self._display_entry(value)


    def _set_path_title(self, path):
        if len(path) > 40:
            path = path[-40:]
        self._tree_title.title = path

    def _do_add(self, *_):
        self.show_input_dialog("Enter entry name", self._on_add_name_confirmed)

    def _display_entry(self, value):
        if self._highlighter:
            tf = misc.make_tempfile(json.dumps(value,indent=4),'json')
            try:
                result = subprocess.check_output(
                    self._highlighter.format(file=tf.name), shell=True
                )
                self._textview.text = result.decode()
            except Exception as e:
                logging.error(e)
                self._textview.text = json.dumps(value, indent=4)
            finally:
                self._drop_file(tf)
        else:
            text = json.dumps(value,indent=4)
            logging.info(text)
            self._textview.text = json.dumps(value, indent=4)


    def _on_add_name_confirmed(self, entry_name):
        selected = self._tree.model.get_current()
        tf = misc.make_tempfile(json.dumps({'data':''}),'.json')
        result = subprocess.run([self._editor, tf.name])
        if result.returncode == 0:
            tf.seek(0)
            try:
                data = json.load(tf)
                if data:
                    selected.add_child(entry_name, data)
            except ValueError as e:
                self._show_error(e)
            except Exception as e:
                logging.error(f"{e} - {traceback.format_exc()}")
                self._show_error(e) 
                self._textview.text = ""
        self._drop_file(tf)
        self.refresh()

    def _do_edit(self, *_):
        selected = self._tree.current_item
        value = selected.data
        tf = misc.make_tempfile(json.dumps(value,indent=4),'.json')
        result = subprocess.run([self._editor, tf.name])
        if result.returncode == 0:
            tf.seek(0)
            try:
                edited_stuff = json.load(tf)
                selected.value = edited_stuff
                self._display_entry(selected.value)
            except ValueError as e:
                self._show_error(e)
            except Exception as e:
                logging.error(f'Error writing value {e} - {traceback.format_exc()}')
        self._drop_file(tf)
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
            [("y", "Yes", confirm), ("n", "No", cancel)],
        )

    def _do_delete_recursively(self, *_):
        parent = self._tree.model.get_current()
        item = self._tree.current_item
        def confirm():
            item.remove()
            self._tree.model.remove_child(item, False)

        def cancel():
            pass

        self.show_question_dialog(
            "Warning",
            "Sure you want to recursively delete this path? (y/n)",
            [("y", "Yes", confirm), ("n", "No", cancel)],
        )

    def _do_export(self, *_):
        pass

    def _show_error(self, error):
        error_str = misc.word_wrap_text(str(error), 70)
        error_str =f"An error has occurred:\n\n{error_str}"
        self._show_text_popup(error_str)

    def _show_help(self, *_):
        self._show_text_popup(texts.HELP)

    def _drop_file(self, fp):
        try:
            fp.close()
            os.remove(fp.name)
        except Exception as e:
            logging.warn(f'Unable to remove tempfile {e}')


    def _show_text_popup(self, text):    
        max_height, max_width = ansi.terminal_size()    
    
        popup_width = int(max_width * 0.75)    
        popup_height = int(max_height * 0.75)    
    
        rect = Rect(    
            int((max_width - popup_width) / 2),    
            int((max_height - popup_height) / 2),    
            popup_width,    
            popup_height,    
        )    
        text_view = TextView(rect=rect, text=text)    
        self.open_popup(text_view) 

def main():
    explorer = VaultBrowser()
    explorer.main_loop()


if __name__ == "__main__":
    main()
