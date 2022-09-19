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

import os

from gi.repository import Adw, GObject, Gio, Gtk

from coronainfo import app
from coronainfo.controllers import AppController
from coronainfo.ui.dialog_preferences import PreferencesDialog
from coronainfo.ui.view_content_main import MainContentView
from coronainfo.utils.ui_helpers import create_action, evaluate_title, log_action_call


@Gtk.Template(resource_path="/com.izzthedude.CoronaInfo/ui/main-window")
class MainWindow(Adw.ApplicationWindow):
    __gtype_name__ = "MainWindow"

    refresh_btn: Gtk.Button = Gtk.Template.Child(name="refresh_btn")
    search_btn: Gtk.ToggleButton = Gtk.Template.Child(name="search_btn")

    toast_overlay: Adw.ToastOverlay = Gtk.Template.Child(name="toast_overlay")
    content_box: Gtk.Box = Gtk.Template.Child(name="content_box")

    builder: Gtk.Builder = Gtk.Builder.new_from_resource("/com.izzthedude.CoronaInfo/ui/spinner-view")
    spinner_box: Gtk.Box = builder.get_object("spinner_box")
    spinner: Gtk.Spinner = builder.get_object("spinner")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._init_settings()
        self._setup_help_overlay()

        title = evaluate_title(app.get_settings())
        self.set_title(title)

        self.main_content = MainContentView(self)
        self.content_box.append(self.main_content)
        self.content_box.append(self.spinner_box)

        self._bind_properties()

        self.controller = AppController.get_main_controller()
        self.controller.connect(self.controller.POPULATE_STARTED, self.on_populate_started)
        self.controller.connect(self.controller.POPULATE_FINISHED, self.on_populate_finished)
        self.controller.connect(self.controller.PROGRESS_MESSAGE, self.on_progress_emitted)
        self.controller.connect(self.controller.TOAST_MESSAGE, self.on_toast_message)
        self.controller.connect(self.controller.ERROR_OCCURRED, self.on_error_message)

        create_action(self, "refresh-data", self.on_refresh_action, ["<Ctrl>r"])
        create_action(self, "save-data", self.on_save_action, ["<Ctrl>s"])
        create_action(self, "preferences", self.on_preferences_action, ["<Ctrl>comma"])
        create_action(self, "toggle-search", self.main_content.on_toggle_search_action)

        if os.environ.get("CORONAINFO_DEBUG"):
            create_action(self, "debug", self._on_debug_action, ["<Ctrl>d"])

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

    def on_toast_message(self, controller, message: str, timeout: int = 0):
        toast = Adw.Toast(title=message, timeout=timeout)
        self.toast_overlay.add_toast(toast)

    def on_error_message(self, controller, message: str):
        self.spinner_box.set_visible(False)

    def on_refresh_action(self, action: Gio.SimpleAction, param):
        log_action_call(action)
        self.controller.on_refresh()

    def on_save_action(self, action: Gio.SimpleAction, param):
        log_action_call(action)

        self._dialog = Gtk.FileChooserNative(
            title="Save File as",
            transient_for=self,
            action=Gtk.FileChooserAction.SAVE,
            accept_label="_Save",
            cancel_label="_Cancel"
        )
        self.controller.on_save(self._dialog)

    def on_preferences_action(self, action: Gio.SimpleAction, param):
        preferences = PreferencesDialog(self)
        preferences.set_columns(self.main_content.table.get_columns())
        preferences.show()

    def _on_debug_action(self, action: Gio.SimpleAction, param):
        log_action_call(action)

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
            self.main_content.searchbar,
            "search-mode-enabled",
            GObject.BindingFlags.BIDIRECTIONAL | GObject.BindingFlags.SYNC_CREATE
        )

        self.spinner_box.bind_property(
            "visible",
            self.main_content,
            "visible",
            GObject.BindingFlags.BIDIRECTIONAL | GObject.BindingFlags.SYNC_CREATE | GObject.BindingFlags.INVERT_BOOLEAN
        )
