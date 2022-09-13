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

import logging
import sys

import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Gio

from coronainfo import _logger  # Unused but is necessary to initialise the logger
from coronainfo.enums import App, Paths
from coronainfo.settings import AppSettings
from coronainfo.views import MainWindow, AboutDialog
from coronainfo.utils.ui_helpers import create_action, log_action_call
from coronainfo.utils.files import get_json


class CoronaInfoApp(Gtk.Application):
    _schema = Gio.Settings(schema_id=App.ID)
    _settings = AppSettings(**get_json(Paths.SETTINGS_JSON)) if Paths.SETTINGS_JSON.exists() else AppSettings.placeholder()

    def __init__(self):
        super().__init__(application_id=App.ID,
                         flags=Gio.ApplicationFlags.FLAGS_NONE)

        create_action(self, "about", self.on_about_action)
        create_action(self, "quit", self.on_quit_action, ["<Ctrl>q"])

        self.connect("activate", self.on_activate)
        self.connect("shutdown", self.on_shutdown)

    @classmethod
    def get_schema(cls) -> Gio.Settings:
        return cls._schema

    @classmethod
    def get_settings(cls) -> Gio.Settings:
        return cls._settings

    def on_activate(self, app):
        logging.info("Preparing window")
        win = self.props.active_window
        if not win:
            win = MainWindow(application=self)
            self.set_accels_for_action("win.show-help-overlay", ["<Ctrl>question"])
        win.present()
        logging.info("Window launched")

    def on_shutdown(self, app):
        logging.info("Shutting down")
        self._settings.commit()

    def on_about_action(self, action: Gio.SimpleAction, param):
        log_action_call(action)
        about = AboutDialog(self.props.active_window)
        about.present()

    def on_quit_action(self, action: Gio.SimpleAction, param):
        log_action_call(action)
        self.quit()


def get_schema() -> Gio.Settings:
    return CoronaInfoApp.get_schema()


def get_settings() -> AppSettings:
    return CoronaInfoApp.get_settings()


def main(version):
    app = CoronaInfoApp()
    logging.info("Launching application")
    return app.run(sys.argv)
