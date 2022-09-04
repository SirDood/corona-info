from typing import Callable
from gi.repository import Gio, Gtk


def create_action(self: Gtk.Application | Gtk.ApplicationWindow, name: str, callback: Callable, shortcuts: list = None):
    action = Gio.SimpleAction.new(name, None)
    action.connect("activate", callback)
    self.add_action(action)

    if shortcuts:
        app = self
        origin = "app"
        if isinstance(app, Gtk.ApplicationWindow):
            app = self.get_application()
            origin = "win"

        app.set_accels_for_action(f"{origin}.{name}", shortcuts)
