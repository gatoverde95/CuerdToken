#!/usr/bin/env python3
import locale
import os

def get_system_language():
    """Get the system's language code"""
    try:
        # Try to get the LANG environment variable first
        lang_env = os.getenv('LANG', '').split('.')[0]
        if lang_env:
            return lang_env[:2].lower()
        
        # If LANG is not set, try locale.getdefaultlocale()
        system_lang = locale.getdefaultlocale()
        if system_lang and system_lang[0]:
            return system_lang[0][:2].lower()
    except:
        pass
    return 'en'  # Default to English if detection fails

class Translator:
    def __init__(self):
        self.current_lang = get_system_language()
        if self.current_lang not in ['en', 'es']:
            self.current_lang = 'en'

        self.translations = {
            "en": {
                # Menu items
                "File": "File",
                "Edit": "Edit",
                "View": "View",
                "Help": "Help",
                "About": "About",
                "Quit": "Quit",
                "Language": "Language",
                
                # Main window
                "System Management": "System Management",
                "Update Repositories": "Update Repositories",
                "Upgrade Packages": "Upgrade Packages",
                "Update Flatpak": "Update Flatpak",
                "Clean Packages": "Clean Packages",
                "Autoremove": "Autoremove",
                "Update All": "Update All",
                "System Status": "System Status",
                
                # Progress dialog
                "Starting...": "Starting...",
                "Cancel": "Cancel",
                "Completed": "Completed",
                "Error": "Error",
                "Progress": "Progress",
                
                # Status bar
                "User": "User",
                
                # About dialog
                "A simple system management tool for Linux systems.": 
                    "A simple system management tool for CuerdOS.",
                "Project Website": "Website",
                
                # Messages
                "Language Changed": "Language Changed",
                "Please restart the application to apply the language change.":
                    "Please restart the application to apply the language change.",
                
                # Status messages
                "Updating repositories...": "Updating repositories...",
                "Upgrading packages...": "Upgrading packages...",
                "Updating Flatpak applications...": "Updating Flatpak applications...",
                "Cleaning package cache...": "Cleaning package cache...",
                "Removing unused packages...": "Removing unused packages...",
                "Checking system status...": "Checking system status...",
                "Task completed successfully": "Task completed successfully",
                "Task failed": "Task failed",
                "Operation cancelled": "Operation cancelled",
                "Operation Successful": "Operation Successful",
                "Operation Failed": "Operation Failed",
                "Packages updated": "Packages updated",
                "Newly installed": "Newly installed",
                "To remove": "To remove",
                "Flatpak apps updated": "Flatpak apps updated",
                "Packages removed": "Packages removed",
            },
            "es": {
                # Elementos del menú
                "File": "Archivo",
                "Edit": "Editar",
                "View": "Ver",
                "Help": "Ayuda",
                "About": "Acerca de",
                "Quit": "Salir",
                "Language": "Idioma",
                
                # Ventana principal
                "System Management": "Gestión del Sistema",
                "Update Repositories": "Actualizar Repositorios",
                "Upgrade Packages": "Actualizar Paquetes",
                "Update Flatpak": "Actualizar Flatpak",
                "Clean Packages": "Limpiar Paquetes",
                "Autoremove": "Autoremover",
                "Update All": "Actualizar Todo",
                "System Status": "Estado del Sistema",
                
                # Diálogo de progreso
                "Starting...": "Iniciando...",
                "Cancel": "Cancelar",
                "Completed": "Completado",
                "Error": "Error",
                "Progress": "Progreso",
                
                # Barra de estado
                "User": "Usuario",
                
                # Diálogo Acerca de
                "A simple system management tool for Linux systems.": 
                    "Una herramienta simple de gestión del sistema para CuerdOS.",
                "Project Website": "Pagina Web",
                
                # Mensajes
                "Language Changed": "Idioma Cambiado",
                "Please restart the application to apply the language change.":
                    "Por favor, reinicie la aplicación para aplicar el cambio de idioma.",
                
                # Mensajes de estado
                "Updating repositories...": "Actualizando repositorios...",
                "Upgrading packages...": "Actualizando paquetes...",
                "Updating Flatpak applications...": "Actualizando aplicaciones Flatpak...",
                "Cleaning package cache...": "Limpiando caché de paquetes...",
                "Removing unused packages...": "Eliminando paquetes sin usar...",
                "Checking system status...": "Verificando estado del sistema...",
                "Task completed successfully": "Tarea completada con éxito",
                "Task failed": "La tarea falló",
                "Operation cancelled": "Operación cancelada",
                "Operation Successful": "Operación Exitosa",
                "Operation Failed": "Operación Fallida",
                "Packages updated": "Paquetes actualizados",
                "Newly installed": "Nuevamente instalados",
                "To remove": "Para eliminar",
                "Flatpak apps updated": "Aplicaciones Flatpak actualizadas",
                "Packages removed": "Paquetes eliminados",
            }
        }

    def translate(self, text):
        """Translate text to current language"""
        try:
            return self.translations[self.current_lang].get(text, text)
        except KeyError:
            return text

    def set_language(self, lang):
        """Set current language if supported"""
        if lang in self.translations:
            self.current_lang = lang
            return True
        return False

# Create a singleton instance
translator = Translator()