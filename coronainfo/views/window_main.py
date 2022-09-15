# window.py
#
# Copyright 2022 Izzat Z.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import logging
import os

from gi.repository import Adw, GObject, Gio, Gtk

from coronainfo import app
from coronainfo.controllers import AppController
from coronainfo.utils.ui_helpers import create_action, evaluate_title, log_action_call
from coronainfo.views.dialog_preferences import PreferencesDialog


@Gtk.Template(resource_path="/com.izzthedude.CoronaInfo/ui/main-window")
class MainWindow(Adw.ApplicationWindow):
    __gtype_name__ = "MainWindow"

    refresh_btn: Gtk.Button = Gtk.Template.Child(name="refresh_btn")
    search_btn: Gtk.ToggleButton = Gtk.Template.Child(name="search_btn")

    toast_overlay: Adw.ToastOverlay = Gtk.Template.Child(name="toast_overlay")
    content_box: Gtk.Box = Gtk.Template.Child(name="content_box")

    spinner_box: Gtk.Box = Gtk.Template.Child(name="spinner_box")
    spinner: Gtk.Spinner = Gtk.Template.Child(name="spinner")

    table_box: Gtk.Box = Gtk.Template.Child(name="table_box")
    searchbar: Gtk.SearchBar = Gtk.Template.Child(name="searchbar")
    search_entry: Gtk.SearchEntry = Gtk.Template.Child(name="search_entry")
    statuspage: Adw.StatusPage = Gtk.Template.Child(name="statuspage")
    table: Gtk.TreeView = Gtk.Template.Child(name="table_view")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._init_settings()
        self._setup_help_overlay()
        self._bind_properties()

        create_action(self, "refresh-data", self.on_refresh_action, ["<Ctrl>r"])
        create_action(self, "save-data", self.on_save_action, ["<Ctrl>s"])
        create_action(self, "preferences", self.on_preferences_action, ["<Ctrl>comma"])
        create_action(self, "toggle-search", self.on_toggle_search_action)

        if os.environ.get("CORONAINFO_DEBUG"):
            create_action(self, "debug", self._on_debug_action, ["<Ctrl>d"])
            logging.debug("Debug action created.")

        title = evaluate_title(app.get_settings())
        self.set_title(title)

        self.searchbar.connect_entry(self.search_entry)
        self.searchbar.set_key_capture_widget(self)

        self.controller = AppController.get_main_controller()
        self.controller.connect(self.controller.POPULATE_STARTED, self.on_populate_started)
        self.controller.connect(self.controller.POPULATE_FINISHED, self.on_populate_finished)
        self.controller.connect(self.controller.PROGRESS_MESSAGE, self.on_progress_emitted)
        self.controller.connect(self.controller.MODEL_EMPTY, self.on_model_empty)
        self.controller.connect(self.controller.TOAST_MESSAGE, self.on_error_message)
        self.controller.set_table(self.table)
        self.controller.start_populate()

    def on_populate_started(self, controller):
        self.refresh_btn.set_sensitive(False)
        self.spinner_box.set_visible(True)
        self.spinner.start()

    def on_populate_finished(self, controller):
        self.spinner.stop()
        self.spinner_box.set_visible(False)
        self.refresh_btn.set_sensitive(True)

    def on_progress_emitted(self, controller, message: str):
        self.set_title(message)

    def on_error_message(self, controller, message: str, timeout: int = 0):
        toast = Adw.Toast(title=message, timeout=timeout)
        self.toast_overlay.add_toast(toast)

    def on_refresh_action(self, action: Gio.SimpleAction, param):
        log_action_call(action)
        self.controller.on_refresh()

    def on_save_action(self, action: Gio.SimpleAction, param):
        log_action_call(action)
        self.controller.on_save(self)

    def on_toggle_search_action(self, action: Gio.SimpleAction, param):
        log_action_call(action)
        search_mode = self.searchbar.get_search_mode()
        self.searchbar.set_search_mode(not search_mode)

    def on_preferences_action(self, action: Gio.SimpleAction, param):
        log_action_call(action)
        settings = PreferencesDialog(self)
        settings.set_columns(self.table.get_columns())
        settings.show()

    @Gtk.Template.Callback()
    def on_search(self, entry: Gtk.SearchEntry):
        self.table.set_visible(True)
        self.controller.set_filter(entry.get_text())

    def on_model_empty(self, controller):
        search = self.search_entry.get_text()
        self.statuspage.set_title(f"`{search}` Not Found")
        self.statuspage.set_visible(True)

    def _on_debug_action(self, action: Gio.SimpleAction, param):
        logging.debug(f"Debug action activated")

    def _init_settings(self):
        settings = app.get_schema()

        settings.bind(
            "window-width",
            self,
            "default-width",
            Gio.SettingsBindFlags.DEFAULT
        )

        settings.bind(
            "window-height",
            self,
            "default-height",
            Gio.SettingsBindFlags.DEFAULT
        )

        settings.bind(
            "window-maximized",
            self,
            "maximized",
            Gio.SettingsBindFlags.DEFAULT
        )

    def _setup_help_overlay(self):
        builder: Gtk.Builder = Gtk.Builder.new_from_resource("/com.izzthedude.CoronaInfo/ui/help-overlay")
        shortcuts_window: Gtk.ShortcutsWindow = builder.get_object("help_overlay")
        self.set_help_overlay(shortcuts_window)

    def _bind_properties(self):
        self.search_btn.bind_property(
            "active",
            self.searchbar,
            "search-mode-enabled",
            GObject.BindingFlags.BIDIRECTIONAL | GObject.BindingFlags.SYNC_CREATE
        )

        self.statuspage.bind_property(
            "visible",
            self.table,
            "visible",
            GObject.BindingFlags.BIDIRECTIONAL | GObject.BindingFlags.SYNC_CREATE | GObject.BindingFlags.INVERT_BOOLEAN
        )

        self.spinner_box.bind_property(
            "visible",
            self.table_box,
            "visible",
            GObject.BindingFlags.BIDIRECTIONAL | GObject.BindingFlags.SYNC_CREATE | GObject.BindingFlags.INVERT_BOOLEAN
        )
