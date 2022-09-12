from gi.repository import Adw, GObject, Gtk


@Gtk.Template(resource_path="/coronainfo/ui/preferences-dialog")
class PreferencesDialog(Adw.PreferencesWindow):
    __gtype_name__ = "PreferencesDialog"

    columns_group: Adw.PreferencesGroup = Gtk.Template.Child(name="columns_group")

    def __init__(self, parent: GObject.Object):
        super().__init__()
        self.set_transient_for(parent)

        self.rows: list[Adw.ActionRow] = []

    def set_columns(self, columns: list[Gtk.TreeViewColumn]):
        for column in columns:
            row = Adw.ActionRow()
            toggle = Gtk.CheckButton()
            column.bind_property(
                "visible",
                toggle,
                "active",
                GObject.BindingFlags.BIDIRECTIONAL | GObject.BindingFlags.SYNC_CREATE
            )

            row.set_title(column.get_title())
            row.add_suffix(toggle)
            row.set_activatable_widget(toggle)

            self.columns_group.add(row)
            self.rows.append(row)
