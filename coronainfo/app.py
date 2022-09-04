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
from gi.repository import Gtk, Gio

from coronainfo.views import MainWindow, AboutDialog


class CoronaInfoApp(Gtk.Application):
    def __init__(self):
        super().__init__(application_id="com.izzthedude.CoronaInfo",
                         flags=Gio.ApplicationFlags.FLAGS_NONE)

        self.create_action("preferences", self.on_preferences_action, ["<Ctrl>period"])
        self.create_action("about", self.on_about_action)
        self.create_action("quit", self.on_quit_action, ["<Ctrl>q"])

    def do_activate(self):
        win = self.props.active_window
        if not win:
            win = MainWindow(application=self)
            self.set_accels_for_action("win.show-help-overlay", ["<Ctrl>question"])
        win.present()

    def on_preferences_action(self, action: Gio.SimpleAction, param):
        print("PREFERENCES")

    def on_about_action(self, action: Gio.SimpleAction, param):
        about = AboutDialog(self.props.active_window)
        about.present()

    def on_quit_action(self, action: Gio.SimpleAction, param):
        self.quit()

    def create_action(self, name: str, callback, shortcuts: list = None):
        action = Gio.SimpleAction.new(name, None)
        action.connect("activate", callback)
        self.add_action(action)
        if shortcuts:
            self.set_accels_for_action(f"app.{name}", shortcuts)


def main(version):
    app = CoronaInfoApp()
    return app.run(sys.argv)
