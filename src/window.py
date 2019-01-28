# window.py
#
# Copyright 2019 Avi Wadhwa
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

from gi.repository import Gtk, GLib
from .gi_composites import GtkTemplate
import sys

folders=[GLib.get_user_special_dir(GLib.UserDirectory.DIRECTORY_DESKTOP), GLib.get_user_special_dir(GLib.UserDirectory.DIRECTORY_DOCUMENTS), GLib.get_user_special_dir(GLib.UserDirectory.DIRECTORY_DOWNLOAD), GLib.get_user_special_dir(GLib.UserDirectory.DIRECTORY_MUSIC), GLib.get_user_special_dir(GLib.UserDirectory.DIRECTORY_PICTURES), GLib.get_user_special_dir(GLib.UserDirectory.DIRECTORY_VIDEOS), "~"]

@GtkTemplate(ui='/org/gnome/Organizer/window.ui')
class OrganizerWindow(Gtk.ApplicationWindow):
    __gtype_name__ = 'OrganizerWindow'
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.init_template()
    def on_about_button_clicked(self, button):
        print("about clicked")
        dialog = Gtk.AboutDialog()
        dialog.set_modal(True)
        dialog.set_authors(["Avi Wadhwa"])
        dialog.set_artists(["lol there's no artwork"])
        dialog.set_logo_icon_name(None)
        dialog.set_license_type(Gtk.License.GPL_3_0)
        dialog.set_program_name(_("Organizer"))
        dialog.set_translator_credits(_("translator-credits"))
        dialog.set_version("0.1")
        dialog.set_comments(_("Organizes your files"))
        dialog.set_website("https://gitlab.gnome.org/aviwad/organizer")
        dialog.run()
        dialog.destroy()

    def row_activated(self, widget, row):
        row_index = row.get_index()
        #if row.get_index() is 7 then open filechooser
        if (row_index == 7):
            print("time to die")
        else:
            directory = folders[row_index]
            print(directory)
        #otherwise set respective location per index
