from gi.repository import GObject, Gtk

from coronainfo.models import CoronaData, CoronaHeaders


class MainController(GObject.Object):
    __gtype_name__ = "MainController"

    def __init__(self):
        self.table = None

        field_types = (field.type for field in CoronaData.get_fields())
        self.model = Gtk.ListStore(*field_types)
        self.country_filter = ""
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
