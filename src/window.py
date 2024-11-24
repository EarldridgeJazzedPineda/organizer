# window.py
#
# Copyright 2019 Avi Wadhwa
# Copyright 2024 Earldridge Jazzed Pineda
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
#from .gi_composites import GtkTemplate
import threading
import shutil
# until I realize why GLib permissions are messed up
import os
from time import sleep

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

category_names = ["archives", "text", "ebooks", "font", "illustrations", "image", "audio", "application", "presentations", "spreadsheets", "video"]

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
@Gtk.Template(resource_path="/org/librehunt/Organizer/window.ui")
class OrganizerWindow(Gtk.ApplicationWindow):
    __gtype_name__ = 'OrganizerWindow'

    # initializing widgets to be used later
    subtitle = Gtk.Template.Child()
    gtk_stack = Gtk.Template.Child()
    stack_2 = Gtk.Template.Child()
    file_sorting = Gtk.Template.Child()
    go_back = Gtk.Template.Child()
    go_back_revealer = Gtk.Template.Child()
    subtitle_revealer = Gtk.Template.Child()
    start_screen = Gtk.Template.Child()
    header_bar = Gtk.Template.Child()
    sidebar = Gtk.Template.Child()
    sidebar_scrolled_window = Gtk.Template.Child()
    scrolled_start_screen = Gtk.Template.Child()
    spinner = Gtk.Spinner()
    busy_title = Gtk.Template.Child()
    inappnotification_revealer = Gtk.Template.Child()
    inappnotification_button = Gtk.Template.Child()
    inappnotification_label = Gtk.Template.Child()

    # all lists
    application_list = Gtk.Template.Child()
    archives_list = Gtk.Template.Child()
    audio_list = Gtk.Template.Child()
    ebooks_list = Gtk.Template.Child()
    font_list = Gtk.Template.Child()
    illustrations_list = Gtk.Template.Child()
    image_list = Gtk.Template.Child()
    presentations_list = Gtk.Template.Child()
    spreadsheets_list = Gtk.Template.Child()
    text_list = Gtk.Template.Child()
    video_list = Gtk.Template.Child()

    # all columns
    application_column = Gtk.Template.Child()
    archives_column = Gtk.Template.Child()
    audio_column = Gtk.Template.Child()
    ebooks_column = Gtk.Template.Child()
    font_column = Gtk.Template.Child()
    illustrations_column = Gtk.Template.Child()
    image_column = Gtk.Template.Child()
    presentations_column = Gtk.Template.Child()
    spreadsheets_column = Gtk.Template.Child()
    text_column = Gtk.Template.Child()
    video_column = Gtk.Template.Child()

    # all category location options
    archive_location_option = Gtk.Template.Child()
    ebooks_location_option = Gtk.Template.Child()
    font_location_option = Gtk.Template.Child()
    illustrations_location_option = Gtk.Template.Child()
    application_location_option = Gtk.Template.Child()
    presentations_location_option = Gtk.Template.Child()
    spreadsheets_location_option = Gtk.Template.Child()
    audio_location_option = Gtk.Template.Child()
    image_location_option = Gtk.Template.Child()
    text_location_option = Gtk.Template.Child()
    video_location_option = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        #self.init_template()

    def does_exist(self, file, directory, index):
        filename, file_extension = os.path.splitext(file)
        if index == 0:
            duplicate_versioning = ""
        else:
            duplicate_versioning = " ("+str(index+1)+")"
        if not os.path.exists(directory+"/"+filename+duplicate_versioning+file_extension):
            file = filename+duplicate_versioning+file_extension
            return file
        return self.does_exist(file, directory, index+1)

    def mainloop_after_move(self, newdirectory):
        self.busy_title.set_visible(False)
        self.busy_title.props_active = False
        newdirectory_last_name = newdirectory.split('/').pop()
        self.inappnotification_revealer.set_reveal_child(False)
        self.inappnotification_label.set_text("Files moved successfully")
        self.inappnotification_revealer.set_reveal_child(True)
        # so the popover can popdown before anything else happens
        sleep(0.5)
        if not len(visible_index_list)-1:
            # only one category then
            self.go_back_revealer.set_reveal_child(False)
            self.subtitle_revealer.set_reveal_child(False)
            self.gtk_stack.set_visible_child(self.scrolled_start_screen)
        else:
            row_index = self.sidebar.get_selected_row().get_index()
            row_index_in_visible = visible_index_list.index(row_index)
            # remove older row index from index list
            visible_index_list.remove(row_index)
            # hide da row
            self.sidebar.get_selected_row().set_visible(False)
            # select row behind / forward
            try:
                new_row_index = visible_index_list[row_index_in_visible-1]
            except:
                new_row_index = visible_index_list[row_index_in_visible+1]
            # set that row as selected
            newer_row = self.sidebar.get_row_at_index(new_row_index)
            self.sidebar.select_row(newer_row)

    def mainloop_after_mime(self):
        # Hide the spinner from start screen
        self.spinner.destroy()
        global visible_index_list
        visible_index_list = []
        categories = [archives, text, ebooks, font, illustrations, image, audio, application, presentations, spreadsheets, video]
        for index, category in enumerate(categories):
            category = sorted(category, key=str.lower)
            if len(category):
                visible_index_list.append(index)
            if not len(category):
                self.sidebar.get_row_at_index(index).set_visible(False)
                # set the respective row to visible false
            for entry in category:
                row = Gtk.Builder()
                row.add_objects_from_resource("/org/librehunt/Organizer/row.ui", ("file_row", "filename_label"))
                file_row = row.get_object("file_row")
                filename_label = row.get_object("filename_label")
                filename_label.set_text(entry)
                eval("self."+category_names[index]+"_list").add(file_row)
        first_proper_category = next((i for i, x in enumerate(categories) if x), None)
        try:
            self.file_sorting.set_visible_child(eval("self."+category_names[first_proper_category]+"_column"))
            self.stack_2.set_visible_child(self.sidebar_scrolled_window)
            self.gtk_stack.set_visible_child(self.stack_2)
            # Change title to folder
            self.subtitle.set_text(directory.split('/').pop())
            self.subtitle_revealer.set_reveal_child(True)
            # Unhide the back button
            self.go_back_revealer.set_reveal_child(True)
        except:
            self.inappnotification_revealer.set_reveal_child(False)
            self.inappnotification_label.set_text("Folder was already empty")
            self.inappnotification_revealer.set_reveal_child(True)
            self.go_back_clicked_cb("")
            # in app notification that app already sorted
    def move_files_threading(self, directory, newdirectory, files, popover):
        GLib.idle_add(popover.hide,)
        for file in files:
            new_file = self.does_exist(file, newdirectory, 0)
            try:
                shutil.move(directory+"/"+file, newdirectory+"/"+new_file)
            except:
                self.inappnotification_revealer.set_reveal_child(False)
                self.inappnotification_label.set_text("Error occurred")
                self.inappnotification_revealer.set_reveal_child(True)
        GLib.idle_add(self.mainloop_after_move, newdirectory)
                # select row in front
        # move to previous listboxrow
        # but if first, then next
        # but if last, then go back home
        # hide current listboxrow

    def move_files(self, directory, newdirectory, files, popover):
        self.busy_title.set_visible(True)
        self.busy_title.props_active= True
        self.busy_title.start()
        move_thread = threading.Thread(target=self.move_files_threading, args=(directory, newdirectory, files, popover,))
        move_thread.start()

    # files function separated, for threading
    def print_mimes(self, directory):
        # set arrays for file lists
        global archives
        global ebooks
        global font
        global illustrations
        global image
        global audio
        global application
        global presentations
        global spreadsheets
        global text
        global video
        archives = []
        ebooks = []
        font = []
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

            # hide folders, hidden files and desktop files
            if first_mimetype != "inode" and name.startswith('.') == False and name.endswith('.desktop') == False and name.endswith('~') == False:
                application_mimetype = application_mimetypes.get(second_mimetype)
                if first_mimetype == "application" and application_mimetype:
                    if application_mimetype:
                        eval(application_mimetype).append(name)

                else:
                    eval(first_mimetype).append(name)
        Gio_directory.close()
        GLib.idle_add(self.mainloop_after_mime,)
    # Back Button
    @Gtk.Template.Callback()
    def go_back_clicked_cb(self, button):

        # if is folded on content then go to sidebar, otherwise actual back to startscreen
        if self.stack_2.get_folded() and self.stack_2.get_visible_child().get_name() == "GtkStack":
            self.stack_2.set_visible_child(self.sidebar_scrolled_window)
        else:
            # hide the back button using gtkrevealer and go to start screen
            self.go_back_revealer.set_reveal_child(False)
            self.subtitle_revealer.set_reveal_child(False)
            self.gtk_stack.set_visible_child(self.scrolled_start_screen)

    # In app notification close button
    @Gtk.Template.Callback()
    def inappnotification_button_clicked_cb(self, button):
        self.inappnotification_revealer.set_reveal_child(False)

    # About Menu
    @Gtk.Template.Callback()
    def on_about_button_clicked(self, button):
        dialog = Gtk.AboutDialog()
        dialog.set_modal(True)
        dialog.set_authors(['Avi Wadhwa'])
        dialog.set_artists(["Avi Wadhwa", "Tobias Bernard"])
        dialog.set_logo_icon_name("org.librehunt.Organizer")
        dialog.set_license_type(Gtk.License.GPL_3_0)
        dialog.set_program_name(('Organizer'))
        dialog.set_translator_credits(_('translator-credits'))
        dialog.set_version('0.201')
        dialog.set_comments(_('Organizes your files'))
        dialog.set_website('https://github.com/aviwad/organizer')
        dialog.set_transient_for(self)
        dialog.run()
        dialog.destroy()
    @Gtk.Template.Callback()
    def category_row_clicked(self, widget, row):
        self.file_sorting.set_visible_child(eval("self."+category_names[row.get_index()]+"_column"))
        self.stack_2.set_visible_child(self.file_sorting)

    # When any location is clicked on homescreen
    @Gtk.Template.Callback()
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
        for sidebar_row in self.sidebar.get_children():
            sidebar_row.set_visible(True)


        row_index = row.get_index()
        global directory

        # Open filechooser if "other" option clicked
        if row_index == 7:
            directory_chooser = \
                Gtk.FileChooserDialog('Please choose a folder', None,
                    Gtk.FileChooserAction.SELECT_FOLDER,
                    (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, 'Select'
                    , Gtk.ResponseType.OK))
            directory_chooser.set_transient_for(self)
            directory_chooser.set_modal = True
            response = directory_chooser.run()
            if response == Gtk.ResponseType.OK:
                response_type = True
            else:
                response_type = False

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
    @Gtk.Template.Callback()
    def archives_move_clicked(self, button):
        if self.archive_location_option.get_active():
            archive_directory_chooser = Gtk.FileChooserDialog('Choose where to move the Archive files', None, Gtk.FileChooserAction.SELECT_FOLDER, (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, 'Select', Gtk.ResponseType.OK))
            archive_directory_chooser.set_transient_for(self)
            archive_directory_chooser.set_modal = True
            response = archive_directory_chooser.run()
            if response == Gtk.ResponseType.OK:
                response_type = True
            else:
                response_type = False
            # Get foldername and then close the filechooser
            newdirectory = archive_directory_chooser.get_filename()
            archive_directory_chooser.destroy()
            # get filechooser, use that to move files
        else:
            response_type = True
            newdirectory = directory+"/Archives"
            if not os.path.exists(newdirectory):
                os.mkdir(newdirectory)
        if response_type:
            #button.get_parent().get_parent().get_parent().popdown()
            self.move_files(directory, newdirectory, archives, button.get_parent().get_parent().get_parent())
    @Gtk.Template.Callback()
    def ebooks_move_clicked(self, button):
        if self.ebooks_location_option.get_active():
            ebooks_directory_chooser = Gtk.FileChooserDialog('Choose where to move the Ebook files', None, Gtk.FileChooserAction.SELECT_FOLDER, (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, 'Select', Gtk.ResponseType.OK))
            ebooks_directory_chooser.set_transient_for(self)
            ebooks_directory_chooser.set_modal = True
            response = ebooks_directory_chooser.run()
            if response == Gtk.ResponseType.OK:
                response_type = True
            else:
                response_type = False
            # Get foldername and then close the filechooser
            newdirectory = ebooks_directory_chooser.get_filename()
            ebooks_directory_chooser.destroy()
            # get filechooser, use that to move files
        else:
            response_type = True
            newdirectory = directory+"/Ebooks"
            if not os.path.exists(newdirectory):
                os.mkdir(newdirectory)
        if response_type:
            #button.get_parent().get_parent().get_parent().popdown()
            self.move_files(directory, newdirectory, ebooks, button.get_parent().get_parent().get_parent())
    @Gtk.Template.Callback()
    def font_move_clicked(self, button):
        if self.font_location_option.get_active():
            font_directory_chooser = Gtk.FileChooserDialog('Choose where to move the Font files', None, Gtk.FileChooserAction.SELECT_FOLDER, (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, 'Select', Gtk.ResponseType.OK))
            font_directory_chooser.set_transient_for(self)
            font_directory_chooser.set_modal = True
            response = font_directory_chooser.run()
            if response == Gtk.ResponseType.OK:
                response_type = True
            else:
                response_type = False
            # Get foldername and then close the filechooser
            newdirectory = font_directory_chooser.get_filename()
            font_directory_chooser.destroy()
            # get filechooser, use that to move files
        else:
            response_type = True
            newdirectory = directory+"/Fonts"
            if not os.path.exists(newdirectory):
                os.mkdir(newdirectory)
        if response_type:
            #button.get_parent().get_parent().get_parent().popdown()
            self.move_files(directory, newdirectory, font, button.get_parent().get_parent().get_parent())
    @Gtk.Template.Callback()
    def illustrations_move_clicked(self, button):
        if self.illustrations_location_option.get_active():
            illustrations_directory_chooser = Gtk.FileChooserDialog('Choose where to move the Illustration files', None, Gtk.FileChooserAction.SELECT_FOLDER, (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, 'Select', Gtk.ResponseType.OK))
            illustrations_directory_chooser.set_transient_for(self)
            illustrations_directory_chooser.set_modal = True
            response = illustrations_directory_chooser.run()
            if response == Gtk.ResponseType.OK:
                response_type = True
            else:
                response_type = False
            # Get foldername and then close the filechooser
            newdirectory = illustrations_directory_chooser.get_filename()
            illustrations_directory_chooser.destroy()
            # get filechooser, use that to move files
        else:
            response_type = True
            newdirectory = directory+"/Illustrations"
            if not os.path.exists(newdirectory):
                os.mkdir(newdirectory)
        if response_type:
            #button.get_parent().get_parent().get_parent().popdown()
            self.move_files(directory, newdirectory, illustrations, button.get_parent().get_parent().get_parent())
    @Gtk.Template.Callback()
    def application_move_clicked(self, button):
        if self.application_location_option.get_active():
            application_directory_chooser = Gtk.FileChooserDialog('Choose where to move the Other files', None, Gtk.FileChooserAction.SELECT_FOLDER, (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, 'Select', Gtk.ResponseType.OK))
            application_directory_chooser.set_transient_for(self)
            application_directory_chooser.set_modal = True
            response = application_directory_chooser.run()
            if response == Gtk.ResponseType.OK:
                response_type = True
            else:
                response_type = False
            # Get foldername and then close the filechooser
            newdirectory = application_directory_chooser.get_filename()
            application_directory_chooser.destroy()
            # get filechooser, use that to move files
        else:
            response_type = True
            newdirectory = directory+"/Other"
            if not os.path.exists(newdirectory):
                os.mkdir(newdirectory)
        if response_type:
            #button.get_parent().get_parent().get_parent().popdown()
            self.move_files(directory, newdirectory, application, button.get_parent().get_parent().get_parent())

    @Gtk.Template.Callback()
    def presentations_move_clicked(self, button):
        if self.presentations_location_option.get_active():
            presentations_directory_chooser = Gtk.FileChooserDialog('Choose where to move the Presentation files', None, Gtk.FileChooserAction.SELECT_FOLDER, (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, 'Select', Gtk.ResponseType.OK))
            presentation_directory_chooser.set_transient_for(self)
            presentation_directory_chooser.set_modal = True
            response = presentation_directory_chooser.run()
            if response == Gtk.ResponseType.OK:
                response_type = True
            else:
                response_type = False
            # Get foldername and then close the filechooser
            newdirectory = presentation_directory_chooser.get_filename()
            presentation_directory_chooser.destroy()
            # get filechooser, use that to move files
        else:
            response_type = True
            newdirectory = directory+"/Presentations"
            if not os.path.exists(newdirectory):
                os.mkdir(newdirectory)
        if response_type:
            #button.get_parent().get_parent().get_parent().popdown()
            self.move_files(directory, newdirectory, presentations, button.get_parent().get_parent().get_parent())

    @Gtk.Template.Callback()
    def spreadsheets_move_clicked(self, button):
        if self.spreadsheets_location_option.get_active():
            spreadsheets_directory_chooser = Gtk.FileChooserDialog('Choose where to move the Spreadsheet files', None, Gtk.FileChooserAction.SELECT_FOLDER, (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, 'Select', Gtk.ResponseType.OK))
            spreadsheets_directory_chooser.set_transient_for(self)
            spreadsheets_directory_chooser.set_modal = True
            response = spreadsheets_directory_chooser.run()
            if response == Gtk.ResponseType.OK:
                response_type = True
            else:
                response_type = False
            # Get foldername and then close the filechooser
            newdirectory = spreadsheets_directory_chooser.get_filename()
            spreadsheets_directory_chooser.destroy()
            # get filechooser, use that to move files
        else:
            response_type = True
            newdirectory = directory+"/Spreadsheets"
            if not os.path.exists(newdirectory):
                os.mkdir(newdirectory)
        if response_type:
            #button.get_parent().get_parent().get_parent().popdown()
            self.move_files(directory, newdirectory, spreadsheets, button.get_parent().get_parent().get_parent())

    @Gtk.Template.Callback()
    def audio_move_clicked(self, button):
        if self.audio_location_option.get_active():
            audio_directory_chooser = Gtk.FileChooserDialog('Choose where to move the Music files', None, Gtk.FileChooserAction.SELECT_FOLDER, (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, 'Select', Gtk.ResponseType.OK))
            audio_directory_chooser.set_transient_for(self)
            audio_directory_chooser.set_modal = True
            response = audio_directory_chooser.run()
            if response == Gtk.ResponseType.OK:
                response_type = True
            else:
                response_type = False
            # Get foldername and then close the filechooser
            newdirectory = audio_directory_chooser.get_filename()
            audio_directory_chooser.destroy()
            # get filechooser, use that to move files
        else:
            response_type = True
            newdirectory = directory+"/Music"
            if not os.path.exists(newdirectory):
                os.mkdir(newdirectory)
        if response_type:
            #button.get_parent().get_parent().get_parent().popdown()
            self.move_files(directory, newdirectory, audio, button.get_parent().get_parent().get_parent())

    @Gtk.Template.Callback()
    def image_move_clicked(self, button):
        if self.image_location_option.get_active():
            image_directory_chooser = Gtk.FileChooserDialog('Choose where to move the Image files', None, Gtk.FileChooserAction.SELECT_FOLDER, (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, 'Select', Gtk.ResponseType.OK))
            image_directory_chooser.set_transient_for(self)
            image_directory_chooser.set_modal = True
            response = image_directory_chooser.run()
            if response == Gtk.ResponseType.OK:
                response_type = True
            else:
                response_type = False
            # Get foldername and then close the filechooser
            newdirectory = image_directory_chooser.get_filename()
            image_directory_chooser.destroy()
            # get filechooser, use that to move files
        else:
            response_type = True
            newdirectory = directory+"/Images"
            if not os.path.exists(newdirectory):
                os.mkdir(newdirectory)
        if response_type:
            #button.get_parent().get_parent().get_parent().popdown()
            self.move_files(directory, newdirectory, image, button.get_parent().get_parent().get_parent())

    @Gtk.Template.Callback()
    def text_move_clicked(self, button):
        if self.text_location_option.get_active():
            text_directory_chooser = Gtk.FileChooserDialog('Choose where to move the Document files', None, Gtk.FileChooserAction.SELECT_FOLDER, (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, 'Select', Gtk.ResponseType.OK))
            text_directory_chooser.set_transient_for(self)
            text_directory_chooser.set_modal = True
            response = text_directory_chooser.run()
            if response == Gtk.ResponseType.OK:
                response_type = True
            else:
                response_type = False
            # Get foldername and then close the filechooser
            newdirectory = text_directory_chooser.get_filename()
            text_directory_chooser.destroy()
            # get filechooser, use that to move files
        else:
            response_type = True
            newdirectory = directory+"/Documents"
            if not os.path.exists(newdirectory):
                os.mkdir(newdirectory)
        if response_type:
            #button.get_parent().get_parent().get_parent().popdown()
            self.move_files(directory, newdirectory, text, button.get_parent().get_parent().get_parent())

    @Gtk.Template.Callback()
    def video_move_clicked(self, button):
        if self.video_location_option.get_active():
            video_directory_chooser = Gtk.FileChooserDialog('Choose where to move the Video files', None, Gtk.FileChooserAction.SELECT_FOLDER, (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, 'Select', Gtk.ResponseType.OK))
            video_directory_chooser.set_transient_for(self)
            video_directory_chooser.set_modal = True
            response = video_directory_chooser.run()
            if response == Gtk.ResponseType.OK:
                response_type = True
            else:
                response_type = False
            # Get foldername and then close the filechooser
            newdirectory = video_directory_chooser.get_filename()
            video_directory_chooser.destroy()
            # get filechooser, use that to move files
        else:
            response_type = True
            newdirectory = directory+"/Videos"
            if not os.path.exists(newdirectory):
                os.mkdir(newdirectory)
        if response_type:
            self.move_files(directory, newdirectory, video, button.get_parent().get_parent().get_parent())
