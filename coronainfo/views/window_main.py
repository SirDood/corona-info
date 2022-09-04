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

from gi.repository import Gtk, Gio

from coronainfo.utils.ui_helpers import create_action


@Gtk.Template(resource_path="/coronainfo/ui/main-window")
class MainWindow(Gtk.ApplicationWindow):
    __gtype_name__ = "MainWindow"

    refresh_btn: Gtk.Button = Gtk.Template.Child(name="refresh_btn")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Set the shortcuts window aka help overlay
        builder: Gtk.Builder = Gtk.Builder.new_from_resource("/coronainfo/ui/help-overlay")
        shortcuts_window: Gtk.ShortcutsWindow = builder.get_object("help_overlay")
        self.set_help_overlay(shortcuts_window)

        create_action(self, "refresh-data", self.on_refresh_action, ["<Ctrl>r"])
        create_action(self, "save-data", self.on_save_action)

    def on_refresh_action(self, action: Gio.SimpleAction, param):
        print("REFRESH")

    def on_save_action(self, action: Gio.SimpleAction, param):
        print("SAVE DATA")
