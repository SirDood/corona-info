from bs4 import BeautifulSoup, Tag
from gi.repository import GLib, GObject, Gio, Gtk

from coronainfo.enums import Paths
from coronainfo.models import CoronaData, CoronaHeaders
from coronainfo.utils.cache import cache_json, get_cache_json
from coronainfo.utils.functions import convert_to_num


class MainController(GObject.Object):
    __gtype_name__ = "MainController"

    def __init__(self):
        self.table = None

        field_types = (field.type for field in CoronaData.get_fields())
        self.model = Gtk.ListStore(*field_types)
        self.country_filter = ""
        self.set_filter(self.country_filter)

    def start_populate(self):
        # TODO: figure out how to do this in a thread with GTK
        self.load_data()

    def load_data(self):
        for row in self._get_data():
            self.model.append(row)
        self.set_filter(self.country_filter)

    def on_refresh(self):
        # TODO: figure out how to do this in a thread with GTK
        self.refresh_data()

    def refresh_data(self):
        for row in self._get_data(use_cache=False):
            self.model.append(row)
        self.set_filter(self.country_filter)

    def set_table(self, table: Gtk.TreeView):
        self.table = table

        # Set columns
        for i, header in enumerate(CoronaHeaders.as_tuple()):
            title = header.replace("_", " ").replace("PER", "/").title()
            renderer = Gtk.CellRendererText()

            column = Gtk.TreeViewColumn(title, renderer, text=i)
            column.set_alignment(0.5)
            column.set_sort_column_id(i)
            column.set_expand(True)

            self.table.append_column(column)

    def set_filter(self, text: str):
        if self.table:
            self.country_filter = text
            model_filter: Gtk.TreeModelFilter = self.model.filter_new()
            model_filter.set_visible_func(self.visible_func)
            self.table.set_model(model_filter)

    def visible_func(self, model: Gtk.ListStore, tree_iter: Gtk.TreeIter, data):
        if not self.country_filter:
            return True

        country = model[tree_iter][int(CoronaHeaders.COUNTRY)]
        return self.country_filter.lower() in country.lower()

    def _get_data(self, use_cache: bool = True):
        cache_file = Paths.CACHE

        if not cache_file.exists() or not use_cache:
            dataset = self._fetch_data()
            cache_json(cache_file.name, [row.as_dict() for row in dataset])

        json_data = get_cache_json(cache_file.name)
        result = map(lambda row: CoronaData(**row), json_data)
        return result

    def _fetch_data(self) -> map:
        fetch_url: Gio.File = Gio.File.new_for_uri("https://www.worldometers.info/coronavirus/")
        try:
            success, content, etag = fetch_url.load_contents(None)
            print("Successfully fetched data")

            # Parse html content and find the table for today
            soup = BeautifulSoup(content, "html.parser")
            table = soup.find(id="main_table_countries_today")
            table_body = table.find("tbody")

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
