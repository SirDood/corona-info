from bs4 import BeautifulSoup
from gi.repository import GLib, GObject, Gio, Gtk

from coronainfo.enums import Cache
from coronainfo.models import CoronaData, CoronaHeaders
from coronainfo.utils.cache import cache_file


class MainController(GObject.Object):
    __gtype_name__ = "MainController"

    def __init__(self):
        self.table = None

        field_types = (field.type for field in CoronaData.get_fields())
        self.model = Gtk.ListStore(*field_types)
        self.country_filter = ""
        self.set_filter(self.country_filter)

    def on_refresh(self):
        self._fetch_data()
        pass

    def _fetch_data(self):
        fetch_url: Gio.File = Gio.File.new_for_uri("https://www.worldometers.info/coronavirus/")

        success, content, etag = False, None, None
        try:
            success, content, etag = fetch_url.load_contents(None)
            print("Successfully fetched data")

            # Parse html content and find the table for today
            soup = BeautifulSoup(content, "html.parser")
            table = soup.find(id="main_table_countries_today")
            table_body = table.find("tbody")
            output = str(table_body)

        except GLib.Error as err:
            print("An error has occurred while fetching data:", err)
            return

        file_name = Cache.RAW_HTML.name
        try:
            cache_file(file_name, output)
            print("Successfully cached raw html data")

        except Exception as err:
            print("An error has occurred while caching raw html data:", err)

    def on_fetch_data_finished(self, source: Gio.File, result: Gio.AsyncResult, data):
        pass

    def set_table(self, table: Gtk.TreeView):
        self.table = table

        # Set columns
        for i, header in enumerate(CoronaHeaders.as_tuple()):
            title = header.replace("_", " ").replace("PER", "/").title()
            renderer = Gtk.CellRendererText()

            column = Gtk.TreeViewColumn(title, renderer, text=i)
            column.set_alignment(0.5)
            column.set_sort_column_id(i)
            if not i == int(CoronaHeaders.NO):
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
