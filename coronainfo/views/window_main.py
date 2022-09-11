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

from gi.repository import GObject, Gio, Gtk

from coronainfo.controllers import AppController
from coronainfo.enums import App
from coronainfo.models.model_corona import CoronaHeaders
from coronainfo.utils.ui_helpers import create_action
from coronainfo.views.dialog_preferences import PreferencesDialog


@Gtk.Template(resource_path="/coronainfo/ui/main-window")
class MainWindow(Gtk.ApplicationWindow):
    __gtype_name__ = "MainWindow"
    TITLE = f"{App.NAME} {App.VERSION}"

    refresh_btn: Gtk.Button = Gtk.Template.Child(name="refresh_btn")
    spinner: Gtk.Spinner = Gtk.Template.Child(name="spinner")
    search_btn: Gtk.ToggleButton = Gtk.Template.Child(name="search_btn")
    searchbar: Gtk.SearchBar = Gtk.Template.Child(name="searchbar")
    search_entry: Gtk.SearchEntry = Gtk.Template.Child(name="search_entry")
    content_box: Gtk.Box = Gtk.Template.Child(name="content_box")
    table: Gtk.TreeView = Gtk.Template.Child(name="table_view")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._init_settings()
        self.set_title(self.TITLE)

        # Set the shortcuts window aka help overlay
        builder: Gtk.Builder = Gtk.Builder.new_from_resource("/coronainfo/ui/help-overlay")
        shortcuts_window: Gtk.ShortcutsWindow = builder.get_object("help_overlay")
        self.set_help_overlay(shortcuts_window)

        create_action(self, "refresh-data", self.on_refresh_action, ["<Ctrl>r"])
        create_action(self, "save-data", self.on_save_action, ["<Ctrl>s"])
        create_action(self, "preferences", self.on_preferences_action, ["<Ctrl>comma"])
        create_action(self, "toggle-search", self.on_toggle_search_action)

        self.searchbar.connect_entry(self.search_entry)
        self.searchbar.set_key_capture_widget(self)
        self.searchbar.bind_property(
            "search-mode-enabled",
            self.search_btn,
            "active",
            GObject.BindingFlags.BIDIRECTIONAL | GObject.BindingFlags.SYNC_CREATE
        )

        self.controller = AppController.get_main_controller()
        self.controller.set_table(self.table)
        self.setup_table()

        self.controller.connect(self.controller.POPULATE_STARTED, self.on_populate_started)
        self.controller.connect(self.controller.POPULATE_FINISHED, self.on_populate_finished)
        self.controller.connect(self.controller.PROGRESS_MESSAGE, self.on_progress_emitted)
        self.controller.start_populate()

    def setup_table(self):
        # Hide some columns initially
        columns: list[Gtk.TreeViewColumn] = self.table.get_columns()
        columns[int(CoronaHeaders.TOTAL_RECOVERED)].set_visible(False)
        columns[int(CoronaHeaders.SERIOUS_CASES)].set_visible(False)
        columns[int(CoronaHeaders.TOTAL_CASES_PER_1M)].set_visible(False)
        columns[int(CoronaHeaders.DEATHS_PER_1M)].set_visible(False)
        columns[int(CoronaHeaders.TOTAL_TESTS)].set_visible(False)
        columns[int(CoronaHeaders.TESTS_PER_1M)].set_visible(False)
        columns[int(CoronaHeaders.POPULATION)].set_visible(False)

    def on_populate_started(self, controller):
        self.refresh_btn.set_sensitive(False)
        self.searchbar.set_visible(False)
        self.table.set_visible(False)
        self.content_box.set_valign(Gtk.Align.CENTER)
        self.spinner.set_visible(True)
        self.spinner.start()

    def on_populate_finished(self, controller):
        self.spinner.stop()
        self.spinner.set_visible(False)
        self.content_box.set_valign(Gtk.Align.FILL)
        self.table.set_visible(True)
        self.searchbar.set_visible(True)
        self.refresh_btn.set_sensitive(True)
        self.set_title(self.TITLE)

    def on_progress_emitted(self, controller, message: str):
        self.set_title(message)

    def on_refresh_action(self, action: Gio.SimpleAction, param):
        self.controller.on_refresh()

    def on_save_action(self, action: Gio.SimpleAction, param):
        print("SAVE DATA")

    def on_toggle_search_action(self, action: Gio.SimpleAction, param):
        search_mode = self.searchbar.get_search_mode()
        self.searchbar.set_search_mode(not search_mode)

    def on_preferences_action(self, action: Gio.SimpleAction, param):
        settings = PreferencesDialog(self)
        settings.set_columns(self.table.get_columns())
        settings.show()

    @Gtk.Template.Callback()
    def on_search(self, entry: Gtk.SearchEntry):
        self.controller.set_filter(entry.get_text())

    def _init_settings(self):
        settings = Gio.Settings(schema_id=App.ID)

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
