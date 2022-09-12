from datetime import datetime
from typing import Callable, Union

from gi.repository import GObject, Gio, Gtk

from coronainfo.enums import App, Date
from coronainfo.settings import Settings


def run_in_thread(func: Callable, on_finish: Callable = None,
                  func_args: tuple = (), on_finish_args: tuple = (),
                  cancellable: Gio.Cancellable = Gio.Cancellable()) -> Gio.Task:
    # TODO: figure out better ways to do this lmao
    def func_wrapper(task: Gio.Task, arg2, arg3, cancellable: Gio.Cancellable = None):
        func_name = func.__name__
        print(f"[WORKER] Running function: {func_name}{func_args}")

        try:
            func(*func_args)
        except Exception as err:
            print(f"An error has occurred while running '{func_name}' in thread:", err)

    def on_finish_wrapper(task: Gio.Task, status: GObject.ParamSpecBoolean):
        on_finish_name = on_finish.__name__
        print(f"[WORKER] Running on_finish: {on_finish_name}{on_finish_args}")

        try:
            on_finish(*on_finish_args)
        except Exception as err:
            print(f"An error has occurred while running '{on_finish_name}' in thread:", err)

    task: Gio.Task = Gio.Task.new(None, cancellable, None, None)
    task.set_return_on_cancel(False)
    if on_finish:
        task.connect("notify::completed", on_finish_wrapper)
    task.run_in_thread(func_wrapper)

    return task


def create_action(self: Union[Gtk.Application, Gtk.ApplicationWindow], name: str, callback: Callable, shortcuts: list = None):
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


def evaluate_title(settings: Settings) -> str:
    last_fetched = settings.last_fetched

    display = f"{App.NAME} {App.VERSION}"
    if last_fetched:
        display_date = datetime.fromisoformat(last_fetched).strftime(Date.DISPLAY_FORMAT)
        display = f"Last fetched: {display_date}"

    return display


def reset_gschema(settings: Gio.Settings):
    for key in settings.keys():
        settings.reset(key)
