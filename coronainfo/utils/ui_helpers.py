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

        self._on_finish = None
        self._on_finish_args = None
        self._on_finish_kwargs = None

        self._on_error = None
        self._on_error_args = None
        self._on_error_kwargs = None

        self._source = None
        self._cancellable = None

    def start(self):
        task: Gio.Task = Gio.Task.new(self._source, self._cancellable, self._ready_wrapper, None)
        if self._on_finish: self.connect(self.FINISHED, self._on_finish_wrapper)
        if self._on_error: self.connect(self.ERROR, self._on_finish_wrapper)
        task.run_in_thread(self._func_wrapper)

    def set_on_finish(self, func: Callable, *args, **kwargs):
        self._on_finish = func
        self._on_finish_args = args
        self._on_finish_kwargs = kwargs

    def set_on_error(self, func: Callable, *args, **kwargs):
        self._on_error = func
        self._on_error_args = args
        self._on_error_kwargs = kwargs

    def set_source(self, source: Any):
        self._source = source

    def set_cancellable(self, cancellable: Gio.Cancellable):
        self._cancellable = cancellable

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

    def _on_finish_wrapper(self, taskmanager, result):
        # Determine if self._on_finish or self._on_error should run
        is_error = isinstance(result, Exception)
        func = self._on_finish if not is_error else self._on_error
        func_args = self._on_finish_args if not is_error else self._on_error_args
        func_kwargs = self._on_finish_kwargs if not is_error else self._on_error_kwargs
        func_name = func.__name__

        logging.debug(f"Worker running on finished function: {func_name}{func_args}{func_kwargs}")
        try:
            if result is None:
                func(*func_args, **func_kwargs)
            else:
                func(*func_args, result, **func_kwargs)

        except Exception as err:
            logging.error(f"An error has occurred while running '{func_name}':", exc_info=True)

    def _setup_signals(self):
        create_signal(self, self.STARTED)
        create_signal(self, self.FINISHED, [object])
        create_signal(self, self.ERROR, [object])  # param_type is Exception


def create_action(self: Union[Gtk.Application, Gtk.ApplicationWindow], name: str, callback: Callable,
                  shortcuts: list = None):
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


def create_signal(source: GObject.Object, name: str, param_types: list = []):
    GObject.signal_new(
        name,  # Signal message
        source,  # A Python GObject instance or type that the signal is associated with
        GObject.SignalFlags.RUN_LAST,  # Signal flags
        GObject.TYPE_BOOLEAN,  # Return type of the signal handler
        param_types  # Parameter types
    )


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
