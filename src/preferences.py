import gi
import sqlite3

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw, GObject
from .conectar import Connect  # Tu módulo de conexión


class Enfermedad(GObject.Object):
    nombre = GObject.Property(type=str)
    sindrome = GObject.Property(type=str)

    def __init__(self, nombre, sindrome):
        super().__init__()
        self.nombre = nombre
        self.sindrome = sindrome

class EnfermedadesPreferencesPage(Adw.PreferencesPage):
    __gtype_name__ = 'EnfermedadesPreferencesPage'

    def __init__(self):
        super().__init__()
        self.set_margin_end(12)

        # Grupo para la búsqueda
        search_group = Adw.PreferencesGroup()
        self.add(search_group)

        self.search = Gtk.SearchEntry()
        self.search.set_placeholder_text("Buscar enfermedad...")
        search_group.add(self.search)

        # Grupo para las enfermedades
        enfermedades_group = Adw.PreferencesGroup()
        self.add(enfermedades_group)

        self.listbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        enfermedades_group.add(self.listbox)

        self.enfermedades = self.cargar_enfermedades()
        cantidad = len(self.enfermedades)
        enfermedades_group.set_title(f"Enfermedades [{cantidad}]")
        self.filtrar_y_actualizar()

        self.search.connect("search-changed", lambda s: self.filtrar_y_actualizar())


    def cargar_enfermedades(self):
        conn = Connect()
        cursor = conn.conectar()
        cursor.execute("SELECT enfermedad, síndrome FROM enfermedades ORDER BY enfermedad ASC;")
        filas = cursor.fetchall()
        cursor.close()
        return [Enfermedad(nombre=row[0], sindrome=row[1]) for row in filas]

    def filtrar_y_actualizar(self):
        texto = self.search.get_text().lower()
        # Limpiar hijos de listbox
        child = self.listbox.get_first_child()
        while child:
            next_child = child.get_next_sibling()
            self.listbox.remove(child)
            child = next_child

        for enf in self.enfermedades:
            if texto in enf.nombre.lower() or texto in (enf.sindrome or "").lower():
                fila = Adw.ActionRow()
                fila.set_title(enf.nombre)
                fila.set_subtitle(enf.sindrome)
                fila.set_activatable(True)
                fila.connect("activated", self.on_fila_activated, enf)
                self.listbox.append(fila)

        self.listbox.show()

    def on_fila_activated(self, fila, enfermedad):
        dialog = Gtk.MessageDialog(
            transient_for=fila.get_toplevel(),
            modal=True,
            buttons=Gtk.ButtonsType.OK,
            message_type=Gtk.MessageType.INFO,
            text=enfermedad.nombre
        )
        dialog.format_secondary_text(enfermedad.sindrome or "Sin descripción")
        dialog.run()
        dialog.destroy()

class PreferencesWindow(Adw.PreferencesWindow):
    def __init__(self):
        super().__init__()
        self.set_search_enabled(False)
        page = EnfermedadesPreferencesPage()
        self.add(page)