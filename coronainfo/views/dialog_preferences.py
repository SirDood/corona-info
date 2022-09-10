from gi.repository import Adw, GObject, Gtk


@Gtk.Template(resource_path="/coronainfo/ui/preferences-dialog")
class PreferencesDialog(Adw.PreferencesWindow):
    __gtype_name__ = "PreferencesDialog"

    def __init__(self, parent: GObject.Object):
        super().__init__()
        self.set_transient_for(parent)
