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

from gi.repository import Gtk


@Gtk.Template(resource_path="/ui/main-window")
class MainWindow(Gtk.ApplicationWindow):
    __gtype_name__ = "MainWindow"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        shortcuts_window = ShortcutsWindow()
        self.set_help_overlay(shortcuts_window)


@Gtk.Template(resource_path="/ui/help-overlay")
class ShortcutsWindow(Gtk.ShortcutsWindow):
    __gtype_name__ = "ShortcutsWindow"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

