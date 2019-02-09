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
import threading

# dict mapping the special categories for "application" mimetype files
# inspired by Nautilus, Gnome Autoar, and Calibre's tables
# https://gitlab.gnome.org/GNOME/nautilus/blob/master/src/nautilus-mime-actions.c#L91
# https://github.com/GNOME/gnome-autoar/blob/master/gnome-autoar/autoar-mime-types.c
# https://github.com/kovidgoyal/calibre/blob/master/resources/calibre-mimetypes.xml
application_mimetypes = { # DOCUMENTS
                "rtf": "text",
                "msword": "text",
                "vnd.sun.xml.writer": "text",
                "vnd.sun.xml.writer.global": "text",
                "vnd.sun.xml.writer.template": "text",
                "vnd.oasis.opendocument.text": "text",
                "vnd.oasis.opendocument.text-template": "text",
                "x-abiword": "text",
                "x-applix-word": "text",
                "x-mswrite": "text",
                "docbook+xml": "text",
                "x-kword": "text",
                "x-kword-crypt": "text",
                "x-lyx": "text",
                "vnd.openxmlformats-officedocument.wordprocessingml.document": "text",
                "pdf": "text",
                "postscript": "text",
                "x-dvi": "text",

                # ARCHIVES
                "x-7z-compressed": "archives",
                "x-7z-compressed-tar": "archives",
                "x-bzip": "archives",
                "x-bzip-compressed-tar": "archives",
                "x-compress": "archives",
                "x-compressed-tar": "archives",
                "x-cpio": "archives",
                "x-gzip": "archives",
                "x-lha": "archives",
                "x-lzip": "archives",
                "x-lzip-compressed-tar": "archives",
                "x-lzma": "archives",
                "x-lzma-compressed-tar": "archives",
                "x-tar": "archives",
                "x-tarz": "archives",
                "x-xar": "archives",
                "x-xz": "archives",
                "x-xz-compressed-tar": "archives",
                "zip": "archives",
                "gzip": "archives",
                "bzip2": "archives",
                "vnd.rar": "archives",

                # ILLUSTRATION
                "illustrator": "illustration",
                "vnd.corel-draw": "illustration",
                "vnd.stardivision.draw": "illustration",
                "vnd.oasis.opendocument.graphics": "illustration",
                "x-dia-diagram": "illustration",
                "x-karbon": "illustration",
                "x-killustrator": "illustration",
                "x-kivio": "illustration",
                "x-kontour": "illustration",
                "x-wpg": "illustration",

                # MUSIC
                "ogg" : "audio",

                # IMAGES
                "vnd.oasis.opendocument.image": "image",
                "x-krita": "image",

                # PRESENTATIONS
                "vnd.ms-powerpoint": "presentations",
                "vnd.sun.xml.impress": "presentations",
                "vnd.oasis.opendocument.presentation": "presentations",
                "x-magicpoint": "presentations",
                "x-kpresenter": "presentations",
                "vnd.openxmlformats-officedocument.presentationml.presentation": "presentations",

                # SPREADSHEETS
                "vnd.lotus-1-2-3": "spreadsheets",
                "vnd.ms-excel": "spreadsheets",
                "vnd.stardivision.calc": "spreadsheets",
                "vnd.sun.xml.calc": "spreadsheets",
                "vnd.oasis.opendocument.spreadsheet": "spreadsheets",
                "x-applix-spreadsheet": "spreadsheets",
                "x-gnumeric": "spreadsheets",
                "x-kspread": "spreadsheets",
                "x-kspread-crypt": "spreadsheets",
                "x-quattropro": "spreadsheets",
                "x-sc": "spreadsheets",
                "x-siag": "spreadsheets",
                "vnd.openxmlformats-officedocument.spreadsheetml.sheet": "spreadsheets",

                # EBOOKS
                "x-sony-bbeb": "ebooks",
                "epub+zip": "ebooks",
                "text/lrs": "ebooks",
                "x-mobipocket-ebook": "ebooks",
                "x-palm-database": "ebooks",
                "x-topaz-ebook": "ebooks",
                "x-kindle-application": "ebooks",
                "x-mobipocket-subscription": "ebooks",
                "x-mobipocket-ebook": "ebooks",
                "x-mobipocket-subscription-magazine": "ebooks",
                "x-mobi8-ebook": "ebooks"
                }

