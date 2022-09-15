import logging
from datetime import datetime
from typing import Any, Callable, Union

from gi.repository import GLib, GObject, Gio, Gtk

from coronainfo.enums import App, Date
from coronainfo.settings import AppSettings


class TaskManager(GObject.Object):
    STARTED = "snowsuit-greeting"
    FINISHED = "mango-eggplant"
    ERROR = "xbox-rebate"

    def __init__(self, func: Callable, *args, **kwargs):
        super().__init__()
        if not GObject.signal_list_names(self):
            self._setup_signals()

        # TODO: Add cancel functionality

        self._func = func
        self._args = args
        self._kwargs = kwargs

        self._source = None
        self._cancellable = None

    def set_source(self, source: Any):
        self._source = source

    def set_cancellable(self, cancellable: Gio.Cancellable):
        self._cancellable = cancellable

    def start(self):
        task: Gio.Task = Gio.Task.new(self._source, self._cancellable, self._ready_wrapper, None)
        task.run_in_thread(self._func_wrapper)

    def _func_wrapper(self, task: Gio.Task, source, data, cancellable: Gio.Cancellable):
        func_name = self._func.__name__
        logging.debug(f"Worker running function: {func_name}{self._args}{self._kwargs}")

        try:
            self.emit(self.STARTED)
            result = self._func(*self._args, **self._kwargs)
            task.return_value(result)
        except Exception as err:
            logging.error(f"An error has occurred while running '{func_name}' in thread:", exc_info=True)
            task.return_value(err)

    def _ready_wrapper(self, source, task: Gio.Task, error):
        result = task.propagate_value()[1]

        if isinstance(result, BaseException) or isinstance(result, GLib.Error):
            self.emit(self.ERROR, result)
            return

        self.emit(self.FINISHED, result)

    def _setup_signals(self):
        GObject.signal_new(
            self.STARTED,
            self,
            GObject.SignalFlags.RUN_LAST,
            GObject.TYPE_BOOLEAN,
            []
        )

        GObject.signal_new(
            self.FINISHED,
            self,
            GObject.SignalFlags.RUN_LAST,
            GObject.TYPE_BOOLEAN,
            [object]
        )

        GObject.signal_new(
            self.ERROR,
            self,
            GObject.SignalFlags.RUN_LAST,
            GObject.TYPE_BOOLEAN,
            [object]  # Exception
        )


def run_in_thread(func: Callable, on_finish: Callable = None,
                  func_args: tuple = (), on_finish_args: tuple = (),
                  cancellable: Gio.Cancellable = Gio.Cancellable()) -> TaskManager:
    def on_finish_wrapper(task: TaskManager, result):
        on_finish_name = on_finish.__name__
        logging.debug(f"Worker running on_finish: {on_finish_name}{on_finish_args}")

        try:
            on_finish(*on_finish_args)
        except Exception as err:
            logging.error(f"An error has occurred while running '{on_finish_name}' in thread:", exc_info=True)

    task = TaskManager(func, *func_args)
    task.set_cancellable(cancellable)
    if on_finish:
        task.connect(task.FINISHED, on_finish_wrapper)
    task.start()

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


def evaluate_title(settings: AppSettings) -> str:
    last_fetched = settings.last_fetched

    display = f"{App.NAME} {App.VERSION}"
    if last_fetched:
        display_date = datetime.fromisoformat(last_fetched).strftime(Date.DISPLAY_FORMAT)
        display = f"Last fetched: {display_date}"

    return display


def log_action_call(action: Gio.SimpleAction):
    logging.debug(f"Action `{action.get_name()}` called")


def reset_gschema(settings: Gio.Settings):
    for key in settings.keys():
        settings.reset(key)
