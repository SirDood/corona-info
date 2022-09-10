from gi.repository import Gtk, GObject


@Gtk.Template(resource_path="/coronainfo/ui/preferences-dialog")
class PreferencesDialog(Gtk.Window):
    __gtype_name__ = "PreferencesDialog"

    def __init__(self, parent: GObject.Object):
        super().__init__()
        self.set_transient_for(parent)