# array mapping each xdg folder with the GtkList options 1-6
folders = [
    GLib.get_user_special_dir(GLib.UserDirectory.DIRECTORY_DESKTOP),
    GLib.get_user_special_dir(GLib.UserDirectory.DIRECTORY_DOCUMENTS),
    GLib.get_user_special_dir(GLib.UserDirectory.DIRECTORY_DOWNLOAD),
    GLib.get_user_special_dir(GLib.UserDirectory.DIRECTORY_MUSIC),
    GLib.get_user_special_dir(GLib.UserDirectory.DIRECTORY_PICTURES),
    GLib.get_user_special_dir(GLib.UserDirectory.DIRECTORY_VIDEOS),
    GLib.get_home_dir()
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

    # all lists
    application_list = GtkTemplate.Child()
    archives_list = GtkTemplate.Child()
    audio_list = GtkTemplate.Child()
    ebooks_list = GtkTemplate.Child()
    font_list = GtkTemplate.Child()
    illustrations_list = GtkTemplate.Child()
    image_list = GtkTemplate.Child()
    presentations_list = GtkTemplate.Child()
    spreadsheets_list = GtkTemplate.Child()
    text_list = GtkTemplate.Child()
    video_list = GtkTemplate.Child()
    
    __gtype_name__ = 'OrganizerWindow'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.init_template()

    # testing 123
    def activated (self, widget, row):
        file_popover()

    # files function separated, for threading
    
    def print_mimes(self, directory):

        # set arrays for file lists
        archives = []
        ebooks = []
        fonts = []
        illustrations = []
        image = []
        audio = []
        application = []
        presentations = []
        spreadsheets = []
        text = []
        video = []

        # instantiate Gio directory
        Gio_directory = Gio.File.new_for_path(directory).enumerate_children("*", Gio.FileQueryInfoFlags(1), None)

        # loop through FileInfo objects
        for entry in Gio_directory:

            mimetype = entry.get_content_type()
            first_mimetype = mimetype.split("/")[0]
            second_mimetype = mimetype.split("/")[1]
            name = entry.get_name()
            print(mimetype)

            # hide folders, hidden files and desktop files
            if first_mimetype != "inode" and name.startswith('.') == False and name.endswith('.desktop') == False and name.endswith('~') == False:
                application_mimetype = application_mimetypes.get(second_mimetype)
                if first_mimetype == "application" and application_mimetype:
                    if application_mimetype:
                        eval(application_mimetype).append(name)

                else:
                    eval(first_mimetype).append(name)
        Gio_directory.close()
        categories = [archives, ebooks, fonts, illustrations, image, audio, application, presentations, spreadsheets, text, video]
        category_names = ["archives", "ebooks", "fonts", "illustrations", "image", "audio", "application", "presentations", "spreadsheets", "text", "video"]
        for index, category in enumerate(categories):
            category = sorted(category, key=str.lower)
            print(category)
            for entry in category:
                row = Gtk.Builder()
                row.add_objects_from_resource("/avi/wad/Organizer/row.ui", ("file_row", "filename_label"))
                file_row = row.get_object("file_row")
                filename_label = row.get_object("filename_label")
                filename_label.set_text(entry)
                GLib.idle_add(eval("self."+category_names[index]+"_list").add, file_row)
        
        # Hide the spinner from start screen
        GLib.idle_add(self.gtk_stack.set_visible_child, self.stack_2)
        GLib.idle_add(self.spinner.destroy)

    # Back Button
    def go_back_clicked_cb(self, button):

        # if is folded on content then go to sidebar, otherwise actual back to startscreen
        if self.stack_2.get_fold().value_name == "HDY_FOLD_FOLDED" and self.stack_2.get_visible_child().get_name() == "GtkStack":
            self.stack_2.set_visible_child(self.sidebar)
        else:
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
        dialog.set_logo_icon_name(None)
        dialog.set_license_type(Gtk.License.GPL_3_0)
        dialog.set_program_name(('Organizer'))
        dialog.set_translator_credits(_('translator-credits'))
        dialog.set_version('0.1')
        dialog.set_comments(_('Organizes your files'))
        dialog.set_website('https://gitlab.gnome.org/aviwad/organizer')
        dialog.set_transient_for(self)
        dialog.run()
        dialog.destroy()

    def sidebar_clicked(self, widget, eventbutton):
        self.stack_2.set_visible_child(widget.get_stack())

    # When any location is clicked on homescreen

    def row_activated(self, widget, row):
        # loop and delete all previous all ListBoxRows
        list_of_listboxes = [self.application_list,self.archives_list,
        self.audio_list,self.ebooks_list,self.font_list,self.illustrations_list,
        self.image_list,self.presentations_list,self.spreadsheets_list,self.text_list,self.video_list]
        for current_location_list in list_of_listboxes:
            children = current_location_list.get_children()
            children_length = len(children)
            for entry in range (0, children_length):
                current_location_list.remove(children[entry])


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

            # separate thread to not hang up the entire GUI, and to render the spinner at the same time
            thread_testing = threading.Thread(target=self.print_mimes, args=(directory,))
            thread_testing.start()

            # Change title to folder
            self.header_bar.set_subtitle(directory.split('/').pop())

            # Unhide the back button
            self.go_back.show()
