from bs4 import BeautifulSoup, Tag
from gi.repository import GLib, GObject, Gio, Gtk

from coronainfo.enums import Paths
from coronainfo.models import CoronaData, CoronaHeaders
from coronainfo.utils.cache import cache_json, get_cache_json
from coronainfo.utils.functions import convert_to_num
from coronainfo.utils.ui_helpers import run_in_thread


class MainController(GObject.Object):
    POPULATE_STARTED = "velvet-massager"
    POPULATE_FINISHED = "cube-helpless"
    PROGRESS_MESSAGE = "absurd-frosted"

    def __init__(self):
        super().__init__()
        self._setup_signals()

        self.table: Gtk.TreeView = None

        field_types = (field.type for field in CoronaData.get_fields())
        self.model = Gtk.ListStore(*field_types)
        self.country_filter = ""
        self.set_filter(self.country_filter)

        self.is_populating = False

    def start_populate(self):
        run_in_thread(self._populate_data, self.on_populate_finished)

    def on_refresh(self):
        if not self.is_populating:
            self.model.clear()
            run_in_thread(self._populate_data, self.on_populate_finished, func_args=(False,))
        else:
            print("[WARNING]: Refresh in progress")

    def on_populate_finished(self):
        self.is_populating = False
        self.emit(self.POPULATE_FINISHED)

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

        self.table.set_model(None)
        for row in self._get_data(use_cache=use_cache):
            self.model.append(row)
        self.set_filter(self.country_filter)

    def _get_data(self, use_cache: bool = True):
        cache_file = Paths.CACHE

        if not cache_file.exists() or not use_cache:
            self.update_progress("Fetching data...")
            dataset = self._fetch_data()
            cache_json(cache_file.name, [row.as_dict() for row in dataset])

        self.update_progress("Reading data...")
        json_data = get_cache_json(cache_file.name)
        result = map(lambda row: CoronaData(**row), json_data)
        return result

    def _fetch_data(self) -> map:
        fetch_url: Gio.File = Gio.File.new_for_uri("https://www.worldometers.info/coronavirus/")
        try:
            success, content, etag = fetch_url.load_contents(None)

            # Parse html content and find the table for today
            soup = BeautifulSoup(content, "html.parser")
            table = soup.find(id="main_table_countries_today")
            table_body = table.find("tbody")

            self.update_progress("Parsing HTML...")
            result = self._parse_table_html(table_body)
            return result

        except GLib.Error as err:
            print("An error has occurred while fetching data:", err)

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
