# main.py
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

import sys

import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Gio

from coronainfo.enums import App
from coronainfo.views import MainWindow, AboutDialog
from coronainfo.utils.ui_helpers import create_action


class CoronaInfoApp(Gtk.Application):
    _settings = Gio.Settings(schema_id=App.ID)

    def __init__(self):
        super().__init__(application_id=App.ID,
                         flags=Gio.ApplicationFlags.FLAGS_NONE)

        create_action(self, "about", self.on_about_action)
        create_action(self, "quit", self.on_quit_action, ["<Ctrl>q"])

    @classmethod
    def get_schema(cls) -> Gio.Settings:
        return cls._settings

    def do_activate(self):
        win = self.props.active_window
        if not win:
            win = MainWindow(application=self)
            self.set_accels_for_action("win.show-help-overlay", ["<Ctrl>question"])
        win.present()

    def on_about_action(self, action: Gio.SimpleAction, param):
        about = AboutDialog(self.props.active_window)
        about.present()

    def on_quit_action(self, action: Gio.SimpleAction, param):
        self.quit()


def get_schema() -> Gio.Settings:
    return CoronaInfoApp.get_schema()


def main(version):
    app = CoronaInfoApp()
    return app.run(sys.argv)
