# centor.py
# Criterios de Centor para Faringitis Estreptocócica

from gi.repository import Gtk, Adw
import gettext

_ = gettext.gettext

class CalculadoraCentor(Gtk.Box):
    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL)

        # Contenedor con scroll para respetar la altura de la ventana
        self.scroll = Gtk.ScrolledWindow()
        self.scroll.set_vexpand(True)
        self.scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.append(self.scroll)

        clamp = Adw.Clamp(
            maximum_size=600,
            margin_top=12,
            margin_bottom=24,
            margin_start=12,
            margin_end=12
        )
        self.scroll.set_child(clamp)

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        clamp.set_child(box)

        # --- SECCIÓN DE CRITERIOS ---
        grupo_entrada = Adw.PreferencesGroup(
            title=_("Criterios de Centor"),
            description=_("Evaluación de probabilidad de faringitis bacteriana.")
        )
        box.append(grupo_entrada)

        # Definición de criterios (1 punto cada uno)
        # Escapamos el símbolo > como &gt; para evitar errores de Gtk-WARNING
        self.criterios = [
            ("exudado", _("Exudado o inflamación amigdalina"), None),
            ("adenopatia", _("Adenopatías cervicales anteriores dolorosas"), None),
            ("fiebre", _("Fiebre (temperatura &gt; 38°C)"), None),
            ("ausencia_tos", _("Ausencia de tos"), None),
            ("edad_joven", _("Edad 3-14 años"), _("Sumar 1 punto")),
            ("edad_adulto", _("Edad 15-44 años"), _("Sumar 0 puntos")),
            ("edad_anciano", _("Edad &gt; 45 años"), _("Restar 1 punto"))
        ]

        self.switches = {}
        for id_crit, titulo, subtitulo in self.criterios:
            fila = Adw.SwitchRow(title=titulo)
            if subtitulo:
                fila.set_subtitle(subtitulo)
            grupo_entrada.add(fila)
            self.switches[id_crit] = fila

        # --- SECCIÓN DE RESULTADO ---
        grupo_resultado = Adw.PreferencesGroup(title=_("Resultado y Conducta"))
        box.append(grupo_resultado)

        caja_res = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4, css_classes=["card"])
        caja_res.set_margin_top(12)

        self.label_puntos = Gtk.Label(label="0", css_classes=["title-1", "accent"])
        self.label_unidad = Gtk.Label(label=_("puntos"), css_classes=["caption", "dim-label"])

        caja_res.append(self.label_puntos)
        caja_res.append(self.label_unidad)
        grupo_resultado.add(caja_res)

        self.fila_interpretacion = Adw.ActionRow(
            title=_("Sugerencia terapéutica"),
            subtitle=_("Riesgo muy bajo (2-6%), no requiere estudio ni antibiótico")
        )
        grupo_resultado.add(self.fila_interpretacion)

        # Botón de cálculo estilo pill
        boton = Gtk.Button(
            label=_("Calcular Score"),
            margin_top=12,
            css_classes=["suggested-action", "pill"]
        )
        boton.set_margin_start(90)
        boton.set_margin_end(90)
        boton.connect("clicked", self.calcular)
        box.append(boton)

    def calcular(self, boton):
        total = 0

        # Criterios clásicos
        if self.switches["exudado"].get_active(): total += 1
        if self.switches["adenopatia"].get_active(): total += 1
        if self.switches["fiebre"].get_active(): total += 1
        if self.switches["ausencia_tos"].get_active(): total += 1

        # Modificadores por edad (Escala de McIsaac)
        if self.switches["edad_joven"].get_active(): total += 1
        # edad_adulto suma 0, no es necesario procesar
        if self.switches["edad_anciano"].get_active(): total -= 1

        self.label_puntos.set_label(str(total))

        # Interpretación y asignación de colores
        if total <= 1:
            nivel = _("Riesgo bajo: No requiere antibiótico ni cultivo")
            color = "success"
        elif total <= 3:
            nivel = _("Riesgo intermedio: Realizar test rápido o cultivo")
            color = "warning"
        else:
            nivel = _("Riesgo alto: Considerar tratamiento empírico")
            color = "error"

        self.fila_interpretacion.set_subtitle(nivel)

        # Actualización visual del color
        for c in ["success", "warning", "error"]:
            self.label_puntos.remove_css_class(c)
        self.label_puntos.add_css_class(color)
