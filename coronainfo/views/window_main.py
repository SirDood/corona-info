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
from coronainfo.models.model_corona import CoronaHeaders
from coronainfo.utils.ui_helpers import create_action


@Gtk.Template(resource_path="/coronainfo/ui/main-window")
class MainWindow(Gtk.ApplicationWindow):
    __gtype_name__ = "MainWindow"

    search_btn: Gtk.ToggleButton = Gtk.Template.Child(name="search_btn")
    searchbar: Gtk.SearchBar = Gtk.Template.Child(name="searchbar")
    search_entry: Gtk.SearchEntry = Gtk.Template.Child(name="search_entry")
    table: Gtk.TreeView = Gtk.Template.Child(name="table_view")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Set the shortcuts window aka help overlay
        builder: Gtk.Builder = Gtk.Builder.new_from_resource("/coronainfo/ui/help-overlay")
        shortcuts_window: Gtk.ShortcutsWindow = builder.get_object("help_overlay")
        self.set_help_overlay(shortcuts_window)

        create_action(self, "refresh-data", self.on_refresh_action, ["<Ctrl>r"])
        create_action(self, "save-data", self.on_save_action, ["<Ctrl>s"])
        create_action(self, "settings", self.on_settings_action, ["<Ctrl>comma"])
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
        self.setup_table()

    def setup_table(self):
        self.controller.set_table(self.table)

        # Hide some columns initially
        columns: list[Gtk.TreeViewColumn] = self.table.get_columns()
        columns[int(CoronaHeaders.TOTAL_RECOVERED)].set_visible(False)
        columns[int(CoronaHeaders.SERIOUS_CASES)].set_visible(False)
        columns[int(CoronaHeaders.TOTAL_CASES_PER_1M)].set_visible(False)
        columns[int(CoronaHeaders.DEATHS_PER_1M)].set_visible(False)
        columns[int(CoronaHeaders.TOTAL_TESTS)].set_visible(False)
        columns[int(CoronaHeaders.TESTS_PER_1M)].set_visible(False)
        columns[int(CoronaHeaders.POPULATION)].set_visible(False)

    def on_refresh_action(self, action: Gio.SimpleAction, param):
        print("REFRESH")

    def on_save_action(self, action: Gio.SimpleAction, param):
        print("SAVE DATA")

    def on_toggle_search_action(self, action: Gio.SimpleAction, param):
        print("TOGGLE SEARCH")
        search_mode = self.searchbar.get_search_mode()
        self.searchbar.set_search_mode(not search_mode)

    @Gtk.Template.Callback()
    def on_search(self, entry: Gtk.SearchEntry):
        print("ENTRY:", entry.get_text())

    def on_toggle_columns_action(self, action: Gio.SimpleAction, param):
        print("TOGGLE COLUMNS")

    def on_settings_action(self, action: Gio.SimpleAction, param):
        print("SETTINGS")
