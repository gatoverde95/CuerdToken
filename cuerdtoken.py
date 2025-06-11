#!/usr/bin/env python3
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib, Pango
import os
from datetime import datetime, UTC
from translations import translator
from actions import (
    update_repos,
    upgrade_packages,
    update_flatpak,
    clean_packages,
    autoremove_packages,
    update_all,
    check_system_status,
    CommandResult
)
from config import load_config, save_config

class CuerdTokenWindow(Gtk.Window):
    def __init__(self):
        super().__init__(title="CuerdToken")
        self.translator = translator
        
        # Set window icon using system icon
        icon_theme = Gtk.IconTheme.get_default()
        try:
            # Intentar usar un icono del sistema primero
            icon = icon_theme.load_icon("system-software-update", 48, 0)
            self.set_icon(icon)
        except GLib.Error:
            # Si falla, intentar usar un icono alternativo
            try:
                icon = icon_theme.load_icon("preferences-system", 48, 0)
                self.set_icon(icon)
            except GLib.Error:
                print("Warning: Could not load window icon")
        
        # Load saved language
        config = load_config()
        if config.get("language"):
            self.translator.set_language(config["language"])
            
        self.set_border_width(10)
        self.set_default_size(600, 400)
        
        # Store widgets that need translation updates
        self.translatable_widgets = []

        # Create UI
        self.create_ui()
        
    def update_title_label(self):
        """Update the title label with current language"""
        try:
            markup = GLib.markup_escape_text(self.translator.translate("System Management"))
            self.title_label.set_markup(
                f"<span size='x-large' weight='bold'>{markup}</span>"
            )
        except Exception as e:
            print(f"Error updating title label: {e}")
            self.title_label.set_text(self.translator.translate("System Management"))

    def create_ui(self):
        """Create the main user interface"""
        # Main vertical box to contain menubar and content
        root_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.add(root_box)

        # Add menubar
        self.create_menubar(root_box)

        # Main container for buttons
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        root_box.pack_start(main_box, True, True, 0)

        # Title label
        self.title_label = Gtk.Label()
        self.update_title_label()
        self.translatable_widgets.append(('title', self.title_label))
        main_box.pack_start(self.title_label, False, True, 10)
        
        # Grid for buttons
        grid = Gtk.Grid()
        grid.set_row_spacing(10)
        grid.set_column_spacing(10)
        grid.set_halign(Gtk.Align.CENTER)
        main_box.pack_start(grid, True, True, 0)

        # Status bar
        self.statusbar = Gtk.Statusbar()
        self.update_statusbar()
        GLib.timeout_add_seconds(1, self.update_statusbar)
        root_box.pack_end(self.statusbar, False, True, 0)

        # Define buttons with their properties
        buttons = [
            {"icon": "system-software-update", "label": "Update Repositories", 
             "action": lambda b: self.show_progress_window(
                 self.translator.translate("Update Repositories"),
                 update_repos)},
            {"icon": "software-update-available", "label": "Upgrade Packages", 
             "action": lambda b: self.show_progress_window(
                 self.translator.translate("Upgrade Packages"),
                 upgrade_packages)},
            {"icon": "flatpak-symbolic", "label": "Update Flatpak", 
             "action": lambda b: self.show_progress_window(
                 self.translator.translate("Update Flatpak"),
                 update_flatpak)},
            {"icon": "edit-clear", "label": "Clean Packages", 
             "action": lambda b: self.show_progress_window(
                 self.translator.translate("Clean Packages"),
                 clean_packages)},
            {"icon": "user-trash-full", "label": "Autoremove", 
             "action": lambda b: self.show_progress_window(
                 self.translator.translate("Autoremove"),
                 autoremove_packages)},
            {"icon": "emblem-synchronizing", "label": "Update All", 
             "action": lambda b: self.show_progress_window(
                 self.translator.translate("Update All"),
                 update_all)},
            {"icon": "utilities-system-monitor", "label": "System Status", 
             "action": lambda b: self.show_progress_window(
                 self.translator.translate("System Status"),
                 check_system_status)},
        ]

        # Create and arrange buttons in the grid
        for i, btn_data in enumerate(buttons):
            row = i // 3
            col = i % 3
            button = self.create_button(
                btn_data["icon"],
                btn_data["label"],
                btn_data["action"]
            )
            grid.attach(button, col, row, 1, 1)

    def create_menubar(self, box):
        """Create and add menubar to the main window"""
        menubar = Gtk.MenuBar()
        
        # File Menu
        file_menu = Gtk.Menu()
        file_item = Gtk.MenuItem.new_with_label(self.translator.translate("File"))
        file_item.set_submenu(file_menu)
        self.translatable_widgets.append(("File", file_item))
        
        quit_item = Gtk.MenuItem.new_with_label(self.translator.translate("Quit"))
        quit_item.connect("activate", lambda w: Gtk.main_quit())
        self.translatable_widgets.append(("Quit", quit_item))
        file_menu.append(quit_item)
        
        # Language Menu
        language_menu = Gtk.Menu()
        language_item = Gtk.MenuItem.new_with_label(self.translator.translate("Language"))
        language_item.set_submenu(language_menu)
        self.translatable_widgets.append(("Language", language_item))
        
        for lang_code, lang_name in [("en", "English"), ("es", "Español")]:
            lang_option = Gtk.MenuItem.new_with_label(lang_name)
            lang_option.connect("activate", lambda w, lc=lang_code: self.on_language_changed(lc))
            language_menu.append(lang_option)
        
        # Help Menu
        help_menu = Gtk.Menu()
        help_item = Gtk.MenuItem.new_with_label(self.translator.translate("Help"))
        help_item.set_submenu(help_menu)
        self.translatable_widgets.append(("Help", help_item))
        
        about_item = Gtk.MenuItem.new_with_label(self.translator.translate("About"))
        about_item.connect("activate", lambda w: self.on_about_clicked())
        self.translatable_widgets.append(("About", about_item))
        help_menu.append(about_item)
        
        # Add all menus to menubar
        menubar.append(file_item)
        menubar.append(language_item)
        menubar.append(help_item)
        
        box.pack_start(menubar, False, False, 0)

    def create_button(self, icon_name, label_text, callback):
        """Create a button with icon and label"""
        button = Gtk.Button()
        button.set_size_request(180, 100)
        
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        box.set_halign(Gtk.Align.CENTER)
        
        try:
            icon = Gtk.Image.new_from_icon_name(icon_name, Gtk.IconSize.DIALOG)
            box.pack_start(icon, True, True, 0)
            
            label = Gtk.Label()
            label.set_text(GLib.markup_escape_text(self.translator.translate(label_text)))
            label.set_line_wrap(True)
            label.set_line_wrap_mode(Pango.WrapMode.WORD)
            box.pack_start(label, True, True, 0)
            
            self.translatable_widgets.append((label_text, label))
            button.add(box)
            button.connect("clicked", callback)
        except Exception as e:
            print(f"Error creating button: {e}")
            
        return button

    def update_title_label(self):
        """Update the title label with current language"""
        self.title_label.set_markup(
            "<span size='x-large' weight='bold'>" + 
            self.translator.translate("System Management") + 
            "</span>"
        )

    def update_translations(self):
        """Update all translatable widgets with new language"""
        for original, widget in self.translatable_widgets:
            if isinstance(widget, Gtk.Label):
                if original == 'title':
                    self.update_title_label()
                else:
                    widget.set_label(self.translator.translate(original))
            elif isinstance(widget, Gtk.MenuItem):
                widget.set_label(self.translator.translate(original))
        
        # Force window to redraw
        self.queue_draw()

    def on_language_changed(self, lang_code):
        """Handle language change"""
        self.translator.set_language(lang_code)
        save_config({"language": lang_code})
        self.update_translations()
        
        # Show confirmation dialog
        self.show_info_dialog(
            self.translator.translate("Language Changed"),
            self.translator.translate("Language has been updated.")
        )

    def update_statusbar(self):
        """Update status bar with current time and user"""
        try:
            current_time = datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S")
            username = os.getenv('USER', 'unknown')
            status_text = GLib.markup_escape_text(
                f"{self.translator.translate('User')}: {username} | UTC: {current_time}"
            )
            self.statusbar.remove_all(0)
            self.statusbar.push(0, status_text)
        except Exception as e:
            print(f"Error updating statusbar: {e}")
        return True

    def show_info_dialog(self, title, message):
        """Show an information dialog"""
        dialog = Gtk.MessageDialog(
            transient_for=self,
            flags=0,
            message_type=Gtk.MessageType.INFO,
            buttons=Gtk.ButtonsType.OK,
            text=title
        )
        dialog.format_secondary_text(message)
        dialog.run()
        dialog.destroy()

    def show_progress_window(self, title, action_callback):
        """Show a progress dialog for an action"""
        dialog = ProgressDialog(self, title, self.translator)
        dialog.run_action(action_callback)

    def on_about_clicked(self):
        """Show about dialog"""
        try:
            dialog = Gtk.AboutDialog(transient_for=self)
            dialog.set_modal(True)
            
            # Set program icon for about dialog
            icon_theme = Gtk.IconTheme.get_default()
            try:
                # Try system icon first
                icon = icon_theme.load_icon("system-software-update", 128, 0)
                dialog.set_logo(icon)
            except GLib.Error:
                try:
                    # Fallback to alternative system icon
                    icon = icon_theme.load_icon("preferences-system", 128, 0)
                    dialog.set_logo(icon)
                except GLib.Error:
                    print("Warning: Could not load about dialog logo")
            
            dialog.set_program_name("CuerdToken")
            dialog.set_version("1.0")
            dialog.set_copyright("© 2025 CuerdOS")
            dialog.set_comments(self.translator.translate(
                "A simple system management tool for Linux systems."
            ))
            dialog.set_website("https://cuerdos.github.io")
            dialog.set_website_label(self.translator.translate("Project Website"))
            
            # Agregamos más información
            authors = ["gatoverde95"]
            dialog.set_authors(authors)
            
            # Add current system information
            system_info = (
                f"System Information:\n"
                f"Current User: {os.getenv('USER', 'unknown')}\n"
                f"Date: {datetime.now(UTC).strftime('%Y-%m-%d %H:%M:%S')} UTC"
            )
            dialog.set_system_information(system_info)
            
            dialog.set_license_type(Gtk.License.GPL_3_0)
            
            dialog.run()
            dialog.destroy()
        except Exception as e:
            print(f"Error showing about dialog: {e}")

