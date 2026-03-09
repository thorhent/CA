import gi
import gettext

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw, GObject
from .conectar import Connect

_ = gettext.gettext

class Enfermedad(GObject.Object):
    nombre = GObject.Property(type=str)
    sindrome = GObject.Property(type=str)

    def __init__(self, nombre, sindrome, sintomas):
        super().__init__()
        self.set_property("nombre", nombre)
        self.set_property("sindrome", sindrome)
        self.sintomas = sintomas

class EnfermedadesPreferencesPage(Adw.PreferencesPage):
    def __init__(self):
        super().__init__()
        self.set_title(_("Diccionario Clínico"))
        self.set_icon_name("library-medical-symbolic")

        # --- GRUPO DE BÚSQUEDA ---
        self.search_group = Adw.PreferencesGroup()
        self.add(self.search_group)

        self.search_entry = Gtk.SearchEntry()
        self.search_entry.set_placeholder_text(_("Buscar enfermedad, síntoma..."))
        self.search_entry.set_margin_bottom(12)
        self.search_group.add(self.search_entry)

        # --- CONTENEDOR DE RESULTADOS ---
        self.list_group = Adw.PreferencesGroup()
        self.add(self.list_group)

        self.stack = Gtk.Stack()
        self.stack.set_transition_type(Gtk.StackTransitionType.CROSSFADE)
        self.list_group.add(self.stack)

        # Estado vacío
        self.status_page = Adw.StatusPage()
        self.status_page.set_title(_("No se encontraron resultados"))
        self.status_page.set_icon_name("system-search-symbolic")
        self.stack.add_named(self.status_page, "empty")

        # Listado de enfermedades
        self.list_box = Gtk.ListBox()
        self.list_box.set_selection_mode(Gtk.SelectionMode.NONE)
        self.list_box.add_css_class("boxed-list")
        self.stack.add_named(self.list_box, "list")

        # Configuración del filtro
        self.list_box.set_filter_func(self.filter_func)

        self.cargar_enfermedades()

        # Conexión de búsqueda
        self.search_entry.connect("search-changed", self.on_search_changed)

    def filter_func(self, row):
        query = self.search_entry.get_text().lower()
        if not query:
            return True

        # Combinamos título, subtítulo y caché de síntomas para la búsqueda
        contenido = f"{row.get_title()} {row.get_subtitle()} {row.search_cache}".lower()
        return query in contenido

    def on_search_changed(self, entry):
        self.list_box.invalidate_filter()

        cantidad_visible = 0
        texto_busqueda = entry.get_text().strip()

        child = self.list_box.get_first_child()
        while child:
            if child.get_child_visible():
                cantidad_visible += 1
            child = child.get_next_sibling()

        # Lógica del título dinámico
        if texto_busqueda:
            # Si hay búsqueda, mostramos "X de Y"
            nuevo_titulo = _(f"Enfermedades: {cantidad_visible} de {self.total_registros}")
        else:
            # Si está vacío, solo el total
            nuevo_titulo = _(f"Enfermedades: {self.total_registros}")

        self.list_group.set_title(nuevo_titulo)
        self.stack.set_visible_child_name("list" if cantidad_visible > 0 else "empty")


    def cargar_enfermedades(self):
        try:
            conn = Connect()
            cursor = conn.conectar()
            query = """
                SELECT e.enfermedad, e.síndrome, c.sintoma_signo
                FROM enfermedades e
                LEFT JOIN clinica c ON e.cod_enfermedad = c.cod_enfermedad
                ORDER BY e.enfermedad ASC;
            """
            cursor.execute(query)
            filas = cursor.fetchall()
            cursor.close()

            temp_dict = {}
            for row in filas:
                if row[0] not in temp_dict:
                    temp_dict[row[0]] = {"sindrome": row[1], "sintomas": []}
                if row[2]: temp_dict[row[0]]["sintomas"].append(row[2])

            # Guardamos el total general en una variable de clase
            self.total_registros = len(temp_dict)

            for nombre, datos in temp_dict.items():
                row = Adw.ExpanderRow()
                row.set_title(nombre)
                row.set_subtitle(datos["sindrome"] or "")
                row.search_cache = " ".join(datos["sintomas"])

                for s in datos["sintomas"]:
                    sintoma_row = Adw.ActionRow()
                    sintoma_row.set_title(s)
                    row.add_row(sintoma_row)

                self.list_box.append(row)

            # Inicializamos el título con el total
            self.list_group.set_title(_(f"Enfermedades: {self.total_registros}"))
            self.stack.set_visible_child_name("list")
        except Exception as e:
            print(f"Error en carga: {e}")


class PreferencesWindow(Adw.PreferencesWindow):
    def __init__(self):
        super().__init__()
        # Desactivamos el search nativo de la ventana porque usaremos el nuestro interno
        # Esto evita la confusión de tener dos barras de búsqueda
        self.set_title(_("Enfermedades"))
        self.set_search_enabled(False)
        self.set_default_size(600, 660)
        self.add(EnfermedadesPreferencesPage())
