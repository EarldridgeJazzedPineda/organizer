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
from gi.repository import Gtk, GLib, Handy, Gio
from .gi_composites import GtkTemplate
import sys
import os
import threading
import time

# array mapping each xdg folder with the GtkList options 1-6
folders = [
    GLib.get_user_special_dir(GLib.UserDirectory.DIRECTORY_DESKTOP),
    GLib.get_user_special_dir(GLib.UserDirectory.DIRECTORY_DOCUMENTS),
    GLib.get_user_special_dir(GLib.UserDirectory.DIRECTORY_DOWNLOAD),
    GLib.get_user_special_dir(GLib.UserDirectory.DIRECTORY_MUSIC),
    GLib.get_user_special_dir(GLib.UserDirectory.DIRECTORY_PICTURES),
    GLib.get_user_special_dir(GLib.UserDirectory.DIRECTORY_VIDEOS),
    os.path.expanduser('~'),
    ]
# to initiate the custom libhandy widgets
Handy.init()
@GtkTemplate("/avi/wad/Organizer/window.ui")
class OrganizerWindow(Gtk.ApplicationWindow):

    # initializing widgets to be used later

    gtk_stack = GtkTemplate.Child()
    stack_2 = GtkTemplate.Child()
    go_back = GtkTemplate.Child()
    start_screen = GtkTemplate.Child()
    header_bar = GtkTemplate.Child()
    sidebar = GtkTemplate.Child()
    scrolled_start_screen = GtkTemplate.Child()
    spinner = Gtk.Spinner()
    application_list = GtkTemplate.Child()
    audio_list = GtkTemplate.Child()
    font_list = GtkTemplate.Child()
    image_list = GtkTemplate.Child()
    text_list = GtkTemplate.Child()
    video_list = GtkTemplate.Child()
    other_list = GtkTemplate.Child()
    __gtype_name__ = 'OrganizerWindow'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.init_template()

    # files function separated, for threading
    
    def print_mimes(self, directory):
        # instantiate Gio directory

        Gio_directory = Gio.File.new_for_path(directory).enumerate_children("*", Gio.FileQueryInfoFlags(1), None)

        # loop through FileInfo objects
        for entry in Gio_directory:

            # print file name for debugging purposes
            print(entry.get_name())
            mimetype = entry.get_content_type()
            first_mimetype = mimetype.split("/")[0]
            name = entry.get_name()

            # hide folders, hidden files and desktop files
            if first_mimetype != "inode" and name.startswith('.') == False and name.endswith('.desktop') == False:
                row = Gtk.Builder()
                # print mimetype for debugging purposes
                print(mimetype)
                # add GtkListBoxRow for each file in respective stack/category
                row.add_objects_from_resource("/avi/wad/Organizer/row.ui", ("file_row", "filename_label"))
                file_row = row.get_object("file_row")
                filename_label = row.get_object("filename_label")
                filename_label.set_text(entry.get_name())
                #TODO if is application, use Nautilus table and Gnome archive to move to document/archive/other categories
                try:
                    GLib.idle_add(eval("self."+first_mimetype+"_list").add, file_row)
                except:
                    print(mimetype)
                    GLib.idle_add(self.other_list.add, file_row)
        Gio_directory.close()
        # Hide the spinner from start screen
        GLib.idle_add(self.gtk_stack.set_visible_child, self.stack_2)
        GLib.idle_add(self.spinner.destroy)

    # Back Button

    def go_back_clicked_cb(self, button):

        # if is folded (mobile mode) and leaflet model is 2nd (on content), then make child 1 (go to sidebar). otherwise actual back to startscreen
        if self.stack_2.get_fold().value_name == "HDY_FOLD_FOLDED" and self.stack_2.get_visible_child().get_name() == "GtkStack":
            self.stack_2.set_visible_child(self.sidebar)
        else:
            #TODO map this to Alt+left keyboard shortcut
            # hide the back button and go to start screen
            self.go_back.hide()
            self.header_bar.set_subtitle("")
            self.gtk_stack.set_visible_child(self.scrolled_start_screen)

    # About Menu

    def on_about_button_clicked(self, button):
        dialog = Gtk.AboutDialog()
        dialog.set_modal(True)
        dialog.set_authors(['Avi Wadhwa'])
        dialog.set_artists(["lol there's no artwork"])

        # TODO: get icon

        dialog.set_logo_icon_name(None)
        dialog.set_license_type(Gtk.License.GPL_3_0)
        dialog.set_program_name(_('Organizer'))
        dialog.set_translator_credits(_('translator-credits'))
        dialog.set_version('0.1')
        dialog.set_comments(_('Organizes your files'))
        dialog.set_website('https://gitlab.gnome.org/aviwad/organizer')
        dialog.run()
        dialog.destroy()

    def sidebar_clicked(self, widget, eventbutton):
        self.stack_2.set_visible_child(widget.get_stack())

    # When any location is clicked on homescreen

    def row_activated(self, widget, row):
        #TODO loop and delete all listboxrows
        # loop and delete all previous file ListBoxRows

        #children = self.all_location_list.get_children()
        #children_length = len(children)
        #for entry in range (0, children_length):
        #    self.all_location_list.remove(children[entry])

        row_index = row.get_index()

        # Open filechooser if "other" option clicked
        
        if row_index == 7:
            directory_chooser = \
                Gtk.FileChooserDialog('Please choose a folder', None,
                    Gtk.FileChooserAction.SELECT_FOLDER,
                    (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, 'Select'
                    , Gtk.ResponseType.OK))
            response = directory_chooser.run()
            if response == Gtk.ResponseType.OK:
                response_type = True
            else:
                response_type = False
            directory_chooser.set_modal = True

            # Get foldername and then close the filechooser
            directory = directory_chooser.get_filename()
            directory_chooser.destroy()
        else:

            # Get foldername from respective folder array index
            directory = folders[row_index]
            response_type = True
        if response_type:
            row.get_child().pack_end(self.spinner, False, False, 10)
            self.spinner.set_visible(True)
            self.spinner.props.active = True
            self.spinner.start()
            #TODO make this work before the file intensive operation
            thread_testing = threading.Thread(target=self.print_mimes, args=(directory,))
            thread_testing.start()

            # Change title to folder
            self.header_bar.set_subtitle(os.path.basename(directory))

            # Unhide the back button
            self.go_back.show()
            #self.print_mimes(directory)
            #self.gtk_stack.set_visible_child(self.stack_2)
