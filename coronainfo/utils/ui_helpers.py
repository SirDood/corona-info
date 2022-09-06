from typing import Callable, Union

from gi.repository import GObject, Gio, Gtk


def run_in_thread(func: Callable, on_finish: Callable = None,
                  func_args: tuple = (), on_finish_args: tuple = (),
                  cancellable: Gio.Cancellable = Gio.Cancellable()) -> Gio.Task:
    # TODO: figure out better ways to do this lmao
    def func_wrapper(task: Gio.Task, arg2, arg3, cancellable: Gio.Cancellable = None):
        print(f"[WORKER] Running function: {func.__name__}{func_args}")
        func(*func_args)

    def on_finish_wrapper(task: Gio.Task, status: GObject.ParamSpecBoolean):
        print(f"[WORKER] Running on_finish: {on_finish.__name__}{on_finish_args}")
        on_finish(*on_finish_args)

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
