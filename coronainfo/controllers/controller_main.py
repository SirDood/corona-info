import logging
from datetime import datetime

from bs4 import BeautifulSoup, Tag
from gi.repository import GLib, GObject, Gio, Gtk

from coronainfo import app
from coronainfo.enums import App, Date, Paths
from coronainfo.models import CoronaData, CoronaHeaders
from coronainfo.utils.files import get_json, write_json
from coronainfo.utils.functions import convert_to_num
from coronainfo.utils.ui_helpers import run_in_thread, evaluate_title


class MainController(GObject.Object):
    POPULATE_STARTED = "velvet-massager"
    POPULATE_FINISHED = "cube-helpless"
    PROGRESS_MESSAGE = "absurd-frosted"

    def __init__(self):
        super().__init__()
        self._setup_signals()

        self.table: Gtk.TreeView = None

        field_types = tuple(field.type for field in CoronaData.get_fields())
        logging.debug(f"Model field types: {field_types}")
        self.model = Gtk.ListStore(*field_types)
        self.country_filter = ""
        self.set_filter(self.country_filter)

        self.is_populating = False

    def start_populate(self):
        run_in_thread(self._populate_data, self.on_populate_finished)

    def on_populate_finished(self):
        self.is_populating = False
        self.emit(self.POPULATE_FINISHED)
        logging.info("Data population finished")

        # Update title
        display = evaluate_title(app.get_settings())
        self.update_progress(display)

    def on_refresh(self):
        if not self.is_populating:
            self.model.clear()
            run_in_thread(self._populate_data, self.on_populate_finished, func_args=(False,))
        else:
            logging.warning("Refresh in progress!")

    def on_save(self, window: Gtk.ApplicationWindow):
        self._dialog = Gtk.FileChooserNative(
            title="Save File as",
            transient_for=window,
            action=Gtk.FileChooserAction.SAVE,
            accept_label="_Save",
            cancel_label="_Cancel"
        )

        name = App.NAME.replace(' ', '')
        date = datetime.fromisoformat(app.get_settings().last_fetched).date()
        file_name = f"{name}_{date}.json"
        downloads_dir = Gio.File.new_for_path(str(Paths.DOWNLOADS_DIR))
        self._dialog.set_current_name(file_name)
        self._dialog.set_current_folder(downloads_dir)
        self._dialog.connect("response", self.on_save_response)
        self._dialog.show()

    def on_save_response(self, dialog: Gtk.FileChooserNative, response: int):
        logging.debug(f"Response type: {Gtk.ResponseType(response).value_name}")
        if response == Gtk.ResponseType.ACCEPT:
            dest_file: Gio.File = dialog.get_file()
            logging.info(f"Saving data to {dest_file.get_path()}")
            try:
                src_file: Gio.File = Gio.File.new_for_path(str(Paths.CACHE_JSON))
                logging.debug(f"Attempting to read file: {src_file.get_path()}")
                src_file.load_contents_async(None, self.on_read_cache_complete, dest_file)

            except GLib.Error as err:
                logging.error("An error has occurred while trying to read from cache while saving:", exc_info=True)

        self._dialog.destroy()

    def on_read_cache_complete(self, file: Gio.File, result: Gio.AsyncResult, dest_file: Gio.File):
        try:
            contents = file.load_contents_finish(result)[1]
            contents_bytes = GLib.Bytes.new(contents)
            logging.debug(f"Attempting to write to file: {dest_file.get_path()}")
            dest_file.replace_contents_bytes_async(
                contents_bytes,
                None,
                False,
                Gio.FileCreateFlags.NONE,
                None,
                self.on_write_file_complete
            )

        except GLib.Error as err:
            logging.error("An error has occurred while trying to write data:", exc_info=True)

    def on_write_file_complete(self, file: Gio.File, result: Gio.AsyncResult):
        result = file.replace_contents_finish(result)
        path = file.get_path()

        if not result:
            logging.warning(f"Unable to save data to {path}")
            return

        logging.info(f"Successfully saved data to {path}")

    def set_table(self, table: Gtk.TreeView):
        self.table = table

        # Set columns
        for i, header in enumerate(CoronaHeaders.as_tuple()):
            title = header.replace("_", " ").replace("PER", "/").title()
            renderer = Gtk.CellRendererText()
            renderer.set_property("height", 30)

            column = Gtk.TreeViewColumn(title, renderer, text=i)
            column.set_cell_data_func(renderer, self.cell_data_func, func_data=i)
            column.set_alignment(0.5)
            column.set_sort_column_id(i)
            column.set_expand(True)
            self._bind_column_settings(column)

            self.table.append_column(column)

    def cell_data_func(self, column: Gtk.TreeViewColumn,
                       renderer: Gtk.CellRendererText,
                       model: Gtk.TreeModelSort,
                       tree_iter: Gtk.TreeIter,
                       data):

        value = model.get(tree_iter, data)[0]
        if isinstance(value, int):
            display = f"{value:,}"
            if "NEW" in CoronaHeaders.as_tuple()[data]:
                display = "+" + display
            renderer.set_property("text", display)

        if data == int(CoronaHeaders.NEW_CASES):
            renderer.set_property("foreground", "rgb(255, 145, 0)")

        if data == int(CoronaHeaders.NEW_DEATHS):
            renderer.set_property("foreground", "rgb(220, 0, 0)")

        if data == int(CoronaHeaders.NEW_RECOVERED):
            renderer.set_property("foreground", "rgb(0, 160, 0)")

    def set_filter(self, text: str):
        if self.table:
            self.country_filter = text
            model_filter: Gtk.TreeModelFilter = self.model.filter_new()
            model_filter.set_visible_func(self.visible_func)
            model_proxy: Gtk.TreeModelSort = Gtk.TreeModelSort.new_with_model(model_filter)
            self.table.set_model(model_proxy)

    def visible_func(self, model: Gtk.ListStore, tree_iter: Gtk.TreeIter, data):
        if not self.country_filter:
            return True

        country = model[tree_iter][int(CoronaHeaders.COUNTRY)]
        return self.country_filter.lower() in country.lower()

    def update_progress(self, message: str):
        # TODO: look into fixing the 'Trying to snapshot XXX without a current allocation' error
        self.emit(self.PROGRESS_MESSAGE, message)

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
            self.update_progress(message)
            logging.info(message)
            dataset = self._fetch_data()
            logging.debug(f"Caching data at {cache_file}")
            write_json(cache_file, [row.as_dict() for row in dataset])

            # Update last_fetched settings
            today = datetime.now().strftime(Date.RAW_FORMAT)
            logging.debug(f"Updating last_fetched: {today}")
            settings = app.get_settings()
            settings.last_fetched = today

        message = "Reading data..."
        self.update_progress(message)
        logging.info(message)
        json_data = get_json(cache_file)
        result = map(lambda row: CoronaData(**row), json_data)
        return result

    def _fetch_data(self) -> map:
        fetch_url: Gio.File = Gio.File.new_for_uri("https://www.worldometers.info/coronavirus/")
        try:
            success, content, etag = fetch_url.load_contents(None)

            # Parse html content and find the table for today
            logging.info("Parsing fetched data...")
            soup = BeautifulSoup(content, "html.parser")
            table = soup.find(id="main_table_countries_today")
            table_body = table.find("tbody")

            message = "Parsing table HTML..."
            self.update_progress(message)
            logging.info(message)
            result = self._parse_table_html(table_body)
            return result

        except GLib.Error as err:
            logging.error("An error has occurred while fetching data:", exc_info=True)

    def _parse_table_html(self, table: Tag) -> map:
        countries: list[Tag] = table.find_all("tr")[7:]
        result = map(lambda country: sanitise_row(country), countries)

        def sanitise_row(clean_row: Tag):
            row_data = clean_row.find_all("td")[1:15]
            sanitised_row = map(lambda value: sanitise_value(value.text), row_data)
            clean_row = CoronaData(*sanitised_row)

            return clean_row

        def sanitise_value(value: str):
            sanitised_value = value.replace(",", "").strip()

            # For New Whatever values which have a + at the start
            if len(sanitised_value) > 0 and sanitised_value[0] == "+":
                sanitised_value = sanitised_value[1:]
            if sanitised_value == "N/A":
                sanitised_value = None

            clean_value = convert_to_num(sanitised_value)
            if isinstance(clean_value, float):
                clean_value = int(clean_value)

            return clean_value

        return result

    def _setup_signals(self):
        GObject.signal_new(
            self.POPULATE_STARTED,  # Signal message
            self,  # A Python GObject instance or type that the signal is associated with
            GObject.SignalFlags.RUN_LAST,  # Signal flags
            GObject.TYPE_BOOLEAN,  # Return type of the signal handler
            []  # Parameter types
        )

        GObject.signal_new(
            self.POPULATE_FINISHED,
            self,
            GObject.SignalFlags.RUN_LAST,
            GObject.TYPE_BOOLEAN,
            []
        )

        GObject.signal_new(
            self.PROGRESS_MESSAGE,
            self,
            GObject.SignalFlags.RUN_LAST,
            GObject.TYPE_BOOLEAN,
            [str]
        )

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
