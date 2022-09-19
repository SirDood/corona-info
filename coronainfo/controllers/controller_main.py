import logging
from datetime import datetime

from gi.repository import GObject, Gio, Gtk
from requests import ConnectionError, HTTPError

from coronainfo import app
from coronainfo.enums import App, Date, Paths
from coronainfo.utils.files import get_json, write_json
from coronainfo.utils.ui_helpers import create_signal, evaluate_title, run_in_thread
from coronainfo.utils.worldometer import CoronaData, CoronaHeaders, fetch_data


class MainController(GObject.Object):
    POPULATE_STARTED = "velvet-massager"
    POPULATE_FINISHED = "cube-helpless"
    PROGRESS_MESSAGE = "absurd-frosted"
    MODEL_EMPTY = "vintage-next"
    TOAST_MESSAGE = "untwist-unicycle"
    ERROR_OCCURRED = "enforcer-pope"

    def __init__(self):
        super().__init__()
        self._setup_signals()

        self.table: Gtk.TreeView = None

        field_types = CoronaData.field_types()
        logging.debug(f"Model field types: {field_types}")
        self.model = Gtk.ListStore(*field_types)
        self.country_filter = ""
        self.set_filter(self.country_filter)

        self.is_populating = False

    def start_populate(self):
        run_in_thread(self._populate_data,
                      on_finish=self._on_populate_finished,
                      on_error=self._on_populate_error)

    def on_refresh(self):
        if not self.is_populating:
            self.model.clear()
            run_in_thread(self._populate_data, (False,),
                          on_finish=self._on_populate_finished,
                          on_error=self._on_populate_error)
        else:
            message = "Refresh in progress!"
            logging.warning(message)
            self._update_toast(message, 2)

    def on_save(self, dialog: Gtk.FileChooserNative):
        name = App.NAME.replace(' ', '')
        date = datetime.fromisoformat(app.get_settings().last_fetched).date()
        file_name = f"{name}_{date}.json"
        downloads_dir = Gio.File.new_for_path(str(Paths.DOWNLOADS_DIR))
        dialog.set_current_name(file_name)
        dialog.set_current_folder(downloads_dir)
        dialog.connect("response", self._on_save_response)
        dialog.show()

    def set_table(self, table: Gtk.TreeView):
        self.table = table

        # Set columns
        for i, header in enumerate(CoronaHeaders.as_tuple()):
            title = header.replace("_", " ").replace("PER", "/").title()
            renderer = Gtk.CellRendererText()
            renderer.set_property("height", 30)

            column = Gtk.TreeViewColumn(title, renderer, text=i)
            column.set_cell_data_func(renderer, self._cell_data_func, func_data=i)
            column.set_alignment(0.5)
            column.set_sort_column_id(i)
            column.set_expand(True)
            self._bind_column_settings(column)

            self.table.append_column(column)

    def set_filter(self, text: str):
        if self.table:
            self.country_filter = text
            model_filter: Gtk.TreeModelFilter = self.model.filter_new()
            model_filter.set_visible_func(self._visible_func)
            model_proxy: Gtk.TreeModelSort = Gtk.TreeModelSort.new_with_model(model_filter)
            self.table.set_model(model_proxy)

            if len(model_proxy) == 0:
                self.emit(self.MODEL_EMPTY)

    def _populate_data(self, use_cache: bool = True):
        self.emit(self.POPULATE_STARTED)
        self.is_populating = True
        logging.info("Data population started")

        self.table.set_model(None)
        for row in self._get_data(use_cache=use_cache):
            self.model.append(row)
        self.set_filter(self.country_filter)

    def _get_data(self, use_cache: bool = True):
        cache_file = Paths.CACHE_JSON

        if not cache_file.exists() or not use_cache:
            message = "Fetching data..."
            self._update_progress(message)
            logging.info(message)
            dataset = fetch_data()
            logging.debug(f"Caching data at {cache_file}")
            write_json(cache_file, dataset)

            # Update last_fetched settings
            today = datetime.now().strftime(Date.RAW_FORMAT)
            logging.debug(f"Updating last_fetched: {today}")
            settings = app.get_settings()
            settings.last_fetched = today

        message = "Reading data..."
        self._update_progress(message)
        logging.info(message)
        json_data = get_json(cache_file)
        result = map(lambda row: CoronaData(**row), json_data)
        return result

    def _on_populate_finished(self):
        self.is_populating = False
        self.emit(self.POPULATE_FINISHED)
        logging.info("Data population finished")

        # Update title
        title = evaluate_title(app.get_settings())
        self._update_progress(title)

    def _on_populate_error(self, error: Exception):
        self.is_populating = False
        message = str(error)

        if isinstance(error, ConnectionError):
            self._update_toast("A ConnectionError has occurred. Check your Internet connection or if the "
                               "Worldometer website is up.",
                               5)
            self.start_populate()

        elif isinstance(error, HTTPError):
            self._update_toast(message, 5)
            self.start_populate()

        else:
            self._update_progress(evaluate_title(app.get_settings()))
            self.emit(self.ERROR_OCCURRED, message)

    def _on_save_response(self, dialog: Gtk.FileChooserNative, response: int):
        logging.debug(f"Response type: {Gtk.ResponseType(response).value_name}")
        if response == Gtk.ResponseType.ACCEPT:
            dest_path = dialog.get_file().get_path()
            run_in_thread(self._save_file, (dest_path,),
                          on_finish=self._on_save_finished, on_finish_args=(dest_path,))

        dialog.destroy()

    def _save_file(self, destination: str):
        logging.info(f"Saving data to {destination}")
        try:
            cache = get_json(Paths.CACHE_JSON)
            write_json(destination, cache)
        except Exception as err:
            logging.error("An error has occurred while trying to read from cache while saving:", exc_info=True)
            self._update_toast(
                f"An error has occurred while attempting to save data. Refer the logs at {Paths.LOGS_DIR}",
                0)

    def _on_save_finished(self, destination: str):
        message = f"Successfully saved data to {destination}"
        logging.info(message)
        self._update_toast(message, 5)

    def _cell_data_func(self, column: Gtk.TreeViewColumn,
                        renderer: Gtk.CellRendererText,
                        model: Gtk.TreeModelSort,
                        tree_iter: Gtk.TreeIter,
                        data):  # column number

        value = model.get(tree_iter, data)[0]
        if isinstance(value, int):
            display = ""
            if value:
                display = f"{value:,}"
                if "NEW" in CoronaHeaders.as_tuple()[data] and value > 0:
                    prefix = ""
                    if value >= 0:
                        prefix = "+"
                    display = prefix + display

            renderer.set_property("text", display)

        orange = "rgb(255, 145, 0)"
        red = "rgb(220, 0, 0)"
        green = "rgb(0, 160, 0)"
        blue = "rgb(82, 119, 145)"
        if data == int(CoronaHeaders.NEW_CASES):
            colour = orange
            if value < 0:
                colour = blue
            renderer.set_property("foreground", colour)

        if data == int(CoronaHeaders.NEW_DEATHS):
            colour = red
            if value < 0:
                colour = blue
            renderer.set_property("foreground", colour)

        if data == int(CoronaHeaders.NEW_RECOVERED):
            colour = green
            if value < 0:
                colour = red
            renderer.set_property("foreground", colour)

    def _visible_func(self, model: Gtk.ListStore, tree_iter: Gtk.TreeIter, data):
        if not self.country_filter:
            return True

        country = model[tree_iter][int(CoronaHeaders.COUNTRY)]
        return self.country_filter.lower() in country.lower()

    def _update_progress(self, message: str):
        # TODO: look into fixing the 'Trying to snapshot XXX without a current allocation' error
        self.emit(self.PROGRESS_MESSAGE, message)

    def _update_toast(self, message: str, timeout: int):
        self.emit(self.TOAST_MESSAGE, message, timeout)

    def _setup_signals(self):
        create_signal(self, self.POPULATE_STARTED)
        create_signal(self, self.POPULATE_FINISHED)
        create_signal(self, self.PROGRESS_MESSAGE, [str])
        create_signal(self, self.MODEL_EMPTY)
        create_signal(self, self.TOAST_MESSAGE, [str, int])
        create_signal(self, self.ERROR_OCCURRED, [str])

    def _bind_column_settings(self, column: Gtk.TreeViewColumn):
        title = column.get_title()
        name = title.replace(" ", "-").replace("/", "per").lower()

        settings = app.get_schema()
        for key in settings.keys():
            # Convert column-bla-bla-visible to just bla-bla
            key_column_name = "-".join(key.split("-")[1:-1])
            if name == key_column_name:
                settings.bind(
                    key,
                    column,
                    "visible",
                    Gio.SettingsBindFlags.DEFAULT
                )
