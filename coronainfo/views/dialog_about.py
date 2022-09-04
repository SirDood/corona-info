# window.py
#
# Copyright 2022 Izzat Z.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from gi.repository import Gtk


class AboutDialog(Gtk.AboutDialog):
    def __init__(self, parent):
        Gtk.AboutDialog.__init__(self)
        self.set_modal(True)
        self.set_transient_for(parent)

        self.set_program_name("Corona Info")
        self.set_version("0.1.0")
        self.set_logo_icon_name("com.izzthedude.CoronaInfo")

        self.set_authors(["Izzat Z."])
        self.set_copyright("2022 Izzat Z.")
        self.set_license_type(Gtk.License.GPL_3_0)
        self.set_website("https://github.com/izzthedude/corona-info")
        self.set_website_label("GitHub")