class ProgressDialog(Gtk.Dialog):
    def __init__(self, parent, title, trans):
        super().__init__(
            title=title,
            parent=parent,
            flags=0
        )
        self.translator = trans
        self.set_default_size(400, 150)
        self.set_border_width(10)

        content_area = self.get_content_area()
        
        self.status_label = Gtk.Label(label=self.translator.translate("Starting..."))
        content_area.pack_start(self.status_label, True, True, 0)

        self.progress_bar = Gtk.ProgressBar()
        self.progress_bar.set_show_text(True)
        content_area.pack_start(self.progress_bar, True, True, 0)

        self.cancel_button = Gtk.Button.new_with_label(self.translator.translate("Cancel"))
        self.cancel_button.connect("clicked", lambda w: self.response(Gtk.ResponseType.CANCEL))
        content_area.pack_start(self.cancel_button, True, True, 0)

        self.show_all()
        self.cancelled = False

    def show_result_dialog(self, result):
        """Show the result of the operation"""
        message_type = Gtk.MessageType.INFO if result.success else Gtk.MessageType.ERROR
        
        if result.success:
            title = self.translator.translate("Operation Successful")
            message = self.translator.translate(result.message)
            
            if result.details:
                if "upgraded" in result.details:
                    message += f"\n\n{self.translator.translate('Packages updated')}: {result.details['upgraded']}"
                    message += f"\n{self.translator.translate('Newly installed')}: {result.details['newly_installed']}"
                    message += f"\n{self.translator.translate('To remove')}: {result.details['to_remove']}"
                if "updated" in result.details:
                    message += f"\n\n{self.translator.translate('Flatpak apps updated')}: {result.details['updated']}"
                if "removed" in result.details:
                    message += f"\n\n{self.translator.translate('Packages removed')}: {result.details['removed']}"
                if "flatpak_updated" in result.details:
                    message += f"\n{self.translator.translate('Flatpak apps updated')}: {result.details['flatpak_updated']}"
                if "status" in result.details:
                    message = result.details["status"]
        else:
            title = self.translator.translate("Operation Failed")
            message = self.translator.translate(result.message)

        dialog = Gtk.MessageDialog(
            transient_for=self.get_parent(),
            flags=0,
            message_type=message_type,
            buttons=Gtk.ButtonsType.OK,
            text=title
        )
        dialog.format_secondary_text(message)
        dialog.run()
        dialog.destroy()

    def update_progress(self, fraction, status_text):
        """Update progress bar and status label"""
        self.progress_bar.set_fraction(fraction)
        self.status_label.set_text(self.translator.translate(status_text))
        return not self.cancelled

    def run_action(self, action_callback):
        """Run the action in a separate thread"""
        def run_in_thread():
            try:
                result = action_callback(self.update_progress)
                GLib.idle_add(self.show_result_dialog, result)
            except Exception as e:
                GLib.idle_add(
                    self.show_result_dialog,
                    CommandResult(False, f"Error: {str(e)}")
                )
            finally:
                GLib.idle_add(self.response, Gtk.ResponseType.OK)

        GLib.Thread.new(None, run_in_thread)
        self.run()
        self.destroy()

def main():
    try:
        win = CuerdTokenWindow()
        win.connect("destroy", Gtk.main_quit)
        win.show_all()
        Gtk.main()
    except Exception as e:
        print(f"Error initializing application: {e}")
        return 1
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())