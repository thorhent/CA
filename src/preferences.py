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
        self.search.set_placeholder_text("Buscar enfermedad, síndrome o síntoma ...")
        search_group.add(self.search)

        # Grupo para las enfermedades
        self.enfermedades_group = Adw.PreferencesGroup()
        self.add(self.enfermedades_group)

        self.listbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.enfermedades_group.add(self.listbox)

        self.enfermedades = self.cargar_enfermedades()
        self.filtrar_y_actualizar()

        self.search.connect("search-changed", lambda s: self.filtrar_y_actualizar())



    def cargar_enfermedades(self):
        conn = Connect()
        cursor = conn.conectar()
        # Join the diseases and clinica tables to get all symptoms at once
        cursor.execute("SELECT enfermedades.enfermedad, enfermedades.síndrome, clinica.sintoma_signo FROM enfermedades LEFT JOIN clinica USING(cod_enfermedad) ORDER BY enfermedades.enfermedad ASC;")
        filas = cursor.fetchall()
        cursor.close()

        # Group symptoms by disease
        enfermedades_dict = {}
        for row in filas:
            nombre_enf = row[0]
            sindrome = row[1]
            sintoma = row[2]
            if nombre_enf not in enfermedades_dict:
                enfermedades_dict[nombre_enf] = {
                    "sindrome": sindrome,
                    "sintomas": []
                }
            if sintoma:
                enfermedades_dict[nombre_enf]["sintomas"].append(sintoma)

        # Convert the dictionary back to a list of Enfermedad objects
        enfermedades = []
        for nombre, datos in enfermedades_dict.items():
            enfermedad = Enfermedad(nombre=nombre, sindrome=datos["sindrome"])
            # Add a new attribute to hold the symptoms
            enfermedad.sintomas = datos["sintomas"]
            enfermedades.append(enfermedad)

        return enfermedades


    def filtrar_y_actualizar(self):
        texto = self.search.get_text().lower()
        # Limpiar hijos de listbox
        child = self.listbox.get_first_child()
        while child:
            next_child = child.get_next_sibling()
            self.listbox.remove(child)
            child = next_child

        cantidad_enfermedades = 0
        for enf in self.enfermedades:
            search_string = f"{enf.nombre.lower()} {enf.sindrome.lower()} {' '.join(enf.sintomas).lower()}"
            if texto in search_string:
                cantidad_enfermedades += 1
                # Crear el AdwExpanderRow
                expander_row = Adw.ExpanderRow()
                expander_row.set_title(enf.nombre)
                expander_row.set_subtitle(enf.sindrome)
                expander_row.set_margin_top(5)
                expander_row.set_margin_start(10)
                expander_row.set_margin_end(10)
                expander_row.set_margin_bottom(5)
                expander_row.add_css_class("card")

                for sintoma in enf.sintomas:
                    sintoma_row = Gtk.Label() #Adw.ActionRow()
                    sintoma_row.set_label(sintoma)
                    #sintoma_row.set_margin_start(10)
                    #sintoma_row.set_margin_end(10)
                    expander_row.add_row(sintoma_row)

                self.listbox.append(expander_row)

        self.listbox.show()
        self.enfermedades_group.set_title(f"Enfermedades [{cantidad_enfermedades}]")


    def on_fila_activated(self, fila, enfermedad):
        dialog = Gtk.MessageDialog(
            transient_for=fila.get_toplevel(),
            modal=True,
            buttons=Gtk.ButtonsType.OK,
            message_type=Gtk.MessageType.INFO,
            text=enfermedad.nombre
        )
        dialog.format_secondary_text(enfermedad.sindrome or "Sin descripción")

        # Conectar la señal 'response' para destruir el diálogo
        dialog.connect("response", lambda d, r: d.destroy())

        # Mostrar el diálogo sin bloquear el bucle principal de GTK
        dialog.present()

class PreferencesWindow(Adw.PreferencesWindow):
    def __init__(self):
        super().__init__()
        self.set_search_enabled(False)
        page = EnfermedadesPreferencesPage()
        self.add(page)
