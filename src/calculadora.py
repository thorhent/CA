from gi.repository import Gtk, Adw, GLib, Gdk
import gettext

_ = gettext.gettext

@Gtk.Template(resource_path="/io/github/thorhent/CA/calculadora.ui")
class CalculadoraWindow(Adw.ApplicationWindow):
    __gtype_name__ = "CalculadoraWindow"

    listaCalculadoras = Gtk.Template.Child("listaCalculadoras")
    stackCalculadoras = Gtk.Template.Child("stackCalculadoras")
    buscador = Gtk.Template.Child("buscador")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Importaciones locales (asegúrate de tener __init__.py en esa carpeta)
        from .calculadoras.imc import CalculadoraIMC
        from .calculadoras.pam import CalculadoraPAM
        from .calculadoras.tfg import CalculadoraCKDEPI
        from .calculadoras.gap import CalculadoraGap
        from .calculadoras.framingham import CalculadoraFramingham
        from .calculadoras.wells import CalculadoraWells
        from .calculadoras.curb65 import CalculadoraCurb65
        from .calculadoras.centor import CalculadoraCentor
        from .calculadoras.gold import CalculadoraGold
        from .calculadoras.chadsvasc import CalculadoraChadsvasc
        from .calculadoras.qsofa import CalculadoraQsofa
        from .calculadoras.light import CalculadoraLight


        icon_theme = Gtk.IconTheme.get_for_display(Gdk.Display.get_default())
        icon_theme.add_resource_path("/io/github/thorhent/CA/icons")

        # Configurar el filtro de la lista
        self.listaCalculadoras.set_filter_func(self._filtrar_calculadoras)

        # Conectar la señal de búsqueda para invalidar el filtro al escribir
        self.buscador.connect("search-changed", lambda entry: self.listaCalculadoras.invalidate_filter())

        # Cargamos los datos: (ID del Stack, Nombre visible, Instancia del Widget)
        self._cargar_calculadoras([
            ("imc", _("IMC"), _("Índice de Masa Corporal"), "scales-detail-symbolic", CalculadoraIMC()),
            ("pam", _("PAM"), _("Presión Arterial Media"), "heart-filled-symbolic", CalculadoraPAM()),
            ("tfg", _("TFG"), _("Tasa de Filtración Glomerular"), "funnel-outline-symbolic", CalculadoraCKDEPI() ),
            ("gap", _("GAP"), _("Anión GAP"), "shape-balance-symbolic", CalculadoraGap() ),
            ("framingham", _("Framingham"), _("Score de Framingham"), "emergency-number-symbolic", CalculadoraFramingham()  ),
            ("wells", _("Score de Wells"), _("Criterios de Wells simplificados"), "no-wheelchair-symbolic", CalculadoraWells() ),
            ("curb65", _("CURB-65"), _("Criterios para severidad en neumonía"), "compass-wind-symbolic", CalculadoraCurb65() ),
            ("centor", _("Escala de Centor"), _("Evaluar la probabilidad de faringitis estreptocócica"), "face-shutmouth-symbolic", CalculadoraCentor() ),
            ("gold", _("GOLD"), _("Clasificación GOLD para EPOC"), "person-talking-symbolic", CalculadoraGold() ),
            ("qsofa", _("qSOFA"), _("QuickSofa - evaluación de sepsis"), "sad-computer-symbolic", CalculadoraQsofa() ),
            ("chadsvasc", _("CHA2DS2-VASc"), _("Escala para riesgo de ACV"), "path-erase-split2-symbolic", CalculadoraChadsvasc() ),
            ("light", _("Criterios de Light"), _("Diferenciar entre trasudado y exudado"), "blur-alt-symbolic", CalculadoraLight() ),
        ])
        self.listaCalculadoras.connect("row-selected", self._al_seleccionar)

    def _cargar_calculadoras(self, calculadoras):
        # Limpiar el Stack correctamente
        #hijo = self.stackCalculadoras.get_first_child()

        for id_nombre, titulo, subtitulo, icono, widget in calculadoras:
            fila = Adw.ActionRow()
            fila.set_title(titulo)
            fila.set_subtitle(subtitulo)
            fila.set_name(id_nombre)
            fila.set_activatable(True)

            img = Gtk.Image.new_from_icon_name(icono)
            img.set_pixel_size(22)
            fila.add_prefix(img)
            fila.add_suffix(Gtk.Image.new_from_icon_name("go-next-symbolic"))

            widget.set_vexpand(True)
            widget.set_hexpand(True)

            self.listaCalculadoras.append(fila)
            self.stackCalculadoras.add_named(widget, id_nombre)


        #self.stackCalculadoras.set_visible_child_name("inicio")
        self.listaCalculadoras.unselect_all()

    def _al_seleccionar(self, lista, fila):
        if fila:
            # Obtenemos el ID guardado en set_name() y cambiamos el Stack
            id_stack = fila.get_name()
            self.stackCalculadoras.set_visible_child_name(id_stack)

    def _filtrar_calculadoras(self, fila):
        texto_busqueda = self.buscador.get_text().lower().strip()

        # Si no hay texto, mostrar todas las filas
        if not texto_busqueda:
            return True

        # Obtener el contenido de la fila para comparar
        titulo = fila.get_title().lower()
        subtitulo = fila.get_subtitle().lower()

        # Retorna True si el texto buscado está en el título o el subtítulo
        return texto_busqueda in titulo or texto_busqueda in subtitulo
