from gi.repository import Adw, GObject, Gio, Gtk

from coronainfo.controllers import AppController


@Gtk.Template(resource_path="/com.izzthedude.CoronaInfo/ui/main-content-view")
class MainContentView(Gtk.Box):
    __gtype_name__ = "MainContentView"

    searchbar: Gtk.SearchBar = Gtk.Template.Child(name="searchbar")
    search_entry: Gtk.SearchEntry = Gtk.Template.Child(name="search_entry")
    statuspage: Adw.StatusPage = Gtk.Template.Child(name="statuspage")
    table: Gtk.TreeView = Gtk.Template.Child(name="table_view")

    def __init__(self, window: Gtk.ApplicationWindow):
        super().__init__()
        self._bind_properties()

        self.searchbar.connect_entry(self.search_entry)
        self.searchbar.set_key_capture_widget(window)

        self.controller = AppController.get_main_controller()
        self.controller.connect(self.controller.POPULATE_FINISHED, self.on_populate_finished)
        self.controller.connect(self.controller.MODEL_EMPTY, self.on_model_empty)
        self.controller.connect(self.controller.ERROR_OCCURRED, self.on_error_message)
        self.controller.set_table(self.table)

    def on_toggle_search_action(self, action: Gio.SimpleAction, param):
        mode = self.searchbar.get_search_mode()
        self.searchbar.set_search_mode(not mode)

    @Gtk.Template.Callback()
    def on_search(self, entry: Gtk.SearchEntry):
        self.table.set_visible(True)
        self.controller.set_filter(entry.get_text())

    def on_populate_finished(self, controller):
        self.table.set_visible(True)

    def on_model_empty(self, controller):
        search = self.search_entry.get_text()
        self.statuspage.set_icon_name("system-search-symbolic")
        self.statuspage.set_title(f"`{search}` Not Found")
        self.statuspage.set_description("")
        self.statuspage.set_visible(True)

    def on_error_message(self, controller, message: str):
        self.statuspage.set_icon_name("dialog-error-symbolic")
        self.statuspage.set_title("An error has occurred")
        self.statuspage.set_description(message)
        self.statuspage.set_visible(True)

    def _bind_properties(self):
        self.statuspage.bind_property(
            "visible",
            self.table,
            "visible",
            GObject.BindingFlags.BIDIRECTIONAL | GObject.BindingFlags.SYNC_CREATE | GObject.BindingFlags.INVERT_BOOLEAN
        )
